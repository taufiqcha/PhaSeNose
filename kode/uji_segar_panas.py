from sklearn.model_selection import LeaveOneGroupOut

from data import KOLOM_S1, fitur_fase, label_dipanaskan, muat_enose, simpan_json
from model import ambang_terbaik, prediksi_ambang, segar_lda_sesi, skor_kelas, skor_per_kelompok, uji_kelas


def aturan_s1_sesi(s1, y, sesi):
    prediksi = prediksi_ambang(s1, y, LeaveOneGroupOut(), sesi)
    return dict(skor_kelas(y, prediksi), per_kelompok=skor_per_kelompok(y, prediksi, sesi))


def main():
    meta, sinyal = muat_enose()
    fitur, y = fitur_fase(sinyal), label_dipanaskan(meta.jam)
    s1, sesi = fitur["dR"][:, KOLOM_S1], meta.sesi.values
    lintas_sesi = segar_lda_sesi(meta, fitur)
    simpan_json("uji_segar_panas.json", dict(
        jumlah_segar=int((y == 0).sum()), jumlah_dipanaskan=int((y == 1).sum()),
        lda_5fold_dR=uji_kelas(fitur["dR"], y),
        lda_tinggalkan_sesi_dR=lintas_sesi["dR"], lda_tinggalkan_sesi_baseline=lintas_sesi["baseline"],
        aturan_S1_LOO=skor_kelas(y, prediksi_ambang(s1, y)), aturan_S1_tinggalkan_sesi=aturan_s1_sesi(s1, y, sesi),
        ambang_S1_mV_seluruh_data=ambang_terbaik(s1, y)))


if __name__ == "__main__":
    main()
