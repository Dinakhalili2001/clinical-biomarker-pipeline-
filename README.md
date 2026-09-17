# Clinical Biomarker & Remote Monitoring Analytics Pipeline

A small Python portfolio project bridging **clinical/lab biomarker analysis**
and **digital health / remote patient monitoring** — the intersection of
wet-lab immunoassay work and the kind of data pipelines used by digital
health platforms.

Built while learning Python, informed by hands-on experience processing
human clinical plasma samples and running ELISA-based immunoassays
(NETs, cell-free DNA, thrombo-inflammatory biomarkers) across patient
cohorts.

## Why this project

Digital health platforms (remote patient monitoring, decentralized
clinical trials, companion diagnostics) depend on pipelines that turn
raw measurements — whether a lab assay reading or a wearable sensor
reading — into clean, flagged, decision-ready data. This project
demonstrates that pattern in two related contexts:

1. **`elisa_pipeline/`** — turns raw ELISA optical density readings into
   blank-corrected, dilution-adjusted biomarker concentrations, handles
   multiple assay plates correctly (each with its own standard curve),
   flags out-of-range readings, and compares pre- vs. post-treatment
   levels per patient.

2. **`wearable_dashboard/`** — simulates and visualizes daily wearable
   vitals data (heart rate, step count) over time, and includes a basic
   deterioration-style alert (flags sustained elevated heart rate over
   several consecutive days) — the same underlying logic used in remote
   patient monitoring deterioration alerts.

## Skills demonstrated

- Data wrangling and analysis with `pandas` / `numpy`
- Statistical curve fitting (`scipy.stats.linregress`) applied to a real
  assay calibration problem
- Time-series handling and trend visualization (`matplotlib`)
- Translating a real clinical/lab protocol (with input from wet-lab
  experience) into correct, well-documented, reusable code
- Data validation logic (flagging unreliable/out-of-range values rather
  than reporting them silently)

## Project structure

```
clinical-biomarker-pipeline/
├── elisa_pipeline/
│   └── nets_elisa_pipeline.py
├── wearable_dashboard/
│   └── wearable_dashboard.py
├── sample_data/
│   ├── standards_data.csv
│   └── samples_data.csv
├── requirements.txt
└── README.md
```

## How to run

```bash
pip install -r requirements.txt

cd elisa_pipeline
python nets_elisa_pipeline.py

cd ../wearable_dashboard
python wearable_dashboard.py
```

## Data note

All data included here is either anonymized/illustrative (ELISA sample
data) or synthetically generated (wearable data) for demonstration
purposes — no identifiable patient data is included in this repository.

## Background

This project reflects direct experience in a clinical research setting:
processing and analyzing human clinical plasma samples, executing
ELISA-based immunoassays to quantify NETs, cell-free DNA, and
thrombo-inflammatory biomarkers across multiple patient cohorts.

## Next steps

- [ ] Deploy as an interactive Streamlit web app
- [ ] Add automated tests
- [ ] Add SQL-based data storage instead of CSV files
# clinical-biomarker-pipeline-
