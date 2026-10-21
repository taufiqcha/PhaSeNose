import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.linear_model import RidgeClassifierCV
from sklearn.metrics import accuracy_score, balanced_accuracy_score, r2_score
from sklearn.model_selection import LeaveOneGroupOut, LeaveOneOut, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sktime.transformations.panel.rocket import MiniRocketMultivariate

from data import SEED, label_dipanaskan

LIPAT = 5
ALFA_ROCKET = np.logspace(-3, 3, 10)
JUMLAH_PERMUTASI = 200
LIPAT_DALAM = 3
TOL_SELEKSI = 1e-3
KOMPONEN_PLS = 2


def lda():
    return make_pipeline(StandardScaler(), LinearDiscriminantAnalysis())


def pls():
    return make_pipeline(StandardScaler(), PLSRegression(KOMPONEN_PLS))


def lipat_kelas():
    return StratifiedKFold(LIPAT, shuffle=True, random_state=SEED)


def skor_kelas(y, prediksi):
    return dict(akurasi=accuracy_score(y, prediksi), akurasi_seimbang=balanced_accuracy_score(y, prediksi))


def skor_per_kelompok(y, prediksi, kelompok):
    return {g: float(np.mean(prediksi[kelompok == g] == y[kelompok == g])) for g in sorted(set(kelompok))}


def prediksi_kelas(X, y, cv=None, kelompok=None, model=lda):
    return cross_val_predict(model(), X, y, cv=cv if cv is not None else lipat_kelas(), groups=kelompok)


def uji_kelas(X, y, cv=None, kelompok=None, model=lda):
    return skor_kelas(y, prediksi_kelas(X, y, cv, kelompok, model))


def uji_kelas_per_kelompok(X, y, cv, kelompok, model=lda):
    prediksi = prediksi_kelas(X, y, cv, kelompok, model)
    return dict(skor_kelas(y, prediksi), per_kelompok=skor_per_kelompok(y, prediksi, kelompok))


def uji_permutasi_label(hitung, y):
    acak = np.random.default_rng(SEED)
    asli = hitung(y)
    acakan = np.array([hitung(acak.permutation(y)) for _ in range(JUMLAH_PERMUTASI)])
    return dict(statistik=asli, p=(np.sum(acakan >= asli) + 1) / (JUMLAH_PERMUTASI + 1),
                jumlah_permutasi=JUMLAH_PERMUTASI)


def fitur_rocket(panel_latih, *panel_lain):
    ubah = MiniRocketMultivariate(random_state=SEED).fit(panel_latih)
    return [ubah.transform(p) for p in (panel_latih, *panel_lain)]


def fitur_per_lipatan(panel, y, cv, kelompok=None):
    return [(latih, uji, *fitur_rocket(panel[latih], panel[uji])) for latih, uji in cv.split(panel, y, kelompok)]


def prediksi_dari_lipatan(lipatan, y):
    prediksi = np.empty(len(y), dtype=y.dtype)
    for latih, uji, f_latih, f_uji in lipatan:
        klasifier = make_pipeline(StandardScaler(), RidgeClassifierCV(alphas=ALFA_ROCKET)).fit(f_latih, y[latih])
        prediksi[uji] = klasifier.predict(f_uji)
    return prediksi


def uji_rocket(panel, y, cv, kelompok=None):
    prediksi = prediksi_dari_lipatan(fitur_per_lipatan(panel, y, cv, kelompok), y)
    hasil = skor_kelas(y, prediksi)
    if kelompok is not None:
        hasil["per_kelompok"] = skor_per_kelompok(y, prediksi, kelompok)
    return hasil


def ambang_terbaik(x, y):
    return max(np.unique(x), key=lambda a: balanced_accuracy_score(y, (x > a).astype(int)))


def prediksi_ambang(x, y, cv=None, kelompok=None):
    prediksi = np.empty(len(y), dtype=int)
    for latih, uji in (cv if cv is not None else LeaveOneOut()).split(x, y, kelompok):
        prediksi[uji] = (x[uji] > ambang_terbaik(x[latih], y[latih])).astype(int)
    return prediksi


class KoreksiKomponen(BaseEstimator, TransformerMixin):
    def __init__(self, jumlah_sensor):
        self.jumlah_sensor = jumlah_sensor

    def fit(self, X, y=None):
        baseline, respons = X[:, :self.jumlah_sensor], X[:, self.jumlah_sensor:]
        self.skala_baseline_ = StandardScaler().fit(baseline)
        self.arah_ = PCA(1).fit(self.skala_baseline_.transform(baseline)).components_[0]
        self.skala_respons_ = StandardScaler().fit(respons)
        return self

    def transform(self, X):
        z = self.skala_respons_.transform(X[:, self.jumlah_sensor:])
        return z - np.outer(z @ self.arah_, self.arah_)


def lda_koreksi_komponen(jumlah_sensor):
    return lambda: make_pipeline(KoreksiKomponen(jumlah_sensor), StandardScaler(), LinearDiscriminantAnalysis())


def lda_seleksi():
    pemilih = SequentialFeatureSelector(LinearDiscriminantAnalysis(), n_features_to_select="auto", tol=TOL_SELEKSI,
                                        scoring="balanced_accuracy",
                                        cv=StratifiedKFold(LIPAT_DALAM, shuffle=True, random_state=SEED))
    return make_pipeline(StandardScaler(), pemilih, LinearDiscriminantAnalysis())


def r2_semua_dan_dipanaskan(y, prediksi, dipanaskan):
    return dict(semua=r2_score(y, prediksi), dipanaskan=r2_score(y[dipanaskan], prediksi[dipanaskan]))


def prediksi_loo(model, X, y):
    return np.ravel(cross_val_predict(model(), X, y, cv=LeaveOneOut()))


def r2_loo_titik(model, X, y, dipanaskan):
    return r2_semua_dan_dipanaskan(y, prediksi_loo(model, X, y), dipanaskan)


def bs(skor):
    return skor["akurasi_seimbang"]


def segar_lda_sesi(meta, fitur):
    y, sesi = label_dipanaskan(meta.jam), meta.sesi.values
    return dict(dR=uji_kelas(fitur["dR"], y, LeaveOneGroupOut(), sesi),
                baseline=uji_kelas(fitur["baseline"], y, LeaveOneGroupOut(), sesi))


def segar_rocket_sesi(panel, definisi="sesi"):
    penuh = panel["penuh"]
    y, sesi = label_dipanaskan(penuh.jam), penuh[definisi].values
    return dict(respons=uji_rocket(panel["respons"], y, LeaveOneGroupOut(), sesi),
                kontrol=uji_rocket(panel["pra"], y, LeaveOneGroupOut(), sesi))
