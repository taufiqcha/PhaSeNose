# Electronic nose recordings and headspace GC–MS profiles of two palm cooking oils under repeated heating

PhaSeNose repository: https://github.com/taufiqcha/PhaSeNose

Data and code for *Screening of repeatedly heated palm cooking oil using a phase-aware low-cost electronic nose and GC–MS*.

Premium (SA) and economy (SIP) palm cooking oils were heated for 5 min at 200 °C once per hour up to 60 h and recorded by an eight-sensor metal oxide electronic nose in three phases (conditioning, sampling, purging), with ten samples profiled by headspace GC–MS. The code derives the steady window, computes phase-aware features, compares the electronic-nose response with the GC–MS total volatile area, and validates fresh-versus-heated detectors by leaving one recording session out against a pre-sampling air control. `results/` holds every computed result reported in the paper. Identifiers in the code are in Indonesian.

## Data

The raw data are in `data/`, so the code runs without a separate download. `data/README.md` describes the design, file formats, GC–MS protocol, archive structure, and anomalies. The code reads the two archives as they are:

- `01_raw_enose.zip`: 70 headerless `.xlsx` sheets named `<oil>_<level>-<replicate>.xlsx` (SA or SIP; level 0–60 h in steps of 10, the number of hourly heating cycles; replicates 1–5; one file is `SIP_60-5_.xlsx`), each 240 rows (one per second; `SA_20-1.xlsx` has 148) by 8 columns (S1–S8, mV). Recording sessions come from the file times stored in the zip, so the archive must stay zipped.
- `02_raw_gcms.zip`: `raw_gcms/cookingoilITS.pdf`, the compound table (retention time, compound, CAS number, and peak area for each sample), and ten chromatograms `raw_gcms/SA/SA 0.pdf` to `raw_gcms/SIP/SIP 60.pdf`, whose headers give the acquisition date and the extraction method. The Author entry of the PDF document information is blanked; every other byte is as received from the laboratory.

Four scripts read the GC–MS archive: `uji_inventaris.py`, `uji_intensitas.py`, `uji_korelasi_gcms.py`, and `uji_signifikansi.py`. Their outputs are in `results/`, so `angka_naskah.py` and the figure scripts run without it.

## Run

Python 3.11. Each analysis script reads `data/` by default and also accepts another data folder as its argument.

```bash
pip install -r requirements.txt
cd kode
python3 uji_inventaris.py
python3 uji_jendela_steady.py
python3 uji_batas_fase.py
python3 uji_intensitas.py
python3 uji_korelasi_gcms.py
python3 uji_segar_panas.py
python3 uji_dinamis.py
python3 uji_drift.py
python3 uji_jendela_fitur.py
python3 uji_penyaringan.py
python3 uji_signifikansi.py
python3 angka_naskah.py
python3 gambar_sinyal.py
python3 gambar_gcms.py
python3 gambar_validasi.py
```

The seed is 42 throughout. `uji_signifikansi.py` runs for several minutes; the other scripts take under a minute each.

## Scripts

| Script | Result file | Paper |
|---|---|---|
| `uji_inventaris.py` | `uji_inventaris.json` | Sections 2.1–2.2, record counts and GC–MS extraction |
| `uji_jendela_steady.py` | `uji_jendela_steady.json` | Sections 2.3–2.4 and 3.3, steady window and median S1 curve |
| `uji_batas_fase.py` | `uji_batas_fase.json` | Section 2.3, checks the fixed phase-boundary constants against the raw and smoothed signals |
| `uji_intensitas.py` | `uji_intensitas.json` | Sections 2.2 and 3.1, Table 2 |
| `uji_korelasi_gcms.py` | `uji_korelasi_gcms.json` | Section 3.2, Table 3, Fig. 3 |
| `uji_segar_panas.py` | `uji_segar_panas.json` | Section 3.4, Table 5 (LDA, S1 threshold) |
| `uji_dinamis.py` | `uji_dinamis.json` | Sections 3.3–3.4, Table 5 (rise slope) |
| `uji_drift.py` | `uji_drift.json` | Section 3.4, Tables 5–6 (component correction, MiniRocket, sessions) |
| `uji_jendela_fitur.py` | `uji_jendela_fitur.json` | Section 3.3, Table 4 |
| `uji_penyaringan.py` | `uji_penyaringan.json` | Section 3.4, Table 5 (filtered signal) |
| `uji_signifikansi.py` | `uji_signifikansi.json` | Abstract and Sections 3.2–3.4, permutation tests |
| `angka_naskah.py` | `angka.tex` | LaTeX macros that place the computed results in the paper |
| `gambar_sinyal.py` | `figures/gambar_sinyal.pdf` | Fig. 2 |
| `gambar_gcms.py` | `figures/gambar_gcms.pdf` | Fig. 3 |
| `gambar_validasi.py` | `figures/gambar_validasi.pdf` | Fig. 4 (values from `angka.tex`) |

`data.py` holds the paths, data loaders, row windows, and phase features; `model.py` holds the models and validation folds; `gaya_gambar.py` holds the figure style. Fig. 1 is the draw.io diagram `diagram/gambar_alur.drawio`, exported to PDF from draw.io.

## License

The code is released under the MIT License (see `LICENSE`). The data in `data/` are released under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence, https://creativecommons.org/licenses/by/4.0/ (see `data/README.md`).
