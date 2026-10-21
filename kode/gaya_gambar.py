import re

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt

from data import AKAR, HASIL

FOLDER_GAMBAR = AKAR / "figures"
ANGKA_TEX = HASIL / "angka.tex"
WARNA = {"ink": "#2d3142", "muted": "#4f5d75", "soft": "#5a6580", "rule": "#bfc0c0", "accent": "#bf4520",
         "paper": "#ffffff"}
ISIAN_FOKUS = 0.08
ISIAN_DATA = 0.05
PT_PER_INCI = 72
LEBAR_KOLOM_PT = 238.25
HURUF = 10.2
HURUF_KECIL = 8
GARIS = 1.0
GARIS_TEBAL = 1.2
POLA_MAKRO = re.compile(r"\\newcommand\{\\(\w+)\}\{(.*)\}$")
PENGGANTI_TEX = [("$\\Delta R$", "ΔR"), ("--", "–"), ("$-$", "−"), ("\\%", "%"), ("~", " ")]


def inci(pt):
    return pt / PT_PER_INCI


def atur_gaya():
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica"],
                         "font.size": HURUF, "axes.labelsize": HURUF, "axes.titlesize": HURUF,
                         "xtick.labelsize": HURUF_KECIL, "ytick.labelsize": HURUF_KECIL,
                         "legend.fontsize": HURUF_KECIL, "axes.edgecolor": WARNA["ink"],
                         "axes.labelcolor": WARNA["ink"], "text.color": WARNA["ink"], "xtick.color": WARNA["ink"],
                         "ytick.color": WARNA["ink"], "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                         "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
                         "grid.color": WARNA["rule"], "grid.linewidth": 0.4, "lines.linewidth": GARIS,
                         "pdf.fonttype": 42, "mathtext.fontset": "custom", "mathtext.rm": "Arial",
                         "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold",
                         "figure.facecolor": WARNA["paper"], "savefig.facecolor": WARNA["paper"]})


def kisi_horizontal(ax):
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)


def label_panel(ax, huruf, x=-0.02, y=1.0):
    ax.text(x, y, f"({huruf})", transform=ax.transAxes, ha="right", va="bottom", fontweight="bold")


def teks_dari_tex(teks):
    for lama, baru in PENGGANTI_TEX:
        teks = teks.replace(lama, baru)
    return teks


def baca_makro():
    makro = {}
    for baris in ANGKA_TEX.read_text().splitlines():
        cocok = POLA_MAKRO.match(baris)
        if cocok:
            makro[cocok[1]] = cocok[2]
    return makro


def baca_baris_tabel(nama):
    isi = re.search(r"\\newcommand\{\\" + nama + r"\}\{(.*?)\}\n\\newcommand", ANGKA_TEX.read_text(), re.S)
    return [[sel.strip() for sel in baris.rstrip(" \\").split("&")] for baris in isi[1].strip().splitlines()]


def simpan(fig, nama):
    FOLDER_GAMBAR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FOLDER_GAMBAR / nama, format="pdf", metadata={"CreationDate": None})
    plt.close(fig)
