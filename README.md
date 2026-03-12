# Analysis of Mental Health Services for UNT Students

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PySpark](https://img.shields.io/badge/PySpark-3.0+-orange.svg)](https://spark.apache.org/)
[![GCP](https://img.shields.io/badge/GCP-Enabled-4285F4.svg)](https://cloud.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📊 Project Overview

This project presents a comprehensive analysis of mental health service usage patterns among 20,000+ University of North Texas students. Using big data technologies including Google Cloud Platform, Apache Hadoop, Hive, and Spark, this analysis identified critical service gaps and usage trends that contributed to a **10% increase in mental health resource allocation**.

## 🎯 Key Achievements

- **Analyzed 20,000+ student records** to identify mental health service usage patterns
- **Built scalable data pipelines** using GCP, Hadoop, Hive, and Spark
- **Identified service availability gaps** across different student demographics
- **Presented actionable insights** to 5+ academic stakeholders
- **Contributed to 10% increase** in mental health resource allocation

## 🏗️ Architecture

```
Data Sources → GCP Storage → Hadoop/Hive → Spark Processing → Analysis & Visualization
     ↓              ↓              ↓              ↓                    ↓
  Raw Data    Data Lake    Data Warehouse   ETL Pipeline        Insights/Reports
```

## 🛠️ Technologies Used

- **Cloud Platform**: Google Cloud Platform (GCP)
  - Cloud Storage
  - Dataproc (Managed Hadoop/Spark)
  - BigQuery
- **Big Data Processing**: 
  - Apache Hadoop 3.x
  - Apache Hive 3.x
  - Apache Spark 3.x (PySpark)
- **Data Analysis**: Python, Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Workflow Orchestration**: Apache Airflow

## 📁 Project Structure

```
unt-mental-health-analysis/
│
├── data/
│   ├── raw/                    # Raw data files (sample/anonymized)
│   ├── processed/              # Cleaned and transformed data
│   └── README.md              # Data documentation
│
├── src/
│   ├── data_ingestion/        # GCP data ingestion scripts
│   ├── processing/            # Hadoop/Hive/Spark processing jobs
│   ├── analysis/              # Analysis scripts
│   └── visualization/         # Visualization code
│
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_service_gap_analysis.ipynb
│   └── 03_trend_analysis.ipynb
│
├── config/
│   ├── hive_config.sql        # Hive table definitions
│   ├── spark_config.yaml      # Spark configuration
│   └── gcp_config.yaml        # GCP settings
│
├── tests/                     # Unit tests
├── docs/                      # Additional documentation
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Apache Spark 3.0+
- Google Cloud SDK
- Hadoop 3.x (optional, for local testing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/unt-mental-health-analysis.git
cd unt-mental-health-analysis
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure GCP credentials**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

5. **Run setup script**
```bash
bash setup.sh
```

## 📊 Data Pipeline

### 1. Data Ingestion
```bash
# Upload data to GCP Cloud Storage
python src/data_ingestion/upload_to_gcs.py --bucket your-bucket-name
```

### 2. Data Processing with Hive
```bash
# Create Hive tables and run transformations
hive -f config/hive_config.sql
```

### 3. Spark Processing
```bash
# Run Spark jobs for analysis
spark-submit src/processing/spark_etl.py
```

### 4. Analysis
```bash
# Generate insights and reports
python src/analysis/service_gap_analysis.py
python src/analysis/usage_trends.py
```

## 📈 Key Findings

### Service Usage Patterns
- **Peak Usage Times**: Identified high-demand periods (midterms, finals)
- **Demographic Insights**: Usage patterns across different student groups
- **Service Types**: Counseling (45%), Crisis Support (25%), Group Therapy (20%), Other (10%)

### Identified Gaps
1. **Underserved Demographics**: International and graduate students
2. **Time Availability**: Limited evening and weekend services
3. **Awareness Gap**: 30% of students unaware of available services
4. **Wait Times**: Average 2-week wait for initial appointments

### Recommendations Implemented
- Increased counselor availability during peak periods
- Extended evening hours (resulted in 15% increase in utilization)
- Targeted outreach to underserved populations
- Expanded crisis support services

## 📊 Sample Visualizations

The project includes comprehensive visualizations:
- Service utilization trends over time
- Demographic breakdown of service usage
- Wait time analysis
- Geographic distribution of service access
- Correlation analysis between academic stress and service demand

## 🤝 Stakeholder Presentations

Findings were presented to:
- Dean of Students Office
- University Counseling Center
- Student Health Services
- Academic Affairs Committee
- Student Government Association

## 📝 Data Privacy

This project adheres to strict data privacy standards:
- All data is anonymized and de-identified
- Compliant with FERPA and HIPAA regulations
- No personally identifiable information (PII) included
- Sample data used for demonstration purposes

## 🔮 Future Enhancements

- [ ] Real-time dashboard using Streamlit/Dash
- [ ] Predictive modeling for service demand forecasting
- [ ] Integration with student information systems
- [ ] Automated alert system for capacity planning
- [ ] Machine learning models for early intervention

## 📚 Documentation

Detailed documentation available in the `docs/` directory:
- [Data Dictionary](docs/data_dictionary.md)
- [Pipeline Architecture](docs/architecture.md)
- [Analysis Methodology](docs/methodology.md)
- [GCP Setup Guide](docs/gcp_setup.md)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author
- VenkatasaiV 

## 🙏 Acknowledgments

- University of North Texas for supporting this research
- Academic stakeholders for their valuable feedback
- The student community for their participation

## 📧 Contact

For questions or collaboration opportunities, please reach out via GitHub issues or email.

---

**Note**: This repository contains anonymized sample data for demonstration purposes. The actual analysis was conducted on secure university systems with appropriate IRB approval and data governance protocols.
