# Trace Fitbit

Visualizes GPS hiking traces from Fitbit devices as static maps and compiles them into a PDF report.

Each hike is rendered as a map image showing the GPS route on an OpenStreetMap background, annotated with the starting locality, date, total distance, and duration. All maps are assembled into a single PDF with a table of contents and an alphabetical locality index with page numbers.

## Requirements

### Python packages

```
geopandas shapely reverse_geocoder pandas matplotlib contextily
```

### External tool

- [Typst](https://typst.app) — to compile the PDF report

## Installation

```bash
git clone https://github.com/your-username/Trace_fitbit.git
cd Trace_fitbit
conda create -n fitbit313 python=3.13
conda activate fitbit313
pip install geopandas shapely reverse_geocoder pandas matplotlib contextily
```

## Data

Place your Fitbit GPS export files (CSV files named `gps_location_YYYY-MM-DD.csv`) in a folder under `data/`. Update the `DATA_RAW_PATH` constant in `src/trace.py` to point to that folder.

Each CSV must have columns: `timestamp`, `latitude`, `longitude`, `altitude`.

**Note:** GPS data is not included in this repository (private activity records).

## Usage

**Step 1 — Generate map images and summary CSV:**

```bash
python src/trace.py
```

Outputs PNG map images to `data/images/` and writes `data/images/images_recap.csv`.

**Step 2 — Compile the PDF report:**

```bash
typst compile data/generate_pdf.typ data/randonnees.pdf
```

## Project structure

```
Trace_fitbit/
├── src/
│   ├── trace.py          # Main pipeline: GPS CSV → map images + summary CSV
│   └── test_trace.py     # Diagnostic script to regenerate specific traces
├── data/
│   ├── generate_pdf.typ  # Typst template for the PDF report
│   └── images/           # Generated map images and images_recap.csv (not tracked)
├── .gitignore
├── LICENSE
└── README.md
```

## Notes

Some GPS recordings are excluded from the pipeline: they correspond to sessions where the device was tracking while stationary rather than during an actual hike. The excluded dates are listed in `EXCLUDED_DATES` in `src/trace.py`.

## Licence

MIT — see [LICENSE](LICENSE).
