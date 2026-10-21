import datetime as dt
from decimal import ROUND_HALF_UP, Decimal
import io
import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf
from scipy.ndimage import median_filter

AKAR = Path(__file__).resolve().parent.parent
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else AKAR / "data"
HASIL = AKAR / "results"
ZIP_ENOSE = DATA / "01_raw_enose.zip"
ZIP_GCMS = DATA / "02_raw_gcms.zip"
PDF_GCMS = "raw_gcms/cookingoilITS.pdf"
SEED = 42
SENSOR = [f"S{i}" for i in range(1, 9)]
KOLOM_S1 = 0
SENSOR_DILAPORKAN = {"S1": KOLOM_S1, "S8": 7}
MINYAK = ["SA", "SIP"]
MAHAL, MURAH = MINYAK
BARIS_PRA_SAMPLING = slice(0, 33)
BARIS_BASELINE = slice(5, 29)
BARIS_NAIK = slice(33, 45)
BARIS_SAMPLING = slice(33, 159)
BARIS_STEADY = slice(107, 148)
BARIS_SELURUH = slice(0, 240)
TITIK_UJUNG_NAIK = 3
PANJANG_PENUH = 240
JEDA_SESI_JAM = 3
POLA_BERKAS = re.compile(r"(SA|SIP)_(\d+)-(\d)_?\.xlsx$")
POLA_SAMPEL_GCMS = re.compile(r"(SA|SIP) ?(\d+)")
POLA_RT = re.compile(r"\d+\.\d+")
POLA_CAS = re.compile(r"\d{2,7}-\d{2}-\d{1,2}")
POLA_AREA = re.compile(r"\d+")
BARIS_NAMA_MAKS = 3
JENDELA_FILTER = 5
KALI_MAD = 5
DESIMAL = {"skor": 3, "p": 3, "rasio": 2, "persen": 1, "mV": 0, "detik": 0}
JENIS_BATAS_BAWAH = ["persen", "p"]
ANGKA_PENTING_AREA = 3
BARIS_MEDIAN_S1 = [40, 60, 100, 140]
KURANG_DARI = "less than"
AMBANG = {"akurasi": 0.85, "R2": 0.60}
E9_MENTAH = ["F1_rerata_seluruh", "F2_steady_mentah", "F3_proses_mentah"]
E9_KENAIKAN = ["F4_steady_minus_baseline", "F5_proses_minus_baseline"]
E9_TANPA_BASELINE = E9_KENAIKAN + ["F6_steady_relatif", "F7_puncak_minus_baseline"]
E9_ACUAN = E9_KENAIKAN[0]


def baca_xlsx(isi):
    return pd.read_excel(io.BytesIO(isi), header=None).values.astype(float)


def xlsx_enose(arsip):
    return [i for i in sorted(arsip.infolist(), key=lambda i: i.filename) if POLA_BERKAS.search(i.filename)]


def muat_enose():
    meta, sinyal = [], []
    with zipfile.ZipFile(ZIP_ENOSE) as arsip:
        for info in xlsx_enose(arsip):
            cocok = POLA_BERKAS.search(info.filename)
            x = baca_xlsx(arsip.read(info))
            meta.append(dict(berkas=Path(info.filename).name, minyak=cocok[1], jam=int(cocok[2]), ulang=int(cocok[3]),
                             baris=len(x), waktu=dt.datetime(*info.date_time)))
            sinyal.append(x)
    meta = pd.DataFrame(meta)
    meta["sesi"] = meta.minyak + "_" + meta.waktu.dt.strftime("%m%d")
    meta["sesi_jeda"] = sesi_berdasar_jeda(meta)
    return meta, sinyal


def sesi_berdasar_jeda(meta):
    urut = meta.sort_values("waktu")
    jeda = urut.groupby("minyak").waktu.diff().dt.total_seconds().div(3600).fillna(np.inf)
    nomor = (jeda >= JEDA_SESI_JAM).groupby(urut.minyak).cumsum()
    return (urut.minyak + "_" + nomor.astype(str)).reindex(meta.index)


def cukup_panjang(x, jendela):
    return len(x) >= jendela.stop


def rerata_jendela(sinyal, jendela):
    return np.array([x[jendela].mean(0) if cukup_panjang(x, jendela) else np.full(len(SENSOR), np.nan) for x in sinyal])


def puncak_jendela(sinyal, jendela):
    return np.array([x[jendela].max(0) if cukup_panjang(x, jendela) else np.full(len(SENSOR), np.nan) for x in sinyal])


def fitur_fase(sinyal):
    baseline = rerata_jendela(sinyal, BARIS_BASELINE)
    naik = rerata_jendela(sinyal, slice(BARIS_NAIK.stop - TITIK_UJUNG_NAIK, BARIS_NAIK.stop))
    awal = rerata_jendela(sinyal, slice(BARIS_NAIK.start, BARIS_NAIK.start + TITIK_UJUNG_NAIK))
    return dict(baseline=baseline, dR=rerata_jendela(sinyal, BARIS_STEADY) - baseline, slope=naik - awal)


def baris_lengkap(*larik):
    return np.all([~np.isnan(a).any(1) for a in larik], axis=0)


def rerata_per_titik(meta, X):
    tabel = pd.DataFrame(X, columns=SENSOR).assign(minyak=meta.minyak.values, jam=meta.jam.values)
    return tabel.groupby(["minyak", "jam"]).mean()


def jendela_teks(jendela):
    return f"{jendela.start}–{jendela.stop - 1}"


def berkas_penuh(meta):
    return (meta.baris >= PANJANG_PENUH).values


def panel_respons(sinyal, meta):
    return np.stack([(x - x[BARIS_BASELINE].mean(0)).T for x, ok in zip(sinyal, berkas_penuh(meta)) if ok])


def panel_pra_sampling(sinyal, meta):
    return np.stack([x[BARIS_PRA_SAMPLING].T for x, ok in zip(sinyal, berkas_penuh(meta)) if ok])


def siapkan_panel(meta, sinyal):
    return dict(penuh=meta[berkas_penuh(meta)].reset_index(drop=True), respons=panel_respons(sinyal, meta),
                pra=panel_pra_sampling(sinyal, meta))


def jumlah_kelas_panas(meta):
    y = label_dipanaskan(meta.jam)
    return dict(berkas=int(len(y)), segar=int((y == 0).sum()), dipanaskan=int((y == 1).sum()))


def label_dipanaskan(jam):
    return (np.asarray(jam, dtype=float) > 0).astype(int)


def dipanaskan(jam):
    return label_dipanaskan(jam).astype(bool)


def jam_per_sesi(meta, kolom="sesi"):
    return {s: sorted(set(meta.jam[meta[kolom] == s].tolist())) for s in sorted(set(meta[kolom]))}


def jam_kunci_dipanaskan(kamus):
    return [int(k) for k, p in zip(kamus, dipanaskan([int(k) for k in kamus])) if p]


def nilai_kunci_dipanaskan(kamus):
    return [v for v, p in zip(kamus.values(), dipanaskan([int(k) for k in kamus])) if p]


def nilai_kunci_segar(kamus):
    return [v for v, p in zip(kamus.values(), dipanaskan([int(k) for k in kamus])) if not p]


def lebih_dari_satu_saat_dipanaskan(kamus):
    return all(v > 1 for v in nilai_kunci_dipanaskan(kamus))


def gabung_nama(potongan):
    nama = potongan[0]
    for lanjut in potongan[1:]:
        nama += lanjut if nama.endswith("-") else " " + lanjut
    return nama


def baris_teks_gcms():
    with zipfile.ZipFile(ZIP_GCMS) as arsip:
        dokumen = pymupdf.open(stream=arsip.read(PDF_GCMS), filetype="pdf")
        teks = "".join(halaman.get_text() for halaman in dokumen)
    return [baris.strip() for baris in teks.split("\n") if baris.strip()]


def baca_puncak(baris, i):
    for n in range(1, BARIS_NAMA_MAKS + 1):
        j = i + 1 + n
        if j + 1 < len(baris) and POLA_CAS.fullmatch(baris[j]) and POLA_AREA.fullmatch(baris[j + 1]):
            return gabung_nama(baris[i + 1:j]), baris[j], int(baris[j + 1]), j + 2
    return None


def muat_gcms():
    baris, puncak, sampel, i = baris_teks_gcms(), [], None, 0
    while i < len(baris):
        if POLA_SAMPEL_GCMS.fullmatch(baris[i]):
            sampel = POLA_SAMPEL_GCMS.fullmatch(baris[i])
            i += 1
            continue
        hasil = baca_puncak(baris, i) if sampel and POLA_RT.fullmatch(baris[i]) else None
        if hasil:
            nama, cas, area, berikut = hasil
            puncak.append((sampel[1], int(sampel[2]), float(baris[i]), nama, cas, area))
            i = berikut
            continue
        i += 1
    return pd.DataFrame(puncak, columns=["minyak", "jam", "RT", "senyawa", "CAS", "area"])


def total_area_gcms(gcms):
    return gcms.groupby(["minyak", "jam"]).area.sum()


def titik_total_gcms(meta, X, gcms):
    return rerata_per_titik(meta, X).join(total_area_gcms(gcms).rename("gc_total"), how="inner")


def titik_gcms_dipanaskan(titik):
    return dipanaskan(titik.index.get_level_values("jam"))


def ke_json(nilai):
    if isinstance(nilai, dict):
        return {str(k): ke_json(v) for k, v in nilai.items()}
    if isinstance(nilai, (list, tuple, np.ndarray, pd.Series)):
        return [ke_json(v) for v in list(nilai)]
    if isinstance(nilai, (np.integer,)):
        return int(nilai)
    if isinstance(nilai, (np.floating, float)):
        return float(nilai)
    return nilai


def seri_ke_dict(seri):
    return {str(k): float(v) for k, v in seri.items()}


def simpan_json(nama, isi):
    HASIL.mkdir(exist_ok=True)
    (HASIL / nama).write_text(json.dumps(ke_json(isi), indent=1, ensure_ascii=False))


def baca_json(nama):
    return json.loads((HASIL / nama).read_text())


def bulat(nilai, jenis):
    satuan = Decimal(1).scaleb(-DESIMAL[jenis])
    angka = Decimal(repr(float(nilai))).quantize(satuan, rounding=ROUND_HALF_UP)
    if angka == 0 and nilai != 0 and jenis in JENIS_BATAS_BAWAH:
        return f"< {satuan}" if jenis == "p" else f"{KURANG_DARI} {satuan}"
    return str(abs(angka) if angka == 0 else angka)


def bulat_ilmiah(nilai, angka_penting=ANGKA_PENTING_AREA):
    angka = Decimal(repr(float(nilai)))
    pangkat = angka.adjusted()
    satuan = Decimal(1).scaleb(1 - angka_penting)
    mantisa = angka.scaleb(-pangkat).quantize(satuan, rounding=ROUND_HALF_UP)
    if abs(mantisa) >= 10:
        mantisa, pangkat = (mantisa / 10).quantize(satuan, rounding=ROUND_HALF_UP), pangkat + 1
    return str(mantisa), pangkat


def median_bergulir(x):
    return pd.DataFrame(x).rolling(JENDELA_FILTER, center=True, min_periods=1).median().values


def mad_jendela(nilai):
    return np.median(np.abs(nilai - np.median(nilai)))


def mad_bergulir(x):
    return pd.DataFrame(x).rolling(JENDELA_FILTER, center=True, min_periods=1).apply(mad_jendela, raw=True).values


def buang_lonjakan(x):
    median = median_bergulir(x)
    lonjakan = np.abs(x - median) > KALI_MAD * mad_bergulir(x)
    return np.where(lonjakan, median, x), lonjakan


def saring_sinyal(x):
    bersih, lonjakan = buang_lonjakan(x)
    return median_filter(bersih, size=(JENDELA_FILTER, 1), mode="nearest"), lonjakan
