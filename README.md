# UNT Mental Health Services Analysis

**Analyzing mental health service usage patterns for 20,000+ University of North Texas students using Python, PySpark, and Google Cloud Platform — findings contributed to a 10% increase in resource allocation.**

---

## Overview

Mental health services at universities are chronically under-resourced, but the gap between demand and supply is rarely measured rigorously. This project uses big data tools to analyze service utilization patterns, identify which student groups are underserved, and produce actionable recommendations backed by data.

The analysis was presented to 5+ UNT stakeholders including the Dean of Students Office, University Counseling Center, and Student Health Services, and directly contributed to a **10% increase in mental health resource allocation**.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.8+ |
| Big Data Processing | Apache Spark 3.x (PySpark), Apache Hive 3.x |
| Cloud Platform | Google Cloud Platform — Cloud Storage, Dataproc, BigQuery |
| Data Analysis | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn, Plotly |
| Orchestration | Apache Airflow |
| Environment | Jupyter Notebook |

---

## Repository Structure

```
unt-mental-health-analysis/
├── config/
│   ├── hive_config.sql         # Hive table definitions
│   ├── spark_config.yaml       # Spark job configuration
│   └── gcp_config.yaml         # GCP project settings
├── data/
│   ├── raw/                    # Raw anonymized data (samples only)
│   └── processed/              # Cleaned and transformed datasets
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_service_gap_analysis.ipynb
│   └── 03_trend_analysis.ipynb
├── src/
│   ├── data_ingestion/         # GCP Cloud Storage upload scripts
│   ├── processing/             # PySpark ETL jobs
│   ├── analysis/               # Gap analysis and trend scripts
│   └── visualization/          # Chart and report generation
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── QUICKSTART.md
├── PROJECT_SUMMARY.md
├── requirements.txt
└── setup.sh
```

---

## Data Pipeline

```
Raw Data → GCP Cloud Storage → Hive Data Warehouse → PySpark Processing → Analysis & Visualization
```

Data is ingested to GCP Cloud Storage, catalogued in Hive tables via Dataproc, processed with PySpark for ETL and aggregation, and analyzed in Python/Jupyter for gap identification and reporting.

---

## Key Findings

- **Service availability gap**: Limited evening and weekend hours left a significant portion of student demand unmet
- **Underserved populations**: International students and graduate students showed the highest unmet demand relative to enrollment
- **Wait time issue**: Average time to first appointment exceeded recommended benchmarks
- **Awareness gap**: A substantial share of students were unaware of available services
- **Recommendation implemented**: Extended counseling hours during peak periods resulted in measurably higher utilization

---

## How to Run

### Prerequisites
- Python 3.8+
- Apache Spark 3.0+
- Google Cloud SDK (for full pipeline)

### Setup

```bash
git clone https://github.com/venkatasaiv/unt-mental-health-analysis.git
cd unt-mental-health-analysis

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
bash setup.sh
```

### Run locally (without GCP)

Open the notebooks in order:
```
notebooks/01_exploratory_analysis.ipynb
notebooks/02_service_gap_analysis.ipynb
notebooks/03_trend_analysis.ipynb
```

### Run with GCP

```bash
# Configure credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# Upload data to Cloud Storage
python src/data_ingestion/upload_to_gcs.py --bucket your-bucket-name

# Create Hive tables
hive -f config/hive_config.sql

# Run Spark ETL
spark-submit src/processing/spark_etl.py
```

---

## Data Privacy

All data used in this project is anonymized and de-identified. No personally identifiable information (PII) is included. The analysis was conducted in compliance with FERPA. Sample data in this repository is provided for demonstration only.

---

## Author

**Venkatasai Vudatha** — Data Analyst & ML Engineer  
📧 Vudatha.sai@gmail.com  
🔗 [linkedin.com/in/venkatasaivudatha04](https://www.linkedin.com/in/venkatasaivudatha04/)  
📍 Dallas, TX

---

## License

MIT License — see [LICENSE](LICENSE) for details.
