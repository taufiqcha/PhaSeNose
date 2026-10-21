from sklearn.metrics import balanced_accuracy_score, r2_score
from sklearn.model_selection import LeaveOneGroupOut

from data import (SENSOR, fitur_fase, label_dipanaskan, muat_enose, muat_gcms, siapkan_panel, simpan_json,
                  titik_total_gcms)
from model import bs, fitur_per_lipatan, pls, prediksi_dari_lipatan, prediksi_loo, uji_kelas, uji_permutasi_label


def rocket_segar_panas(panel):
    penuh = panel["penuh"]
    y = label_dipanaskan(penuh.jam)
    lipatan = fitur_per_lipatan(panel["respons"], y, LeaveOneGroupOut(), penuh.sesi.values)
    return uji_permutasi_label(lambda acak: balanced_accuracy_score(acak, prediksi_dari_lipatan(lipatan, acak)), y)


def slope_segar_panas(meta, fitur):
    y, sesi = label_dipanaskan(meta.jam), meta.sesi.values
    return uji_permutasi_label(lambda acak: bs(uji_kelas(fitur["slope"], acak, LeaveOneGroupOut(), sesi)), y)


def pls_total_area(meta, fitur, gcms):
    titik = titik_total_gcms(meta, fitur["dR"], gcms)
    X = titik[SENSOR].values
    return uji_permutasi_label(lambda acak: r2_score(acak, prediksi_loo(pls, X, acak)), titik.gc_total.values)


def main():
    meta, sinyal = muat_enose()
    fitur = fitur_fase(sinyal)
    simpan_json("uji_signifikansi.json", dict(
        skema="label diacak di seluruh berkas atau titik, pembagi lipatan (sesi atau LOO) tetap",
        E3_minirocket_tinggalkan_sesi=rocket_segar_panas(siapkan_panel(meta, sinyal)),
        E8_lda_slope_tinggalkan_sesi=slope_segar_panas(meta, fitur),
        E5_pls_semua_sensor_R2_LOO=pls_total_area(meta, fitur, muat_gcms())))


if __name__ == "__main__":
    main()
