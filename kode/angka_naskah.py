import datetime as dt
import platform
from importlib.metadata import version
import math
import re

from data import (AMBANG, BARIS_BASELINE, BARIS_NAIK, BARIS_PRA_SAMPLING, BARIS_SAMPLING, BARIS_STEADY, E9_ACUAN,
                  E9_MENTAH, E9_TANPA_BASELINE, HASIL, JEDA_SESI_JAM, JENDELA_FILTER, KALI_MAD, KOLOM_S1,
                  PANJANG_PENUH, POLA_BERKAS, SEED, SENSOR, TITIK_UJUNG_NAIK, baca_json, bulat, bulat_ilmiah,
                  jam_kunci_dipanaskan, jendela_teks, lebih_dari_satu_saat_dipanaskan, nilai_kunci_dipanaskan,
                  dipanaskan, nilai_kunci_segar)
from model import ALFA_ROCKET, JUMLAH_PERMUTASI, KOMPONEN_PLS, LIPAT, LIPAT_DALAM

KELUARAN = HASIL / "angka.tex"
KATA = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
VARIAN_E9 = {"B0_baseline_saja": "B0, baseline only", "F1_rerata_seluruh": "F1, raw mean of the whole record",
             "F2_steady_mentah": "F2, raw mean of the steady window",
             "F3_proses_mentah": "F3, raw mean of the sampling phase",
             "F4_steady_minus_baseline": "F4, steady window minus baseline",
             "F5_proses_minus_baseline": "F5, sampling phase minus baseline",
             "F6_steady_relatif": "F6, steady window relative to baseline",
             "F7_puncak_minus_baseline": "F7, sampling peak minus baseline"}
NAMA_BULAN = "%d %B %Y"
NAMA_BARIS_MEDIAN = {40: "Empat", 60: "Enam", 100: "Seratus", 140: "SeratusEmpat"}
PUSTAKA = {"Sklearn": "scikit-learn", "Sktime": "sktime", "Numpy": "numpy", "Scipy": "scipy"}
KODE_VARIAN = ["Nol", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh"]
FITUR_LOSO = ["Nol", "Tiga", "Empat", "Tujuh"]
FITUR_LIMA = ["Nol"]
FITUR_SFS = ["Nol", "Tujuh"]
POLA_SUHU = re.compile(r"(\d+)C")
POLA_MENIT = re.compile(r"(\d+)mnt")
POLA_SERAT = re.compile(r"([A-Z]+(?:/[A-Z]+)+)")
POLA_PANJANG = re.compile(r"(\d+)cm")


def s3(x):
    return tanda(bulat(x, "skor"))


def rasio(x):
    return tanda(bulat(x, "rasio"))


def persen(x):
    return bulat(100 * x, "persen") + r"\%"


def mv(x):
    return tanda(bulat(x, "mV"))


def nilai_p(x):
    teks = bulat(x, "p")
    return f"$<$ {teks[2:]}" if teks.startswith("<") else teks


def relasi_p(x):
    teks = bulat(x, "p")
    return f"$p < {teks[2:]}$" if teks.startswith("<") else f"$p = {teks}$"


def ilmiah(x):
    mantisa, pangkat = bulat_ilmiah(x)
    return f"${mantisa} \\times 10^{{{pangkat}}}$"


def tanda(teks):
    return r"$-$" + teks[1:] if teks.startswith("-") else teks


def pangkat(x):
    return f"$10^{{{round(math.log10(x))}}}$"


def kata(n):
    return KATA[n] if 0 <= n < len(KATA) else str(n)


def jendela(j):
    return jendela_teks(j).replace("–", "--")


def deret(daftar):
    daftar = [str(x) for x in daftar]
    return daftar[0] if len(daftar) == 1 else ", ".join(daftar[:-1]) + (", and " if len(daftar) > 2 else " and ") + \
        daftar[-1]


def rentang(nilai, fungsi):
    return f"{fungsi(min(nilai))}--{fungsi(max(nilai))}"


def ba(skor):
    return s3(skor["akurasi_seimbang"])


def acc(skor):
    return s3(skor["akurasi"])


def tanggal(teks):
    return dt.datetime.fromisoformat(teks).strftime(NAMA_BULAN).lstrip("0")


def makro_berkas_pendek(x):
    pendek = [POLA_BERKAS.search(b).groups() for b in x["berkas_di_bawah_terbanyak"]]
    return {"NBerkasPendek": kata(len(pendek)), "BerkasPendekMinyak": deret([m for m, _, _ in pendek]),
            "BerkasPendekJam": deret([j for _, j, _ in pendek]), "BerkasPendekUlang": deret([u for _, _, u in pendek])}


def makro_inventaris(j):
    x = j["xlsx"]
    metode = j["gcms"]["metode"][0]
    return {**makro_berkas_pendek(x), "NBerkas": x["jumlah"], "NMinyak": kata(len(x["minyak"])),
            "NLevel": kata(len(x["jam"])),
            "NUlang": kata(len(x["ulangan"])), "JamMaks": max(x["jam"]),
            "DaftarJam": deret(x["jam"]), "BarisMaks": x["baris_terbanyak"], "BarisMin": x["baris_tersedikit"],
            "NSensor": kata(len(SENSOR)),
            "GCSuhu": POLA_SUHU.search(metode)[1], "GCMenit": POLA_MENIT.search(metode)[1],
            "GCSerat": POLA_SERAT.search(metode)[1], "GCPanjangSerat": POLA_PANJANG.search(metode)[1]}


def makro_jendela(j):
    awal = slice(BARIS_NAIK.start, BARIS_NAIK.start + TITIK_UJUNG_NAIK)
    ujung = slice(BARIS_NAIK.stop - TITIK_UJUNG_NAIK, BARIS_NAIK.stop)
    icitee, lama = j["pembanding"]["ICITEE_50_140"], j["pembanding"]["plateau_lama_40_149"]
    median = j["median_S1_baris"]
    return {"BarisPra": jendela(BARIS_PRA_SAMPLING), "BarisBaseline": jendela(BARIS_BASELINE),
            "BarisNaik": jendela(BARIS_NAIK), "BarisNaikAwal": jendela(awal), "BarisNaikUjung": jendela(ujung),
            "TitikUjungNaik": kata(TITIK_UJUNG_NAIK), "BarisSampling": jendela(BARIS_SAMPLING),
            "BarisPurging": jendela(slice(BARIS_SAMPLING.stop, PANJANG_PENUH)), "BarisSteady": jendela(BARIS_STEADY),
            "BarisCari": f"{BARIS_SAMPLING.start}--{j['batas_akhir_semua_berkas']}",
            "AmbangSteady": persen(j["ambang_perubahan"]), "BarisUjung": j["baris_ujung"],
            "PanjangSteady": j["panjang_steady"], "SteadyMaks": persen(j["steady"]["perubahan_relatif_maks"]),
            "IciteeBaris": icitee["baris"].replace("–", "--"), "IciteeMaks": persen(icitee["perubahan_relatif_maks"]),
            "IciteeSensor": kata(icitee["sensor_berubah_lebih_dari_ambang"]),
            "LamaBaris": lama["baris"].replace("–", "--"), "LamaMaks": persen(lama["perubahan_relatif_maks"]),
            **{f"MedianSi{NAMA_BARIS_MEDIAN[int(b)]}": mv(v) for b, v in median.items()},
            **{f"MedianBaris{NAMA_BARIS_MEDIAN[int(b)]}": b for b in median}}


def makro_versi():
    return {"VersiPython": platform.python_version(), **{f"Versi{k}": version(p) for k, p in PUSTAKA.items()}}


def makro_model():
    return {"Seed": SEED, "Lipat": LIPAT, "LipatDalam": kata(LIPAT_DALAM), "Permutasi": JUMLAH_PERMUTASI,
            "KomponenPLS": kata(KOMPONEN_PLS), "NAlfaRocket": len(ALFA_ROCKET),
            "AlfaMin": pangkat(ALFA_ROCKET.min()), "AlfaMaks": pangkat(ALFA_ROCKET.max()),
            "AmbangBA": s3(AMBANG["akurasi"]), "AmbangRdua": s3(AMBANG["R2"]),
            "JedaSesi": JEDA_SESI_JAM, "JendelaFilter": JENDELA_FILTER, "KaliMAD": KALI_MAD}


def makro_intensitas(j):
    gc = j["rasio_gcms_total_SIP_SA"]
    s1 = j["rasio_dR_semua_sensor_SIP_SA"][SENSOR[KOLOM_S1]]
    panas_gc, panas_s1 = nilai_kunci_dipanaskan(gc), nilai_kunci_dipanaskan(s1)
    sensor = j["sensor_rasio_dR_lebih_dari_1_di_semua_jam_dipanaskan"]
    balik = [s for s, r in j["rasio_dR_semua_sensor_SIP_SA"].items()
             if max(nilai_kunci_segar(r)) < 1 and lebih_dari_satu_saat_dipanaskan(r)]
    area = [v for m in j["total_area_gcms"].values() for v in m.values()]
    return {"AreaGCMin": ilmiah(min(area)), "AreaGCMaks": ilmiah(max(area)),
            "NSensorBalik": kata(len(balik)), "SensorBalik": deret(balik),
            "RasioGCNol": rasio(gc["0"]), "RasioGCRentang": rentang(panas_gc, rasio),
            "RasioGCMaksJam": max((v, k) for k, v in gc.items())[1], "RasioSiNol": rasio(s1["0"]),
            "RasioSiRentang": rentang(panas_s1, rasio), "SensorLebihSatu": deret(sensor),
            "NSensorLebihSatu": kata(len(sensor)), "NSensorTidak": kata(len(SENSOR) - len(sensor)),
            "SensorTidak": deret([s for s in SENSOR if s not in sensor]), "JamGC": deret(list(gc)),
            "JamGCPanas": deret(jam_kunci_dipanaskan(gc)),
            "JamTanpaGC": deret([k for k in s1 if k not in gc])}


def tabel_rasio(j):
    jam = list(j["rasio_dR_semua_sensor_SIP_SA"][SENSOR[KOLOM_S1]])
    gc = j["rasio_gcms_total_SIP_SA"]
    baris = ["GC--MS total area & " + " & ".join(rasio(gc[h]) if h in gc else "--" for h in jam) + r" \\ \midrule"]
    for s in SENSOR:
        baris.append(f"$\\Delta R$, {s} & " + " & ".join(rasio(j["rasio_dR_semua_sensor_SIP_SA"][s][h]) for h in jam)
                     + r" \\")
    return {"TabelRasioKepala": " & ".join(jam), "TabelRasio": "\n".join(baris), "NKolomJam": len(jam)}


def makro_korelasi(j):
    s = j["sensor_spearman_tertinggi"]
    pls, kontrol = j["R2_LOO_pls_semua_sensor"], j["kontrol_baseline_R2_LOO_pls_semua_sensor"]
    spear = [v["spearman"] for v in j["sepuluh_titik"].values()]
    lin = j["R2_LOO_linier_total_area"][s]
    return {"NTitikGC": j["jumlah_titik"], "NTitikGCPanas": kata(j["jumlah_titik_dipanaskan"]), "SensorTerbaik": s,
            "PSpearmanTerbaikRel": relasi_p(j["sepuluh_titik"][s]["spearman_p"]),
            "PLSSemua": s3(pls["semua"]), "PLSPanas": s3(pls["dipanaskan"]), "PLSKontrol": s3(kontrol["semua"]),
            "PLSKontrolPanas": s3(kontrol["dipanaskan"]), "SpearmanTerbaik": s3(j["sepuluh_titik"][s]["spearman"]),
            "SpearmanRentang": rentang(spear, s3),
            "LinierTerbaik": s3(lin["semua"]), "LinierTerbaikPanas": s3(lin["dipanaskan"])}


def tabel_korelasi(j):
    baris = []
    for s in SENSOR:
        isi = [s3(j["sepuluh_titik"][s]["spearman"]), s3(j["sepuluh_titik"][s]["pearson"]),
               s3(j["R2_LOO_linier_total_area"][s]["semua"]), s3(j["R2_LOO_linier_total_area"][s]["dipanaskan"]),
               s3(j["kontrol_baseline_R2_LOO_linier_total_area"][s]["semua"])]
        baris.append(f"{s} & " + " & ".join(isi) + r" \\")
    pls, kontrol = j["R2_LOO_pls_semua_sensor"], j["kontrol_baseline_R2_LOO_pls_semua_sensor"]
    baris.append(r"\midrule PLS, S1--S8 & -- & -- & " + f"{s3(pls['semua'])} & {s3(pls['dipanaskan'])} & "
                 f"{s3(kontrol['semua'])}" + r" \\")
    return {"TabelKorelasi": "\n".join(baris)}


def makro_signifikansi(sig):
    uji = {"PPermRocketSesi": sig["E3_minirocket_tinggalkan_sesi"],
           "PPermSlopeSesi": sig["E8_lda_slope_tinggalkan_sesi"], "PPermPLS": sig["E5_pls_semua_sensor_R2_LOO"]}
    makro = {f"{k}Rel": relasi_p(v["p"]) for k, v in uji.items()}
    jumlah = sig["E3_minirocket_tinggalkan_sesi"]["jumlah_permutasi"]
    makro.update({"PPermTerkecil": nilai_p(1 / (jumlah + 1)),
                  "PPermSesiSkema": (f"labels permuted across recordings with the session folds held fixed, "
                                     f"{jumlah} permutations"),
                  "PPermTitikSkema": (f"GC--MS totals permuted across the points with leave-one-out folds held fixed, "
                                      f"{sig['E5_pls_semua_sensor_R2_LOO']['jumlah_permutasi']} permutations")})
    return makro


def makro_segar(j, drift, dinamis):
    rocket = drift["minirocket"]
    cc = drift["koreksi_komponen_5fold"]
    return {"NSegar": j["jumlah_segar"], "NPanas": j["jumlah_dipanaskan"],
            "NBerkasRocket": rocket["kelas_panas"]["berkas"],
            "LDASesiBA": ba(j["lda_tinggalkan_sesi_dR"]), "BaselineSesiBA": ba(j["lda_tinggalkan_sesi_baseline"]),
            "SiSesiBA": ba(j["aturan_S1_tinggalkan_sesi"]), "AmbangSi": mv(j["ambang_S1_mV_seluruh_data"]),
            "RocketSesiBA": ba(rocket["respons_tinggalkan_sesi"]),
            "RocketSesiAcc": acc(rocket["respons_tinggalkan_sesi"]),
            "RocketKontrolBA": ba(rocket["kontrol_pra_sampling_tinggalkan_sesi"]),
            "RocketJedaBA": ba(rocket["respons_tinggalkan_sesi_jeda"]),
            "RocketKontrolJedaBA": ba(rocket["kontrol_pra_sampling_tinggalkan_sesi_jeda"]),
            "CCSesiBA": ba(cc["segar_vs_panas_tinggalkan_sesi"]),
            "VarianPCSatuPersen": persen(cc["varian_pc1_baseline"]),
            "SlopeSesiBA": ba(dinamis["slope_segar_vs_panas_tinggalkan_sesi"]),
            "NSesi": kata(len(drift["sesi"]["sesi"])), "NSesiJeda": len(drift["sesi"]["sesi_jeda"]),
            "TanggalAwal": tanggal(drift["urutan_sesi"][0]["mulai"]),
            "TanggalAkhir": tanggal(drift["urutan_sesi"][-1]["mulai"])}


def tabel_sesi(drift):
    lda = drift["lda_dR_tinggalkan_sesi"]["per_kelompok"]
    rocket = drift["minirocket"]["respons_tinggalkan_sesi"]["per_kelompok"]
    kontrol = drift["minirocket"]["kontrol_pra_sampling_tinggalkan_sesi"]["per_kelompok"]
    berkas = drift["jumlah_berkas"]["sesi"]
    baris = []
    for i, s in enumerate(drift["urutan_sesi"], 1):
        n = sum(v for k, v in berkas.items() if k.startswith(s["sesi"] + " "))
        baris.append(f"{i} & {s['minyak']} & {tanggal(s['mulai'])} & {', '.join(map(str, s['jam']))} & {n} & "
                     f"{s3(lda[s['sesi']])} & {s3(rocket[s['sesi']])} & {s3(kontrol[s['sesi']])}" + r" \\")
    return {"TabelSesi": "\n".join(baris)}


def sesi_terendah(drift):
    kontrol = drift["minirocket"]["kontrol_pra_sampling_tinggalkan_sesi"]["per_kelompok"]
    terendah = min(kontrol, key=kontrol.get)
    urut = [s["sesi"] for s in drift["urutan_sesi"]]
    info = drift["urutan_sesi"][urut.index(terendah)]
    return {"SesiTerendahNo": urut.index(terendah) + 1, "SesiTerendahMinyak": info["minyak"],
            "SesiTerendahTanggal": tanggal(info["mulai"]),
            "SesiTerendahKontrol": s3(kontrol[terendah]),
            "SesiTerendahRocket": s3(drift["minirocket"]["respons_tinggalkan_sesi"]["per_kelompok"][terendah])}


def makro_fitur(j):
    sesi, lima = "segar_panas_tinggalkan_sesi", "segar_panas_5fold"
    hasil = dict(zip(KODE_VARIAN, (j["hasil"][k] for k in VARIAN_E9)))
    banding = [v for v in E9_MENTAH + E9_TANPA_BASELINE if v != E9_ACUAN]
    mentah = {m: [j["hasil"][v][k]["tanpa_seleksi"]["akurasi_seimbang"] for v in E9_MENTAH] for m, k in
              [("Lima", lima), ("Sesi", sesi)]}
    makro = {"NVarian": kata(len(banding)), "NVarianSemua": kata(len(VARIAN_E9)),
             "NVarianMentah": kata(len(E9_MENTAH)),
             "NBerkasFitur": j["berkas"], **{f"FiturMentah{m}Rentang": rentang(v, s3) for m, v in mentah.items()}}
    makro.update({f"Fitur{k}": ba(hasil[k][sesi]["tanpa_seleksi"]) for k in FITUR_LOSO})
    makro.update({f"Fitur{k}Lima": ba(hasil[k][lima]["tanpa_seleksi"]) for k in FITUR_LIMA})
    makro.update({f"Fitur{k}SFS": ba(hasil[k][sesi]["seleksi_sfs"]) for k in FITUR_SFS})
    return makro


def kenaikan(baru, lama):
    return persen((baru - lama) / lama)


def makro_kenaikan(fitur, drift):
    h, sesi = fitur["hasil"], "segar_panas_tinggalkan_sesi"
    nilai = {k: h[v][sesi]["tanpa_seleksi"]["akurasi_seimbang"] for k, v in zip(KODE_VARIAN, VARIAN_E9)}
    rocket = drift["minirocket"]["respons_tinggalkan_sesi"]["akurasi_seimbang"]
    return {"NaikTujuhTiga": kenaikan(nilai["Tujuh"], nilai["Tiga"]),
            "NaikTujuhEmpat": kenaikan(nilai["Tujuh"], nilai["Empat"]),
            "NaikRocketTiga": kenaikan(rocket, nilai["Tiga"]), "NaikRocketEmpat": kenaikan(rocket, nilai["Empat"])}


def tabel_fitur(j):
    baris = []
    for kunci, nama in VARIAN_E9.items():
        isi = j["hasil"][kunci]
        baris.append(f"{nama} & {ba(isi['segar_panas_5fold']['tanpa_seleksi'])} & "
                     f"{ba(isi['segar_panas_tinggalkan_sesi']['tanpa_seleksi'])} & "
                     f"{ba(isi['segar_panas_tinggalkan_sesi']['seleksi_sfs'])}" + r" \\")
    return {"TabelFitur": "\n".join(baris)}


def makro_batas_fase(j):
    makro = {"NBerkasBatas": j["berkas_kuat"], "NBerkasBatasTotal": j["berkas_total"],
             "NBerkasGugur": len(j["berkas_gugur"]), "GugurSegar": teks_gugur(j["berkas_gugur"]),
             "AmbangAmplitudoBatas": j["metode"]["ambang_amplitudo_mV"],
             "JendelaHalusBatas": j["metode"]["jendela_halus"],
             "BaselineBatas": "--".join(map(str, j["metode"]["baris_baseline"])),
             "CariNaikBatas": "--".join(map(str, j["metode"]["cari_naik"])),
             "CariTurunBatas": "--".join(map(str, j["metode"]["cari_turun"]))}
    for metode, akhiran in [("halus", ""), ("mentah", "Mentah")]:
        kurva = j["kurva_median"][metode]
        makro.update({f"KurvaMedian{akhiran}NBerkas": kurva["berkas"],
                      f"KurvaMedian{akhiran}AwalSampling": kurva["awal_sampling"],
                      f"KurvaMedian{akhiran}AwalPurging": kurva["awal_purging"]})
        for fase, nama in [("awal_sampling", "AwalSampling"), ("awal_purging", "AwalPurging")]:
            isi = j["ringkasan"][metode][fase]
            makro.update({f"{nama}{akhiran}Median": detik(isi["kuartil"]["50"]),
                          f"{nama}{akhiran}QSatu": detik(isi["kuartil"]["25"]),
                          f"{nama}{akhiran}QTiga": detik(isi["kuartil"]["75"]),
                          f"{nama}{akhiran}Modus": isi["modus"], f"{nama}{akhiran}NBerkas": isi["berkas"],
                          f"{nama}{akhiran}NModus": isi["frekuensi"][str(isi["modus"])]})
    return makro


def detik(x):
    return tanda(bulat(x, "detik"))


def teks_gugur(gugur):
    segar = sum(not dipanaskan([g["jam"]])[0] for g in gugur)
    return "all fresh" if segar == len(gugur) else f"{kata(segar)} fresh"


def makro_saring(j):
    tersaring = j["minirocket_tinggalkan_sesi"]["dengan_filter"]
    return {"PersenDiganti": persen(j["total_titik_diganti"] / j["total_titik"]),
            "NDiganti": j["total_titik_diganti"], "NTitikTotal": j["total_titik"],
            "NDigantiMADNol": j["total_titik_diganti_di_jendela_mad_nol"],
            "PersenMADNolDariDiganti": persen(j["total_titik_diganti_di_jendela_mad_nol"] / j["total_titik_diganti"]),
            "SaringRocket": ba(tersaring["respons"]), "SaringKontrol": ba(tersaring["kontrol"])}


def tabel_detektor(segar, drift, dinamis, saring):
    kosong = "--"
    rocket, cc = drift["minirocket"], drift["koreksi_komponen_5fold"]
    n, n_rocket, kontrol = segar["jumlah_segar"] + segar["jumlah_dipanaskan"], rocket["kelas_panas"]["berkas"], \
        ba(segar["lda_tinggalkan_sesi_baseline"])
    tersaring = saring["minirocket_tinggalkan_sesi"]["dengan_filter"]
    baris = [("LDA, steady $\\Delta R$ (F4)", n, ba(segar["lda_5fold_dR"]), ba(segar["lda_tinggalkan_sesi_dR"]),
              kontrol),
             ("LDA after component correction", n, ba(cc["segar_vs_panas"]),
              ba(cc["segar_vs_panas_tinggalkan_sesi"]), kontrol),
             ("LDA, rise slope", n, ba(dinamis["slope_segar_vs_panas"]),
              ba(dinamis["slope_segar_vs_panas_tinggalkan_sesi"]), kontrol),
             ("Single-sensor threshold, S1", n, ba(segar["aturan_S1_LOO"]) + "$^{a}$",
              ba(segar["aturan_S1_tinggalkan_sesi"]), kosong),
             ("PhaSeNose detector (MiniRocket)", n_rocket, ba(rocket["respons_5fold"]),
              ba(rocket["respons_tinggalkan_sesi"]), ba(rocket["kontrol_pra_sampling_tinggalkan_sesi"]) + "$^{b}$"),
             ("PhaSeNose detector, filtered signal", n_rocket, kosong, ba(tersaring["respons"]),
              ba(tersaring["kontrol"]) + "$^{b}$")]
    return {"TabelDetektor": "\n".join(" & ".join(map(str, b)) + r" \\" for b in baris)}


def tulis(makro):
    baris = [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in makro.items()]
    KELUARAN.write_text("\n".join(baris) + "\n")


def main():
    segar, drift = baca_json("uji_segar_panas.json"), baca_json("uji_drift.json")
    dinamis, saring = baca_json("uji_dinamis.json"), baca_json("uji_penyaringan.json")
    intensitas, korelasi = baca_json("uji_intensitas.json"), baca_json("uji_korelasi_gcms.json")
    fitur = baca_json("uji_jendela_fitur.json")
    bagian = [makro_inventaris(baca_json("uji_inventaris.json")), makro_jendela(baca_json("uji_jendela_steady.json")),
              makro_model(), makro_versi(), makro_intensitas(intensitas), tabel_rasio(intensitas),
              makro_korelasi(korelasi),
              tabel_korelasi(korelasi), makro_segar(segar, drift, dinamis), tabel_sesi(drift), sesi_terendah(drift),
              makro_fitur(fitur), tabel_fitur(fitur), makro_kenaikan(fitur, drift), makro_saring(saring),
              tabel_detektor(segar, drift, dinamis, saring),
              makro_signifikansi(baca_json("uji_signifikansi.json")),
              makro_batas_fase(baca_json("uji_batas_fase.json"))]
    tulis({k: v for isi in bagian for k, v in isi.items()})


if __name__ == "__main__":
    main()
