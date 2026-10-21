import numpy as np

from data import (BARIS_MEDIAN_S1, BARIS_SAMPLING, BARIS_STEADY, SENSOR, jendela_teks, muat_enose, panel_respons,
                  simpan_json)

AMBANG_PERUBAHAN = 0.05
BARIS_UJUNG = 10
JENDELA_PEMBANDING = {"ICITEE_50_140": slice(50, 141), "plateau_lama_40_149": slice(40, 150)}


def kurva_median(sinyal, meta):
    return np.median(panel_respons(sinyal, meta), axis=0).T


def perubahan_relatif(kurva, amplitudo, jendela):
    isi = kurva[jendela]
    return np.abs(isi[-BARIS_UJUNG:].mean(0) - isi[:BARIS_UJUNG].mean(0)) / amplitudo


def jendela_terbaik(kurva, amplitudo, panjang, akhir):
    awal = range(BARIS_SAMPLING.start, akhir - panjang + 1)
    return min((slice(a, a + panjang) for a in awal), key=lambda j: perubahan_relatif(kurva, amplitudo, j).max())


def cari_steady(kurva, amplitudo, akhir):
    terpanjang = None
    for panjang in range(2 * BARIS_UJUNG, akhir - BARIS_SAMPLING.start + 1):
        jendela = jendela_terbaik(kurva, amplitudo, panjang, akhir)
        if perubahan_relatif(kurva, amplitudo, jendela).max() <= AMBANG_PERUBAHAN:
            terpanjang = jendela
    return terpanjang


def ringkas(kurva, amplitudo, jendela):
    ubah = perubahan_relatif(kurva, amplitudo, jendela)
    return dict(baris=jendela_teks(jendela), perubahan_relatif_per_sensor=dict(zip(SENSOR, ubah)),
                perubahan_relatif_maks=ubah.max(),
                sensor_berubah_lebih_dari_ambang=int((ubah > AMBANG_PERUBAHAN).sum()))


def main():
    meta, sinyal = muat_enose()
    kurva = kurva_median(sinyal, meta)
    amplitudo = np.abs(kurva[BARIS_SAMPLING]).max(0)
    akhir = int(min(meta.baris.min(), BARIS_SAMPLING.stop))
    steady = cari_steady(kurva, amplitudo, akhir)
    simpan_json("uji_jendela_steady.json", dict(
        ambang_perubahan=AMBANG_PERUBAHAN, baris_ujung=BARIS_UJUNG, batas_akhir_semua_berkas=akhir - 1,
        steady=ringkas(kurva, amplitudo, steady), panjang_steady=steady.stop - steady.start,
        sesuai_data_py=bool(steady == BARIS_STEADY),
        pembanding={k: ringkas(kurva, amplitudo, v) for k, v in JENDELA_PEMBANDING.items()},
        median_S1_baris={str(b): kurva[b, 0] for b in BARIS_MEDIAN_S1}))


if __name__ == "__main__":
    main()
