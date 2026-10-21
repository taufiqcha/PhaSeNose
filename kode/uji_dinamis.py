from sklearn.model_selection import LeaveOneGroupOut

from data import fitur_fase, label_dipanaskan, muat_enose, simpan_json
from model import uji_kelas


def main():
    meta, sinyal = muat_enose()
    slope, y = fitur_fase(sinyal)["slope"], label_dipanaskan(meta.jam)
    simpan_json("uji_dinamis.json", dict(
        slope_segar_vs_panas=uji_kelas(slope, y),
        slope_segar_vs_panas_tinggalkan_sesi=uji_kelas(slope, y, LeaveOneGroupOut(), meta.sesi.values)))


if __name__ == "__main__":
    main()
