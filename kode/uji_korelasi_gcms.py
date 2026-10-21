from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression

from data import SENSOR, fitur_fase, muat_enose, muat_gcms, simpan_json, titik_gcms_dipanaskan, titik_total_gcms
from model import pls, prediksi_loo, r2_loo_titik


def korelasi(titik):
    hasil = {}
    for s in SENSOR:
        spearman, pearson = spearmanr(titik[s], titik.gc_total), pearsonr(titik[s], titik.gc_total)
        hasil[s] = dict(spearman=spearman[0], spearman_p=spearman[1], pearson=pearson[0], pearson_p=pearson[1])
    return hasil


def r2_loo_per_sensor(titik):
    return {s: r2_loo_titik(LinearRegression, titik[[s]].values, titik.gc_total.values, titik_gcms_dipanaskan(titik))
            for s in SENSOR}


def r2_loo_pls(titik):
    return r2_loo_titik(pls, titik[SENSOR].values, titik.gc_total.values, titik_gcms_dipanaskan(titik))


def prediksi_per_titik(titik, sensor_terbaik):
    pls_8 = prediksi_loo(pls, titik[SENSOR].values, titik.gc_total.values)
    linier = prediksi_loo(LinearRegression, titik[[sensor_terbaik]].values, titik.gc_total.values)
    return {f"{m} {j}": dict(gc_total=titik.gc_total[(m, j)], prediksi_pls_semua_sensor=a,
                             prediksi_linier_sensor_terbaik=b, dR_sensor_terbaik=titik[sensor_terbaik][(m, j)])
            for (m, j), a, b in zip(titik.index, pls_8, linier)}


def prediksi_kontrol_per_titik(kontrol, sensor_terbaik):
    pls_8 = prediksi_loo(pls, kontrol[SENSOR].values, kontrol.gc_total.values)
    linier = prediksi_loo(LinearRegression, kontrol[[sensor_terbaik]].values, kontrol.gc_total.values)
    return {f"{m} {j}": dict(prediksi_pls_semua_sensor=a, prediksi_linier_sensor_terbaik=b,
                             baseline_sensor_terbaik=kontrol[sensor_terbaik][(m, j)])
            for (m, j), a, b in zip(kontrol.index, pls_8, linier)}


def main():
    meta, sinyal = muat_enose()
    fitur, gcms = fitur_fase(sinyal), muat_gcms()
    titik, kontrol = titik_total_gcms(meta, fitur["dR"], gcms), titik_total_gcms(meta, fitur["baseline"], gcms)
    sepuluh = korelasi(titik)
    terbaik = max(sepuluh, key=lambda s: sepuluh[s]["spearman"])
    simpan_json("uji_korelasi_gcms.json", dict(
        jumlah_titik=int(len(titik)), jumlah_titik_dipanaskan=int(titik_gcms_dipanaskan(titik).sum()),
        sensor_spearman_tertinggi=terbaik, sepuluh_titik=sepuluh,
        R2_LOO_linier_total_area=r2_loo_per_sensor(titik),
        kontrol_baseline_R2_LOO_linier_total_area=r2_loo_per_sensor(kontrol),
        R2_LOO_pls_semua_sensor=r2_loo_pls(titik), kontrol_baseline_R2_LOO_pls_semua_sensor=r2_loo_pls(kontrol),
        prediksi_loo_per_titik=prediksi_per_titik(titik, terbaik),
        kontrol_baseline_prediksi_loo_per_titik=prediksi_kontrol_per_titik(kontrol, terbaik)))


if __name__ == "__main__":
    main()
