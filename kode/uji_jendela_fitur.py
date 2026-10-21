from sklearn.model_selection import LeaveOneGroupOut

from data import (BARIS_BASELINE, BARIS_SAMPLING, BARIS_SELURUH, BARIS_STEADY, baris_lengkap, jumlah_kelas_panas,
                  label_dipanaskan, muat_enose, puncak_jendela, rerata_jendela, simpan_json)
from model import lda, lda_seleksi, uji_kelas

MODEL_KELAS = {"tanpa_seleksi": lda, "seleksi_sfs": lda_seleksi}


def varian_fitur(sinyal):
    base = rerata_jendela(sinyal, BARIS_BASELINE)
    steady, proses = rerata_jendela(sinyal, BARIS_STEADY), rerata_jendela(sinyal, BARIS_SAMPLING)
    return {"B0_baseline_saja": base, "F1_rerata_seluruh": rerata_jendela(sinyal, BARIS_SELURUH),
            "F2_steady_mentah": steady, "F3_proses_mentah": proses, "F4_steady_minus_baseline": steady - base,
            "F5_proses_minus_baseline": proses - base, "F6_steady_relatif": (steady - base) / base,
            "F7_puncak_minus_baseline": puncak_jendela(sinyal, BARIS_SAMPLING) - base}


def validasi(meta):
    return {"segar_panas_5fold": (None, None), "segar_panas_tinggalkan_sesi": (LeaveOneGroupOut(), meta.sesi.values)}


def uji_varian(X, y, meta):
    return {tugas: {nama: uji_kelas(X, y, cv, sesi, model) for nama, model in MODEL_KELAS.items()}
            for tugas, (cv, sesi) in validasi(meta).items()}


def main():
    meta, sinyal = muat_enose()
    varian = varian_fitur(sinyal)
    pakai = baris_lengkap(*varian.values())
    dikeluarkan = meta.berkas[~pakai].tolist()
    meta = meta[pakai].reset_index(drop=True)
    y = label_dipanaskan(meta.jam)
    simpan_json("uji_jendela_fitur.json", dict(
        berkas=int(pakai.sum()), kelas_panas=jumlah_kelas_panas(meta), berkas_dikeluarkan=dikeluarkan,
        hasil={nama: uji_varian(X[pakai], y, meta) for nama, X in varian.items()}))


if __name__ == "__main__":
    main()
