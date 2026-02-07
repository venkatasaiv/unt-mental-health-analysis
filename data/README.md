# Data Documentation

## Overview

This directory contains the data used for mental health service analysis. All data is anonymized and de-identified to protect student privacy.

## Directory Structure

```
data/
├── raw/              # Raw, unprocessed data files
├── processed/        # Cleaned and transformed data
└── external/         # External reference data
```

## Data Files

### raw/mental_health_data.csv

Main dataset containing mental health service utilization records.

**Columns:**
- `student_id`: Anonymized student identifier (e.g., STU000001)
- `appointment_date`: Date of service appointment (YYYY-MM-DD)
- `service_type`: Type of mental health service received
- `counselor_id`: Anonymized counselor identifier (e.g., CNS001)
- `duration_minutes`: Length of appointment in minutes
- `student_year`: Academic year (Freshman, Sophomore, Junior, Senior, Graduate)
- `student_college`: Student's college/department
- `student_status`: Enrollment status (Full-time, Part-time)
- `international_student`: Boolean flag for international students
- `first_generation`: Boolean flag for first-generation students
- `referral_source`: How the student was referred to services
- `wait_days`: Number of days waited for appointment
- `no_show`: Boolean flag for missed appointments
- `follow_up_scheduled`: Boolean flag for scheduled follow-up

**Sample Size:** ~20,000 students, ~30,000 appointments

**Time Range:** January 2023 - December 2024

## Service Types

- **Individual Counseling**: One-on-one therapy sessions
- **Crisis Support**: Emergency mental health intervention
- **Group Therapy**: Group-based therapeutic sessions
- **Therapy Session**: General therapeutic services
- **Workshop**: Educational/skill-building sessions
- **Assessment**: Initial evaluation and assessment
- **Follow-up**: Continuation of care appointments

## Student Demographics

### Colleges Represented:
- College of Business
- College of Engineering
- College of Arts and Sciences
- College of Education
- College of Health
- College of Liberal Arts
- College of Music
- College of Visual Arts

### Student Years:
- Freshman (~20%)
- Sophomore (~20%)
- Junior (~20%)
- Senior (~25%)
- Graduate (~15%)

## Referral Sources

- Self-referral (most common)
- Faculty referral
- Academic advisor
- Peer referral
- Health Services
- Residence Life
- Athletics
- Online portal
- Emergency services

## Data Privacy & Ethics

### Privacy Protections:
1. **Anonymization**: All student and counselor IDs are anonymized
2. **No PII**: No personally identifiable information included
3. **Aggregation**: Analysis performed on aggregate data
4. **Compliance**: Adheres to FERPA and HIPAA regulations

### Sample Data:
The data in this repository is **sample/demonstration data** generated for:
- Portfolio presentation
- Analysis methodology demonstration
- Code testing and validation

### Real Data:
Actual analysis was conducted on secure university systems with:
- IRB approval
- Data governance protocols
- Restricted access controls
- Secure computing environment

## Data Quality

### Known Issues:
- ~2% missing values in `duration_minutes` and `wait_days`
- Some duplicate records (cleaned in processing)
- Date range limitations for seasonal analysis

### Data Validation:
- All student_ids are unique per student
- Dates are within valid academic year ranges
- Service types conform to defined categories
- Wait times are within reasonable bounds (0-30 days)

## Usage Guidelines

### Loading Data:

**Python/Pandas:**
```python
import pandas as pd
df = pd.read_csv('data/raw/mental_health_data.csv')
```

**PySpark:**
```python
df = spark.read.csv('data/raw/mental_health_data.csv', header=True, inferSchema=True)
```

**SQL (Hive):**
```sql
LOAD DATA INPATH 'data/raw/mental_health_data.csv'
INTO TABLE mental_health.service_records;
```

### Best Practices:
1. Always check for missing values
2. Validate date ranges
3. Remove duplicates before analysis
4. Use appropriate aggregations
5. Maintain data confidentiality

## Data Updates

This is a static dataset for demonstration purposes. In a production environment:
- Data would be updated nightly/weekly
- Incremental loads would be performed
- Historical data would be archived
- Audit trails would be maintained

## Contact

For questions about the data:
- Check the main README.md
- Review analysis scripts in `src/`
- Open an issue on GitHub

## References

- University Counseling Center documentation
- Mental health service taxonomy
- Academic calendar for seasonal patterns
- Student demographics reports

---

**Note:** This data is for demonstration and portfolio purposes only. It does not represent actual student records.
