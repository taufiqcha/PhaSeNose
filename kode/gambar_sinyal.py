import matplotlib.pyplot as plt
import numpy as np

from data import (BARIS_BASELINE, BARIS_MEDIAN_S1, BARIS_PRA_SAMPLING, BARIS_SAMPLING, BARIS_STEADY, KOLOM_S1,
                  PANJANG_PENUH, SENSOR, baca_json, bulat, jendela_teks, muat_enose, panel_respons)
from gaya_gambar import (GARIS_TEBAL, HURUF_KECIL, ISIAN_DATA, ISIAN_FOKUS, LEBAR_KOLOM_PT, WARNA, atur_gaya, inci,
                         kisi_horizontal, label_panel, simpan)

KELUARAN = "gambar_sinyal.pdf"
TINGGI_PT = 300
CONTOH = [("SIP", 0, 1, "Fresh"), ("SIP", 30, 1, "Heated")]
JENDELA_ICITEE = "ICITEE_50_140"
FASE = [("C", BARIS_PRA_SAMPLING), ("S", BARIS_SAMPLING), ("P", slice(BARIS_SAMPLING.stop, PANJANG_PENUH))]
GESER_LABEL = {40: (-4, 2), 60: (4, 3), 100: (0, 5), 140: (0, 5)}
GESER_KURUNG = 1.5
TOLERANSI_MV = 1e-6


def pilih(meta, minyak, jam, ulang):
    return int(meta.index[(meta.minyak == minyak) & (meta.jam == jam) & (meta.ulang == ulang)][0])


def arsir_fase(ax, y_label):
    for nama, jendela in FASE:
        if nama == "S":
            ax.axvspan(jendela.start, jendela.stop - 1, color=WARNA["ink"], alpha=ISIAN_DATA, lw=0)
        ax.text((jendela.start + jendela.stop - 1) / 2, y_label, nama, ha="center", va="bottom",
                fontsize=HURUF_KECIL, color=WARNA["soft"], transform=ax.get_xaxis_transform())


def panel_mentah(ax, x, judul):
    for j in reversed(range(len(SENSOR))):
        fokus = j == KOLOM_S1
        ax.plot(np.arange(len(x)), x[:, j], color=WARNA["ink"] if fokus else WARNA["soft"],
                lw=GARIS_TEBAL if fokus else 0.5, zorder=3 if fokus else 2)
    arsir_fase(ax, 1.0)
    ax.set_title(judul, fontsize=HURUF_KECIL, pad=10, loc="left")
    ax.set_xlim(0, PANJANG_PENUH - 1)
    ax.set_xlabel("Time (s)")
    kisi_horizontal(ax)


def kurung(ax, jendela, y, teks, gaya, warna, atas=True, rata="center"):
    ax.plot([jendela.start, jendela.stop - 1], [y, y], color=warna, ls=gaya, lw=0.9, solid_capstyle="butt")
    x = jendela.start if rata == "left" else (jendela.start + jendela.stop - 1) / 2
    ax.annotate(teks, (x, y), xytext=(0, GESER_KURUNG if atas else -GESER_KURUNG), textcoords="offset points",
                ha=rata, va="bottom" if atas else "top", fontsize=HURUF_KECIL, color=warna,
                bbox=dict(facecolor=WARNA["paper"], edgecolor="none", pad=0.3))


def panel_median(ax, median, nilai_json, icitee):
    ax.axvspan(BARIS_STEADY.start, BARIS_STEADY.stop - 1, color=WARNA["accent"], alpha=ISIAN_FOKUS, lw=0)
    ax.plot(np.arange(len(median)), median, color=WARNA["ink"], lw=GARIS_TEBAL)
    for baris in BARIS_MEDIAN_S1:
        nilai = nilai_json[str(baris)]
        ax.scatter(baris, nilai, s=12, color=WARNA["ink"], zorder=3, lw=0)
        dx, dy = GESER_LABEL[baris]
        ax.annotate(bulat(nilai, "mV"), (baris, nilai), xytext=(dx, dy), textcoords="offset points",
                    fontsize=HURUF_KECIL, ha={-1: "right", 0: "center", 1: "left"}[int(np.sign(dx))], va="bottom")
    puncak = np.nanmax(median)
    kurung(ax, BARIS_BASELINE, -puncak * 0.08, f"baseline {jendela_teks(BARIS_BASELINE)}", "-", WARNA["muted"],
           atas=False, rata="left")
    kurung(ax, icitee, puncak * 1.03, f"fixed window {jendela_teks(icitee)}", (0, (3, 2)), WARNA["ink"])
    kurung(ax, BARIS_STEADY, puncak * 0.78, f"steady {jendela_teks(BARIS_STEADY)}", "-", WARNA["accent"])
    arsir_fase(ax, 1.0)
    ax.set_xlim(0, PANJANG_PENUH - 1)
    ax.set_ylim(-puncak * 0.3, puncak * 1.22)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(f"Median {SENSOR[KOLOM_S1]} (mV)")
    kisi_horizontal(ax)


def jendela_dari_teks(teks):
    awal, akhir = (int(v) for v in teks.split("–"))
    return slice(awal, akhir + 1)


def main():
    atur_gaya()
    meta, sinyal = muat_enose()
    steady = baca_json("uji_jendela_steady.json")
    median = np.median(panel_respons(sinyal, meta)[:, KOLOM_S1, :], axis=0)
    nilai_json = steady["median_S1_baris"]
    if not np.allclose([median[b] for b in BARIS_MEDIAN_S1], [nilai_json[str(b)] for b in BARIS_MEDIAN_S1],
                       atol=TOLERANSI_MV):
        raise ValueError("median S1 tidak sama dengan results/uji_jendela_steady.json")
    fig = plt.figure(figsize=(inci(LEBAR_KOLOM_PT), inci(TINGGI_PT)))
    ax_kiri = fig.add_axes([0.17, 0.58, 0.37, 0.33])
    ax_kanan = fig.add_axes([0.6, 0.58, 0.37, 0.33], sharey=ax_kiri)
    for ax, (minyak, jam, ulang, kata) in zip([ax_kiri, ax_kanan], CONTOH):
        panel_mentah(ax, sinyal[pilih(meta, minyak, jam, ulang)], f"{kata}, {minyak} {jam} h (rep. {ulang})")
    ax_kiri.set_ylabel("Voltage (mV)")
    plt.setp(ax_kanan.get_yticklabels(), visible=False)
    ax_b = fig.add_axes([0.17, 0.1, 0.8, 0.33])
    panel_median(ax_b, median, nilai_json, jendela_dari_teks(steady["pembanding"][JENDELA_ICITEE]["baris"]))
    label_panel(ax_kiri, "a", x=-0.3, y=1.13)
    label_panel(ax_b, "b", x=-0.14, y=1.07)
    simpan(fig, KELUARAN)


if __name__ == "__main__":
    main()
