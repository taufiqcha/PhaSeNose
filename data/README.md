# Electronic nose recordings and headspace GC–MS profiles of two palm cooking oils under repeated heating

Raw recordings of an eight-sensor metal-oxide electronic nose sampling the headspace of two
packaged palm cooking oils, fresh and after repeated heating, together with the
headspace GC–MS profiles of 10 of the oil samples.

This folder holds the raw data analysed by the code in `../kode/`. The code
reads both archives as they are, so keep them zipped and keep their names.

## What this folder contains

| File | Contents |
|---|---|
| `01_raw_enose.zip` | Raw electronic-nose recordings, 70 xlsx files |
| `02_raw_gcms.zip` | Headspace GC–MS reports, 11 PDF files: one compound table and 10 chromatograms |
| `README.md` | This description |

The archives are numbered to keep the reading order clear. Unzipping a copy of
`01_raw_enose.zip` gives `raw_enose/`, and a copy of `02_raw_gcms.zip` gives `raw_gcms/`.

## Experimental design

Two packaged palm cooking oils of one producer, bought at the same supermarket in Surabaya, Indonesia:

1. `SA`, the premium grade
2. `SIP`, the economy grade

- Each oil was heated for 5 min at 200 °C once per hour and then left to stand until the next hour
- The heating level counts the hourly heating cycles, with levels of 0, 10, 20, 30, 40, 50, and 60 h; level 0 h is fresh oil
- 5 replicates per oil and level
- For each recording, 150 mL of oil in a beaker was warmed to 80 °C on a temperature-controlled electric stove, and its headspace was drawn into the sensor chamber
- Both oils at levels 0, 20, 40, 50, and 60 h were also profiled by headspace GC–MS, one chromatogram per sample; levels 10 and 30 h were not

Instrument:

- 8 metal-oxide (MOS) gas sensors of the TGS and MQ series, labelled S1 to S8. The sensor model of each channel is not available
- A Raspberry minicomputer acquired the sensor voltages in millivolts (mV), one row per second
- The instrument also carried a temperature-humidity sensor, but its readings are not in these files

## Electronic-nose file format

- One sheet (`Sheet1`) per file, no header row, 8 columns, 240 rows
- Columns 1 to 8 hold S1 to S8 in that order, in mV, as whole numbers
- Row r, counted from 0, is second r of the recording and spreadsheet row r + 1
- File name `<oil>_<level>-<replicate>.xlsx`, with the level in h; `SA_0-1.xlsx` is oil SA, level 0 h, replicate 1
- No temperature, humidity, or time-stamp column is present

## Three phases

Every recording passes through three phases. The row boundaries are fixed
windows used by the analysis, the same for every recording. They were checked
against the sum of S1 and S8 rather than detected from each file.

| Phase | Rows | Air in the sensor chamber |
|---|---|---|
| Conditioning | 0–32 | Ambient room air |
| Sampling | 33–158 | Headspace of the warmed oil |
| Purging | 159–239 | Ambient room air |

## Archive structure inside 01_raw_enose.zip

```
raw_enose/SA/SA_<level>-<replicate>.xlsx
raw_enose/SIP/SIP_<level>-<replicate>.xlsx
```

Each file keeps its original name, its original bytes, and the modification
time stored in the original export, from 30 December 2023 to 20 January 2024.
These times can be used to group the recordings into measurement sessions.

## How the electronic-nose file count adds up

2 oils times 7 heating levels times 5 replicates gives 70 recordings,
35 for SA and 35 for SIP. All 70 files differ in content.

## Electronic-nose anomalies

- `SA_20-1.xlsx` holds only 148 rows (rows 0–147), so it ends during the sampling phase. It is supplied as recorded.
- `SIP_60-5_.xlsx` carries an extra underscore before the extension. It holds oil SIP, level 60 h, replicate 5; the name is kept as recorded.
- The original export also held 7 `.ods` copies of recordings already present as `.xlsx` with the same name and the same values. The `.ods` copies are not included.

## Headspace GC–MS

Both oils at levels 0, 20, 40, 50, and 60 h were analyzed by headspace solid-phase microextraction (HS-SPME) GC–MS, giving 10 samples with one chromatogram per sample. The analysis was carried out at the Flavor Analysis Laboratory, Balai Besar Pengujian Standar Instrumen Padi (BBPSI Padi, Indonesian Center for Rice Standard Instrument Testing), Ministry of Agriculture, Sukamandi, Subang, Indonesia. For each sample, 15 mL of oil was placed in a 22 mL SPME vial. Volatiles were extracted with a 2 cm DVB/CAR/PDMS fiber at 80 °C for 45 min. Separation used an Agilent 7890A gas chromatograph with an HP-5MS column (30 m × 250 µm × 0.25 µm). The injector operated at 250 °C in splitless mode, with helium as the carrier gas at 0.8 mL/min. The oven was held at 40 °C for 5 min, raised at 4 °C/min to 240 °C, and held for 5 min. Detection used an Agilent 5975C XL EI/CI mass spectrometer with a Triple-Axis Detector, scanning m/z 29–550. The interface was kept at 250 °C, the ion source at 230 °C, and the quadrupole at 150 °C. Compounds were identified against the NIST14 library.

Between the GC–MS analysis and the electronic-nose recordings, the samples were kept at room temperature, 25–30 °C.

## GC–MS files

- `cookingoilITS.pdf` is the compound table issued by the laboratory, 39 pages with the columns Sample, RT (min), Compound, CAS, and Area. It lists 1379 peaks over 10 samples, 88 to 148 per sample. Area is the integrated peak area in arbitrary units
- `<oil> <level>.pdf`, with the level in h, is the one-page total ion chromatogram of one sample. Its header gives the acquisition date, from 24 October 2023 to 27 October 2023, and the extraction note `extract at 80C 45mnt DVB/CAR/PDMS 2cm`

## Archive structure inside 02_raw_gcms.zip

```
raw_gcms/cookingoilITS.pdf
raw_gcms/SA/SA <level>.pdf
raw_gcms/SIP/SIP <level>.pdf
```

Each file keeps its original name and its original bytes, except that the
Author entry of the PDF document information is blanked: the name is replaced
by spaces of the same length, so the page content and every other byte stay as
received. The modification time stored in the archive,
11 October 2026, is the date of the source archive from which the files were taken, not the date of measurement. The laboratory created the PDF reports on
9 January 2024 (CreationDate in the PDF metadata), and the chromatograms were acquired from 24 October 2023 to 27 October 2023.

## How the GC–MS file count adds up

2 oils times 5 heating levels give 10 chromatograms; with the compound table this makes 11 files. All 11 files differ in content.

## GC–MS anomalies

- The header of `SA 60.pdf` gives the sample name as `A 60 5MS 15ml`. The file is supplied as recorded.
- In the compound table, `4-Nonenal, (E)-` appears twice at different retention times within each of 9 samples: SA 0, SA 20, SA 40, SA 50, SA 60, SIP 20, SIP 40, SIP 50, and SIP 60.
- In the compound table, `Furan, 2,3-dihydro-4-methyl-` appears twice at different retention times within each of 7 samples: SA 20, SA 40, SA 50, SIP 20, SIP 40, SIP 50, and SIP 60.

## Processing

None. No cleaning, filtering, baseline correction, resampling, or removal of
recordings was applied. The GC–MS files are the PDF reports as received from
the laboratory, with only the Author entry of the document information blanked.

## Licence

The data in this folder are released under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence,
https://creativecommons.org/licenses/by/4.0/. The code of this repository is released under the MIT
License in `../LICENSE`. When you use the data, please cite this repository,
https://github.com/taufiqcha/PhaSeNose, as given in `../CITATION.cff`.
