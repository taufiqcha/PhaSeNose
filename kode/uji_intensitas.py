from data import (MAHAL, MINYAK, MURAH, SENSOR, fitur_fase, lebih_dari_satu_saat_dipanaskan, muat_enose, muat_gcms,
                  rerata_per_titik, seri_ke_dict, simpan_json, total_area_gcms)


def rasio_murah_mahal(seri):
    return seri_ke_dict(seri[MURAH] / seri[MAHAL])


def main():
    meta, sinyal = muat_enose()
    total = total_area_gcms(muat_gcms())
    titik = rerata_per_titik(meta, fitur_fase(sinyal)["dR"])
    rasio_dR = {s: rasio_murah_mahal(titik[s]) for s in SENSOR}
    simpan_json("uji_intensitas.json", dict(
        total_area_gcms={m: seri_ke_dict(total[m]) for m in MINYAK}, rasio_gcms_total_SIP_SA=rasio_murah_mahal(total),
        rasio_dR_semua_sensor_SIP_SA=rasio_dR,
        sensor_rasio_dR_lebih_dari_1_di_semua_jam_dipanaskan=[
            s for s, r in rasio_dR.items() if lebih_dari_satu_saat_dipanaskan(r)]))


if __name__ == "__main__":
    main()
