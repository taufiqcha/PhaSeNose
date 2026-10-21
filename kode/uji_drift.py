import numpy as np
from sklearn.decomposition import PCA
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

from data import (JEDA_SESI_JAM, SENSOR, fitur_fase, jam_per_sesi, jumlah_kelas_panas, label_dipanaskan, muat_enose,
                  siapkan_panel, simpan_json)
from model import lda_koreksi_komponen, lipat_kelas, segar_rocket_sesi, uji_kelas, uji_kelas_per_kelompok, uji_rocket

DEFINISI_SESI = ["sesi", "sesi_jeda"]


def koreksi_komponen(meta, fitur, y):
    X = np.c_[fitur["baseline"], fitur["dR"]]
    model = lda_koreksi_komponen(len(SENSOR))
    pca = PCA(1).fit(StandardScaler().fit_transform(fitur["baseline"]))
    return dict(varian_pc1_baseline=pca.explained_variance_ratio_[0], segar_vs_panas=uji_kelas(X, y, model=model),
                segar_vs_panas_tinggalkan_sesi=uji_kelas(X, y, LeaveOneGroupOut(), meta.sesi.values, model))


def minirocket(meta, sinyal):
    panel = siapkan_panel(meta, sinyal)
    penuh = panel["penuh"]
    hasil = dict(kelas_panas=jumlah_kelas_panas(penuh),
                 respons_5fold=uji_rocket(panel["respons"], label_dipanaskan(penuh.jam), lipat_kelas()))
    for d in DEFINISI_SESI:
        lintas = segar_rocket_sesi(panel, d)
        hasil[f"respons_tinggalkan_{d}"] = lintas["respons"]
        hasil[f"kontrol_pra_sampling_tinggalkan_{d}"] = lintas["kontrol"]
    return hasil


def urutan_sesi(meta):
    awal = meta.groupby("sesi").waktu.min().sort_values()
    jam = jam_per_sesi(meta)
    return [dict(sesi=s, minyak=s.split("_")[0], mulai=str(w), jam=jam[s]) for s, w in awal.items()]


def jumlah_berkas(meta, definisi):
    return {f"{s} jam {j}": int(n) for (s, j), n in meta.groupby([definisi, "jam"]).size().items()}


def main():
    meta, sinyal = muat_enose()
    fitur, y = fitur_fase(sinyal), label_dipanaskan(meta.jam)
    simpan_json("uji_drift.json", dict(
        sesi={d: jam_per_sesi(meta, d) for d in DEFINISI_SESI},
        jumlah_berkas={d: jumlah_berkas(meta, d) for d in DEFINISI_SESI},
        jeda_sesi_jam=JEDA_SESI_JAM, urutan_sesi=urutan_sesi(meta),
        koreksi_komponen_5fold=koreksi_komponen(meta, fitur, y),
        lda_dR_tinggalkan_sesi=uji_kelas_per_kelompok(fitur["dR"], y, LeaveOneGroupOut(), meta.sesi.values),
        minirocket=minirocket(meta, sinyal)))


if __name__ == "__main__":
    main()
