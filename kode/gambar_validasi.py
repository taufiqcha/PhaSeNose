import re
import textwrap

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from gaya_gambar import (GARIS_TEBAL, HURUF_KECIL, LEBAR_KOLOM_PT, WARNA, atur_gaya, baca_baris_tabel, baca_makro,
                         inci, simpan, teks_dari_tex)

KELUARAN = "gambar_validasi.pdf"
TINGGI_PT = 330
KOSONG = "--"
BATAS_X = 1.03
LEBAR_LABEL = 20
JARAK_KELOMPOK = 1.0
TAMBAH_PER_BARIS = 0.4
UKURAN = {"acak": 60, "sesi": 24, "kontrol": 22}
POLA_CATATAN = re.compile(r"\$\^\{\w\}\$")


def angka(sel):
    teks = POLA_CATATAN.sub("", sel).strip()
    return None if teks == KOSONG else float(teks)


def label(sel):
    return "\n".join(textwrap.wrap(teks_dari_tex(sel), LEBAR_LABEL))


def baris_varian():
    return [dict(nama=b[0].split(",")[0], acak=angka(b[1]), sesi=angka(b[2]), kontrol=None)
            for b in baca_baris_tabel("TabelFitur")]


def sudah_varian(nama, varian):
    return any(f"({v['nama']})" in nama for v in varian)


def baris_detektor(varian):
    return [dict(nama=label(b[0]), acak=angka(b[2]), sesi=angka(b[3]), kontrol=angka(b[4]))
            for b in baca_baris_tabel("TabelDetektor") if angka(b[2]) is not None and not sudah_varian(b[0], varian)]


def posisi(kelompok):
    y, hasil = 0.0, []
    for baris in kelompok:
        ys = []
        for b in baris:
            tambahan = TAMBAH_PER_BARIS * b["nama"].count("\n")
            ys.append(y + tambahan / 2)
            y += 1 + tambahan
        hasil.append(ys)
        y += JARAK_KELOMPOK
    return hasil


def gambar_baris(ax, b, y, fokus):
    warna_sesi = WARNA["accent"] if fokus else WARNA["ink"]
    ax.plot([b["acak"], b["sesi"]], [y, y], color=WARNA["rule"], lw=GARIS_TEBAL * 1.6, zorder=1,
            solid_capstyle="round")
    ax.scatter(b["acak"], y, s=UKURAN["acak"], marker="|", color=WARNA["muted"], zorder=4, lw=GARIS_TEBAL)
    ax.scatter(b["sesi"], y, s=UKURAN["sesi"], color=warna_sesi, zorder=3, lw=0)
    if b["kontrol"] is not None:
        ax.scatter(b["kontrol"], y, s=UKURAN["kontrol"], facecolor=WARNA["paper"], edgecolor=WARNA["ink"],
                   lw=0.8, zorder=3)


def legenda(fig, makro):
    unsur = [Line2D([], [], marker="|", ls="", color=WARNA["muted"], ms=7, mew=GARIS_TEBAL,
                    label=f"{makro['Lipat']}-fold CV"),
             Line2D([], [], marker="o", ls="", color=WARNA["ink"], ms=4.7, label="LOSO"),
             Line2D([], [], marker="o", ls="", mfc=WARNA["paper"], mec=WARNA["ink"], mew=0.8, ms=4.5,
                    label="Control, LOSO"),
             Line2D([], [], ls=(0, (3, 2)), color=WARNA["ink"], lw=0.8, label="Acceptance level")]
    fig.legend(handles=unsur, loc="lower center", ncol=2, frameon=False, handletextpad=0.3, columnspacing=1.0,
               handlelength=1.4, bbox_to_anchor=(0.5, 0.0))


def main():
    atur_gaya()
    makro = baca_makro()
    varian = baris_varian()
    kelompok = [varian, baris_detektor(varian)]
    judul = ["Feature variants, LDA", "Detectors"]
    fig, ax = plt.subplots(figsize=(inci(LEBAR_KOLOM_PT), inci(TINGGI_PT)))
    fig.subplots_adjust(left=0.4, right=0.96, top=0.96, bottom=0.2)
    ambang = float(makro["AmbangBA"])
    ax.axvline(ambang, color=WARNA["ink"], ls=(0, (3, 2)), lw=0.8, zorder=0)
    ax.text(ambang, -1.35, makro["AmbangBA"], ha="center", va="bottom", fontsize=HURUF_KECIL,
            bbox=dict(facecolor=WARNA["paper"], edgecolor="none", pad=0.5))
    nama_y, y_semua = [], []
    for baris, ys, kepala in zip(kelompok, posisi(kelompok), judul):
        fokus = max(range(len(baris)), key=lambda i: baris[i]["sesi"])
        for i, (b, y) in enumerate(zip(baris, ys)):
            gambar_baris(ax, b, y, i == fokus)
        ax.text(-0.02, ys[0] - 0.85, kepala, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontweight="bold", fontsize=HURUF_KECIL)
        nama_y += [b["nama"] for b in baris]
        y_semua += ys
    ax.set_yticks(y_semua)
    ax.set_yticklabels(nama_y, linespacing=0.95)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_ylim(y_semua[-1] + 0.7, -1.4)
    ax.set_xlim(0, BATAS_X)
    ax.set_xlabel("Balanced accuracy")
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    legenda(fig, makro)
    simpan(fig, KELUARAN)


if __name__ == "__main__":
    main()
