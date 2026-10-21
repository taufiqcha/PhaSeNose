import re
import zipfile
from pathlib import Path

import pandas as pd
import pymupdf

from data import PDF_GCMS, POLA_BERKAS, ZIP_ENOSE, ZIP_GCMS, baca_xlsx, muat_gcms, simpan_json, xlsx_enose

POLA_AKUISISI = re.compile(r"Acquired\s*:\s*(\d+ \w+ \d{4})")
POLA_METODE = re.compile(r"Misc Info\s*:\s*(.*)")


def ringkas_xlsx():
    with zipfile.ZipFile(ZIP_ENOSE) as arsip:
        bentuk = {Path(i.filename).name: baca_xlsx(arsip.read(i)).shape for i in xlsx_enose(arsip)}
    label = pd.DataFrame([POLA_BERKAS.search(n).groups() for n in bentuk], columns=["minyak", "jam", "ulang"])
    baris = {n: b[0] for n, b in bentuk.items()}
    return dict(jumlah=len(bentuk), minyak=sorted(label.minyak.unique()), jam=sorted(label.jam.astype(int).unique()),
                ulangan=sorted(label.ulang.astype(int).unique()), kolom=sorted({b[1] for b in bentuk.values()}),
                baris_terbanyak=max(baris.values()), baris_tersedikit=min(baris.values()),
                berkas_di_bawah_terbanyak={n: b for n, b in baris.items() if b < max(baris.values())})


def kepala_kromatogram(isi):
    teks = pymupdf.open(stream=isi, filetype="pdf")[0].get_text()
    return dict(akuisisi=POLA_AKUISISI.search(teks)[1], metode=POLA_METODE.search(teks)[1].strip())


def ringkas_gcms():
    with zipfile.ZipFile(ZIP_GCMS) as arsip:
        kromatogram = {Path(n).name: kepala_kromatogram(arsip.read(n))
                       for n in sorted(arsip.namelist()) if n != PDF_GCMS}
    return dict(kromatogram=kromatogram, puncak=len(muat_gcms()),
                tanggal_akuisisi=sorted({k["akuisisi"] for k in kromatogram.values()}),
                metode=sorted({k["metode"] for k in kromatogram.values()}))


def main():
    simpan_json("uji_inventaris.json", dict(xlsx=ringkas_xlsx(), gcms=ringkas_gcms()))


if __name__ == "__main__":
    main()
