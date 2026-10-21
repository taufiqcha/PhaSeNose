# Electronic nose recordings and headspace GC–MS profiles of two palm cooking oils under repeated heating

Data and code (PhaSeNose) for the article *Screening of repeatedly heated palm
cooking oil using a phase-aware low-cost electronic nose and GC–MS*.

`data/` holds the raw recordings, described in `data/README.md`. Keep both
archives zipped, because the recording sessions are read from the file times
in the zip. `kode/` holds the scripts and `results/` their output; the figure
scripts write to `figures/`. Identifiers in the code are in Indonesian.

Run on macOS with Python 3.11 and the packages in `requirements.txt`. From
`kode/`, run the `uji_*.py` scripts in any order, then `angka_naskah.py`, then
the `gambar_*.py` scripts. The seed is 42.

CC BY 4.0
