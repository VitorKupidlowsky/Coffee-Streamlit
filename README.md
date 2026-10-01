# Coffee-Streamlit: Global *Coffea arabica* Climate Adaptation & Spatial Techno-Economic Explorer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![GCP Cloud Run](https://img.shields.io/badge/Deployed%20on-GCP%20Cloud%20Run-4285F4.svg)](https://cloud.google.com/run)

**Coffee-Streamlit** is an interactive geospatial analytics application designed to translate high-resolution biophysical climate models and techno-economic spatial frameworks into dynamic, actionable risk intelligence. Expanding on master's thesis research (*The Adaptation Premium: A Techno-Economic GIS Spatial Analysis of Global Coffea arabica Competitiveness under Climate Change*), the platform evaluates how climate-induced shifts, hydrological proximity, and infrastructure costs alter the comparative advantage of global coffee-producing regions by 2050.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Core Methodology & Analytical Framework](#core-methodology--analytical-framework)
- [Data Sources](#data-sources)
- [Repository Structure](#repository-structure)
- [Installation & Local Setup](#installation--local-setup)
- [Running the Application](#running-the-application)
- [Docker & Cloud Deployment](#docker--cloud-deployment)
- [Configuration & Environment Variables](#configuration--environment-variables)
- [Academic Citation](#academic-citation)
- [License & Contact](#license--contact)

---

## Overview

Global warming poses a structural threat to the multi-billion-dollar *Coffea arabica* value chain. While artificial irrigation is often considered the primary adaptation mechanism against escalating drought and seasonal variability, its financial and biophysical viability is unevenly distributed across landscapes.

**Coffee-Streamlit** bridges the gap between spatial climatology and financial feasibility. Rather than treating suitability as a static binary classification, this platform simulates infrastructure routing, energy requirements, and localized water stress to calculate an **"Adaptation Premium"**—the localized capital (CAPEX) and operational (OPEX) cost required to maintain viable water supply. Crucially, the tool identifies thresholds where severe heat stress causes capital destruction and leaves assets stranded, regardless of water access.

---

## Key Features

- **Interactive Global & Regional Raster Mapping**: High-performance spatial visualization of continuous suitability scores across major coffee-producing macro-regions (Central & South America, Africa, Asia-Pacific, Oceania).
- **Multi-Scenario Comparison**:
  - **Baseline (2000–2023)**: Historic climatic baseline derived from high-resolution TerraClimate records.
  - **Future Horizon (2050 SSP5-8.5)**: High-warming scenario identifying vulnerable and threatened production zones.
  - **Irrigated Adaptation Intervention**: Simulated infrastructure intervention assessing how much land can be biologically and economically recovered.
- **The Adaptation Premium Calculator**:
  - Evaluates distance to perennial river networks and groundwater aquifers.
  - Accounts for topographical elevation changes (pumping head and energy costs).
  - Integrates regional scarcity multipliers to reflect basin-level competition for water resources.
- **Stranded Asset & Maladaptation Detection**: Highlights zones where extreme temperatures surpass the physiological limits of *Coffea arabica*, preventing maladaptive capital misallocation in unviable irrigation schemes.
- **Export & Reporting Engine**: Dynamic generation of regional summary metrics, tabular shifts ($km^2$), and CSV/GeoTIFF raster data downloads.

---

## Core Methodology & Analytical Framework

1. **Biophysical Suitability Modeling (EcoCrop Framework)**:
   - Evaluates monthly temperature ranges ($T_{min}$, $T_{max}$, $T_{mean}$) and precipitation against physiological crop thresholds.
   - Integrates soil properties (texture, pH, and root-zone depth) into continuous suitability indices ($0.0 \le S \le 1.0$).
2. **Techno-Economic Infrastructure Simulation**:
   - **CAPEX Estimation**: Standardized pipeline capital expenditures calculated via Euclidean and cost-distance routing to nearest surface water (HydroRIVERS) or groundwater wells (Superwell).
   - **OPEX Estimation**: Energy requirements for dynamic head lift ($kWh/m^3$) and localized energy tariffs.
   - **Scarcity Multipliers**: Water stress weighting using WRI Aqueduct basins to penalize extraction in over-allocated catchments.
3. **Transition Typology**:
   - *Stable Suitable*: Viable in both baseline and future scenarios without irrigation.
   - *Irrigation-Recoverable*: Threatened by precipitation deficit but fully restored with irrigation.
   - *Terminal Decline / Stranded Assets*: Suffer fatal heat stress where irrigation fails to preserve yield, leading to capital write-downs.

---

## Data Sources

| Domain | Dataset | Resolution / Coverage | Source |
| :--- | :--- | :--- | :--- |
| **Baseline Climate** | TerraClimate | ~4.6 km ($1/24^\circ$ grid), 2000–2023 | Abatzoglou et al. |
| **Future Projections** | NEX-GDDP-CMIP6 | Downscaled ~25 km, 2050 SSP5-8.5 | Thrasher et al. |
| **Topography** | NASADEM | High-resolution elevation & slope | Crippen et al. |
| **Soil Properties** | SoilGrids v2.0 | Depth, texture classes, pH ($H_2O$) | Poggio et al. |
| **Land Masking** | ESA WorldCover | Urban and permanent water bodies (10 m) | Zanaga et al. |
| **Protected Areas** | WDPA | IUCN Categories I & II polygons | UNEP-WCMC & IUCN |
| **Surface Water** | HydroRIVERS | Global perennial river reach vector lines | Lehner & Grill |
| **Groundwater** | Superwell v1.0 | Aquifer depth and extraction cost estimates | Niazi et al. |
| **Water Stress** | WRI Aqueduct 4.0 | Baseline water stress risk ratings | Hofste et al. |

---

## Repository Structure

```text
├── .streamlit/
│   └── config.toml             # Streamlit theme and server configuration
├── data/
│   ├── raw/                    # Raw geospatial data (not tracked in Git)
│   ├── processed/              # Processed rasters and summary tabular data
│   └── samples/                # Lightweight GeoTIFF/CSV samples for quickstart
├── src/
│   ├── __init__.py
│   ├── config.py               # Constants, default paths, and scenario settings
│   ├── data_loader.py          # Raster and vector ingestion pipelines (Rasterio / GeoPandas)
│   ├── models/
│   │   ├── ecocrop.py          # Biophysical suitability algorithms
│   │   └── techno_economic.py  # CAPEX/OPEX adaptation cost routines
│   ├── utils/
│   │   ├── geo_utils.py        # Spatial masking and reprojection helpers
│   │   └── metrics.py          # Summary aggregation and transition metrics
│   └── visualization/
│       ├── maps.py             # PyDeck, Leafmap, and Folium layer generators
│       └── charts.py           # Plotly interactive breakdown charts
├── app.py                      # Main Streamlit application entry point
├── Dockerfile                  # Production container definition
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment configuration
├── .gitignore
└── README.md
```

---

## Installation & Local Setup

### 1. Prerequisites
- Python 3.10 or higher
- GDAL and PROJ C-libraries (recommended via Conda or system package manager)
- Git LFS (for large raster sample files)

### 2. Clone the Repository
```bash
git clone https://github.com/VitorKupidlowsky/Coffee-Streamlit.git
cd Coffee-Streamlit
```

### 3. Create a Virtual Environment
Using `venv`:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Or using `conda`:
```bash
conda create -n coffee-streamlit python=3.10 gdal rasterio geopandas -c conda-forge
conda activate coffee-streamlit
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Application

To launch the dashboard locally:

```bash
streamlit run app.py
```

The web dashboard will automatically open in your default browser at `http://localhost:8501`.

---

## Docker & Cloud Deployment

### 1. Build and Run via Docker

```bash
# Build the Docker image
docker build -t coffee-streamlit:latest .

# Run the container locally
docker run -p 8501:8501 coffee-streamlit:latest
```

### 2. Deploy to Google Cloud Run

The application is containerized and ready for serverless deployment on Google Cloud Platform:

```bash
# Set project and region
gcloud config set project YOUR_GCP_PROJECT_ID
gcloud config set run/region europe-west4

# Build and submit container image via Cloud Build
gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/coffee-streamlit

# Deploy to Cloud Run
gcloud run deploy coffee-streamlit \
    --image gcr.io/YOUR_GCP_PROJECT_ID/coffee-streamlit \
    --platform managed \
    --memory 2Gi \
    --cpu 2 \
    --allow-unauthenticated
```

---

## Configuration & Environment Variables

Copy `.env.example` to `.env` to configure paths and API credentials:

```bash
cp .env.example .env
```

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATA_DIR` | Local root directory for raster assets | `./data/processed` |
| `GCS_BUCKET_NAME` | Optional GCS bucket for remote raster streaming | `""` |
| `MAPBOX_API_KEY` | Optional Mapbox token for high-res vector tiles | `""` |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`) | `INFO` |

---

## Academic Citation

If you use this model, data transformations, or visualization framework in your research, please cite:

```bibtex
@mastersthesis{kupidlowsky2026adaptation,
  author       = {Vitor Medeiros Kupidlowsky Fernandes},
  title        = {The Adaptation Premium: A Techno-Economic GIS Spatial Analysis of Global Coffea arabica Competitiveness under Climate Change},
  school       = {Rotterdam School of Management, Erasmus University},
  year         = {2026},
  month        = {June},
  type         = {Master's Thesis in Business Analytics and Management}
}
```

---

## License & Contact

- **Author**: Vitor Medeiros Kupidlowsky Fernandes
- **GitHub**: [@VitorKupidlowsky](https://github.com/VitorKupidlowsky)
- **License**: Released under the [MIT License](LICENSE).

