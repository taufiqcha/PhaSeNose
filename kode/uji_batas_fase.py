import numpy as np
import pandas as pd

from data import BARIS_BASELINE, BARIS_SAMPLING, SENSOR, SENSOR_DILAPORKAN, muat_enose, panel_respons, simpan_json

JENDELA_HALUS = 5
CARI_NAIK = slice(20, 61)
CARI_TURUN = slice(130, 201)
AMBANG_AMPLITUDO_MV = 60
KUARTIL = [25, 50, 75]
METODE = {"halus": JENDELA_HALUS, "mentah": 1}
KONSTANTA = {"awal_sampling": BARIS_SAMPLING.start, "awal_purging": BARIS_SAMPLING.stop}


def jumlah_sensor(x):
    return x[:, list(SENSOR_DILAPORKAN.values())].sum(1)


def halus(nilai, jendela):
    return pd.Series(nilai).rolling(jendela, center=True, min_periods=1).mean().values


def awal_fase(kurva, cari, arah):
    beda = np.diff(kurva[cari.start - 1:cari.stop])
    return int(cari.start + (np.argmax(beda) if arah > 0 else np.argmin(beda)))


def batas(kurva, panjang):
    return dict(awal_sampling=awal_fase(kurva, CARI_NAIK, 1),
                awal_purging=awal_fase(kurva, CARI_TURUN, -1) if panjang >= CARI_TURUN.stop else None)


def amplitudo(x):
    return halus(jumlah_sensor(x), JENDELA_HALUS)[CARI_NAIK].max() - jumlah_sensor(x)[BARIS_BASELINE].mean()


def satu_berkas(x):
    return dict(amplitudo_mV=amplitudo(x),
                **{m: batas(halus(jumlah_sensor(x), j), len(x)) for m, j in METODE.items()})


def ringkas(nilai, konstanta):
    nilai = np.array([v for v in nilai if v is not None])
    kuartil = np.percentile(nilai, KUARTIL)
    frekuensi = pd.Series(nilai).value_counts()
    modus = int(frekuensi[frekuensi == frekuensi.max()].index.min())
    return dict(berkas=int(len(nilai)), kuartil={str(k): float(v) for k, v in zip(KUARTIL, kuartil)}, modus=modus,
                minimum=int(nilai.min()), maksimum=int(nilai.max()),
                frekuensi={str(int(k)): int(v) for k, v in frekuensi.sort_index().items()},
                konstanta_data_py=konstanta, konstanta_sama_dengan_median=bool(kuartil[1] == konstanta),
                konstanta_sama_dengan_modus=modus == konstanta,
                konstanta_di_dalam_kuartil=bool(kuartil[0] <= konstanta <= kuartil[2]))


def kurva_median(meta, sinyal, jendela):
    respons = panel_respons(sinyal, meta)[:, list(SENSOR_DILAPORKAN.values())].sum(1)
    hasil = batas(halus(np.median(respons, axis=0), jendela), respons.shape[1])
    return dict(berkas=len(respons), **hasil,
                **{f"konstanta_{k}_sama": hasil[k] == v for k, v in KONSTANTA.items()})


def ringkasan_metode(kuat, metode):
    return {fase: ringkas([h[metode][fase] for h in kuat.values()], konstanta) for fase, konstanta in KONSTANTA.items()}


def main():
    meta, sinyal = muat_enose()
    hasil = {b: satu_berkas(x) for b, x in zip(meta.berkas, sinyal)}
    kuat = {b: h for b, h in hasil.items() if h["amplitudo_mV"] > AMBANG_AMPLITUDO_MV}
    simpan_json("uji_batas_fase.json", dict(
        metode=dict(sensor=[SENSOR[i] for i in SENSOR_DILAPORKAN.values()], jendela_halus=JENDELA_HALUS,
                    baris_baseline=[BARIS_BASELINE.start, BARIS_BASELINE.stop - 1],
                    cari_naik=[CARI_NAIK.start, CARI_NAIK.stop - 1], cari_turun=[CARI_TURUN.start, CARI_TURUN.stop - 1],
                    ambang_amplitudo_mV=AMBANG_AMPLITUDO_MV,
                    definisi="awal fase = baris t setelah beda v[t] - v[t-1] terbesar (naik) atau terkecil (turun)"),
        berkas_total=len(hasil), berkas_kuat=len(kuat),
        berkas_gugur=[dict(berkas=b, minyak=m, jam=int(j)) for b, m, j in zip(meta.berkas, meta.minyak, meta.jam)
                      if b not in kuat],
        ringkasan={m: ringkasan_metode(kuat, m) for m in METODE},
        kurva_median={m: kurva_median(meta, sinyal, j) for m, j in METODE.items()}, per_berkas=hasil))


if __name__ == "__main__":
    main()
