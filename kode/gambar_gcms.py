import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from data import MINYAK, MURAH, baca_json, bulat, dipanaskan
from gaya_gambar import (GARIS_TEBAL, HURUF, HURUF_KECIL, LEBAR_KOLOM_PT, WARNA, atur_gaya, inci, kisi_horizontal,
                         label_panel, simpan)

KELUARAN = "gambar_gcms.pdf"
TINGGI_PT = 400
RUANG_ATAS = 1.08
UKURAN_TITIK = 16


def skala(nilai):
    return 10 ** (math.floor(math.log10(max(nilai))) - 1)


def satuan(pangkat):
    return f"(×10$^{{{int(round(math.log10(pangkat)))}}}$)"


def gaya_minyak(minyak):
    return (WARNA["ink"], "-") if minyak == MURAH else (WARNA["muted"], (0, (3, 2)))


def panel_area(ax, area, faktor):
    for minyak in MINYAK:
        jam = sorted(int(k) for k in area[minyak])
        y = [area[minyak][str(j)] / faktor for j in jam]
        warna, garis = gaya_minyak(minyak)
        ax.plot(jam, y, marker="o", ms=3.2, color=warna, ls=garis, lw=GARIS_TEBAL)
        ax.text(jam[-1] + 1.5, y[-1], minyak, color=warna, va="center", fontweight="bold", fontsize=HURUF_KECIL)
    ax.set_xticks(sorted({int(k) for m in MINYAK for k in area[m]}))
    ax.set_xlim(-3, max(jam) + 8)
    ax.set_ylim(0, max(v / faktor for m in MINYAK for v in area[m].values()) * RUANG_ATAS)
    ax.set_xlabel("Heating level (h)")
    ax.set_ylabel(f"Total area {satuan(faktor)}")
    kisi_horizontal(ax)


def titik(prediksi, kontrol, faktor):
    kunci = list(prediksi)
    jam = np.array([int(k.split()[1]) for k in kunci])
    return dict(ukur=np.array([prediksi[k]["gc_total"] for k in kunci]) / faktor,
                pls=np.array([prediksi[k]["prediksi_pls_semua_sensor"] for k in kunci]) / faktor,
                kontrol=np.array([kontrol[k]["prediksi_pls_semua_sensor"] for k in kunci]) / faktor,
                panas=dipanaskan(jam))


def panel_prediksi(ax, t, r2):
    batas = max(t["ukur"].max(), t["pls"].max(), t["kontrol"].max()) * RUANG_ATAS
    ax.plot([0, batas], [0, batas], color=WARNA["ink"], ls=(0, (3, 2)), lw=0.8, zorder=0)
    ax.scatter(t["ukur"], t["kontrol"], marker="x", s=UKURAN_TITIK, color=WARNA["muted"], lw=0.9, zorder=2)
    ax.scatter(t["ukur"][t["panas"]], t["pls"][t["panas"]], s=UKURAN_TITIK, color=WARNA["accent"], lw=0, zorder=3)
    ax.scatter(t["ukur"][~t["panas"]], t["pls"][~t["panas"]], s=UKURAN_TITIK, facecolor=WARNA["paper"],
               edgecolor=WARNA["accent"], lw=0.9, zorder=3)
    ax.text(0.03, 0.97, f"Responses, $R^2$ = {r2['pls']}", transform=ax.transAxes, va="top", color=WARNA["accent"],
            fontsize=HURUF)
    ax.text(0.03, 0.87, f"Baselines, $R^2$ = {r2['kontrol']}", transform=ax.transAxes, va="top",
            color=WARNA["muted"], fontsize=HURUF)
    ax.set_xlim(0, batas)
    ax.set_yticks([v for v in ax.get_xticks() if v <= batas])
    ax.set_ylim(0, batas)
    ax.set_aspect("equal")
    kisi_horizontal(ax)


def legenda(fig):
    unsur = [Line2D([], [], marker="o", ls="", color=WARNA["accent"], ms=4, label="Responses, heated"),
             Line2D([], [], marker="o", ls="", mfc=WARNA["paper"], mec=WARNA["accent"], ms=4, label="Responses, fresh"),
             Line2D([], [], marker="x", ls="", color=WARNA["muted"], ms=4, label="Baselines (control)"),
             Line2D([], [], ls=(0, (3, 2)), color=WARNA["ink"], lw=0.8, label="1:1")]
    fig.legend(handles=unsur, loc="lower center", ncol=2, frameon=False, handletextpad=0.3, columnspacing=1.0,
               handlelength=1.4, fontsize=HURUF_KECIL, bbox_to_anchor=(0.5, 0.0))


def main():
    atur_gaya()
    intensitas, korelasi = baca_json("uji_intensitas.json"), baca_json("uji_korelasi_gcms.json")
    area = intensitas["total_area_gcms"]
    faktor = skala([v for m in MINYAK for v in area[m].values()])
    t = titik(korelasi["prediksi_loo_per_titik"], korelasi["kontrol_baseline_prediksi_loo_per_titik"], faktor)
    r2 = {"pls": bulat(korelasi["R2_LOO_pls_semua_sensor"]["semua"], "skor").replace("-", "−"),
          "kontrol": bulat(korelasi["kontrol_baseline_R2_LOO_pls_semua_sensor"]["semua"], "skor")
          .replace("-", "−")}
    fig = plt.figure(figsize=(inci(LEBAR_KOLOM_PT), inci(TINGGI_PT)))
    ax_a = fig.add_axes([0.2, 0.72, 0.74, 0.25])
    ax_b = fig.add_axes([0.2, 0.17, 0.74, 0.44])
    panel_area(ax_a, area, faktor)
    panel_prediksi(ax_b, t, r2)
    ax_b.set_xlabel(f"Measured total area {satuan(faktor)}")
    ax_b.set_ylabel(f"Predicted total area {satuan(faktor)}")
    label_panel(ax_a, "a", x=-0.2)
    label_panel(ax_b, "b", x=-0.2)
    legenda(fig)
    simpan(fig, KELUARAN)


if __name__ == "__main__":
    main()
