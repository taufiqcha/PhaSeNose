import numpy as np

from data import JENDELA_FILTER, KALI_MAD, mad_bergulir, muat_enose, saring_sinyal, siapkan_panel, simpan_json
from model import segar_rocket_sesi


def main():
    meta, sinyal = muat_enose()
    tersaring = [saring_sinyal(x) for x in sinyal]
    bersih = [x for x, _ in tersaring]
    diganti = {b: int(l.sum()) for b, (_, l) in zip(meta.berkas, tersaring)}
    mad_nol = {b: int((l & (mad_bergulir(x) == 0)).sum()) for b, x, (_, l) in zip(meta.berkas, sinyal, tersaring)}
    simpan_json("uji_penyaringan.json", dict(
        jendela_detik=JENDELA_FILTER, kali_mad=KALI_MAD,
        titik_diganti_per_berkas=diganti, total_titik_diganti=sum(diganti.values()),
        titik_diganti_di_jendela_mad_nol_per_berkas=mad_nol,
        total_titik_diganti_di_jendela_mad_nol=sum(mad_nol.values()),
        fraksi_jendela_mad_nol=float(np.mean(np.concatenate([(mad_bergulir(x) == 0).ravel() for x in sinyal]))),
        total_titik=int(sum(x.size for x in sinyal)),
        minirocket_tinggalkan_sesi=dict(tanpa_filter=segar_rocket_sesi(siapkan_panel(meta, sinyal)),
                                        dengan_filter=segar_rocket_sesi(siapkan_panel(meta, bersih)))))


if __name__ == "__main__":
    main()
