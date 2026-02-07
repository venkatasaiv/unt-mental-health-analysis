# Quick Start Guide

## Getting Started in 5 Minutes

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/unt-mental-health-analysis.git
cd unt-mental-health-analysis
bash setup.sh
```

### 2. Activate Environment
```bash
source venv/bin/activate
```

### 3. Generate Sample Data
```bash
python src/data_generation/generate_sample_data.py
```

### 4. Run Analysis
```bash
# Option A: Run gap analysis
python src/analysis/service_gap_analysis.py

# Option B: Create visualizations
python src/visualization/create_dashboards.py

# Option C: Explore in Jupyter
jupyter notebook notebooks/01_exploratory_analysis.ipynb
```

## Common Use Cases

### Use Case 1: Quick Data Overview
```python
import pandas as pd
df = pd.read_csv('data/raw/mental_health_data.csv')
print(df.info())
print(df.describe())
```

### Use Case 2: Generate Visualizations
```bash
python src/visualization/create_dashboards.py
# Check outputs/visualizations/ for HTML dashboards
```

### Use Case 3: Run Spark Processing (requires Spark installation)
```bash
spark-submit src/processing/spark_etl.py
```

### Use Case 4: Upload to GCP (requires GCP credentials)
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
python src/data_ingestion/upload_to_gcs.py \
  --project-id your-project-id \
  --bucket your-bucket-name \
  --source data/raw/mental_health_data.csv \
  --destination raw/mental_health_data.csv
```

## Project Structure Overview

```
unt-mental-health-analysis/
│
├── data/                          # Data files
│   ├── raw/                       # Raw CSV data
│   └── processed/                 # Processed outputs
│
├── src/                           # Source code
│   ├── data_ingestion/           # GCP upload scripts
│   ├── processing/               # Spark ETL pipeline
│   ├── analysis/                 # Analysis scripts
│   └── visualization/            # Dashboard creation
│
├── notebooks/                     # Jupyter notebooks
│   └── 01_exploratory_analysis.ipynb
│
├── config/                        # Configuration files
│   └── hive_config.sql           # Hive table definitions
│
├── outputs/                       # Generated outputs
│   └── visualizations/           # HTML dashboards
│
└── README.md                      # Main documentation
```

## Key Files

| File | Purpose |
|------|---------|
| `setup.sh` | One-command environment setup |
| `src/data_generation/generate_sample_data.py` | Generate demo data |
| `src/processing/spark_etl.py` | Main Spark ETL pipeline |
| `src/analysis/service_gap_analysis.py` | Identify service gaps |
| `src/visualization/create_dashboards.py` | Create visualizations |
| `config/hive_config.sql` | Hive table schemas |

## Troubleshooting

### Issue: Python dependencies fail to install
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: GCP authentication fails
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
gcloud auth application-default login
```

### Issue: Spark not found
```bash
# Install Spark (macOS with Homebrew)
brew install apache-spark

# Or download from https://spark.apache.org/downloads.html
```

### Issue: Jupyter kernel not found
```bash
python -m ipykernel install --user --name venv --display-name "Python (venv)"
```

## Next Steps

1. **Customize the Analysis**: Modify SQL queries in `config/hive_config.sql`
2. **Add New Visualizations**: Extend `src/visualization/create_dashboards.py`
3. **Integrate with Your Data**: Replace sample data with your actual data
4. **Deploy to Production**: Set up automated pipelines with Airflow
5. **Share Results**: Export dashboards and present findings

## Resources

- [Main README](README.md) - Comprehensive documentation
- [Data Dictionary](data/README.md) - Data field descriptions
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## Support

- Open an issue on GitHub
- Check existing documentation
- Review code comments

Happy analyzing! 🎓📊
