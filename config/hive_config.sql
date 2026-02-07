-- ============================================================================
-- Hive Configuration for Mental Health Service Analysis
-- ============================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS mental_health
COMMENT 'Mental health service analysis database'
LOCATION '/user/hive/warehouse/mental_health.db';

USE mental_health;

-- ============================================================================
-- Main Service Records Table
-- ============================================================================

DROP TABLE IF EXISTS service_records;

CREATE EXTERNAL TABLE IF NOT EXISTS service_records (
    student_id STRING COMMENT 'Anonymized student identifier',
    appointment_date DATE COMMENT 'Date of appointment',
    service_type STRING COMMENT 'Type of service received',
    counselor_id STRING COMMENT 'Anonymized counselor identifier',
    duration_minutes INT COMMENT 'Duration of appointment in minutes',
    student_year STRING COMMENT 'Academic year (Freshman, Sophomore, etc.)',
    student_college STRING COMMENT 'Student college/department',
    student_status STRING COMMENT 'Full-time or Part-time',
    international_student BOOLEAN COMMENT 'International student flag',
    first_generation BOOLEAN COMMENT 'First generation student flag',
    referral_source STRING COMMENT 'How student was referred',
    wait_days INT COMMENT 'Days waited for appointment',
    no_show BOOLEAN COMMENT 'Whether student missed appointment',
    follow_up_scheduled BOOLEAN COMMENT 'Whether follow-up was scheduled',
    service_category STRING COMMENT 'Categorized service type',
    visit_number INT COMMENT 'Sequential visit number for student',
    days_since_last_visit INT COMMENT 'Days since previous visit',
    high_risk_indicator BOOLEAN COMMENT 'High-risk pattern flag'
)
PARTITIONED BY (year INT, month INT)
STORED AS PARQUET
LOCATION '/user/hive/warehouse/mental_health.db/service_records'
TBLPROPERTIES ('parquet.compress'='SNAPPY');

-- ============================================================================
-- Demographic Usage Analysis Table
-- ============================================================================

DROP TABLE IF EXISTS demographic_usage;

CREATE TABLE IF NOT EXISTS demographic_usage (
    student_year STRING,
    student_college STRING,
    international_student BOOLEAN,
    first_generation BOOLEAN,
    total_visits BIGINT,
    avg_duration DOUBLE,
    avg_wait_days DOUBLE,
    no_shows BIGINT
)
STORED AS PARQUET
TBLPROPERTIES ('parquet.compress'='SNAPPY');

-- ============================================================================
-- Monthly Trends Table
-- ============================================================================

DROP TABLE IF EXISTS monthly_trends;

CREATE TABLE IF NOT EXISTS monthly_trends (
    year INT,
    month INT,
    service_category STRING,
    visit_count BIGINT,
    avg_wait_days DOUBLE,
    unique_students BIGINT
)
STORED AS PARQUET
TBLPROPERTIES ('parquet.compress'='SNAPPY');

-- ============================================================================
-- Service Gaps Analysis Table
-- ============================================================================

DROP TABLE IF EXISTS service_gaps;

CREATE TABLE IF NOT EXISTS service_gaps (
    service_category STRING,
    student_college STRING,
    demand BIGINT,
    avg_wait DOUBLE,
    extended_wait_count BIGINT
)
STORED AS PARQUET
TBLPROPERTIES ('parquet.compress'='SNAPPY');

-- ============================================================================
-- Counselor Workload Table
-- ============================================================================

DROP TABLE IF EXISTS counselor_workload;

CREATE TABLE IF NOT EXISTS counselor_workload (
    counselor_id STRING,
    year INT,
    month INT,
    appointments BIGINT,
    total_minutes BIGINT,
    unique_students BIGINT
)
STORED AS PARQUET
TBLPROPERTIES ('parquet.compress'='SNAPPY');

-- ============================================================================
-- Student Retention Table
-- ============================================================================

DROP TABLE IF EXISTS student_retention;

CREATE TABLE IF NOT EXISTS student_retention (
    student_id STRING,
    total_visits BIGINT,
    first_visit DATE,
    last_visit DATE,
    avg_visit_frequency DOUBLE
)
STORED AS PARQUET
TBLPROPERTIES ('parquet.compress'='SNAPPY');

-- ============================================================================
-- Create Views for Common Queries
-- ============================================================================

-- High-demand periods view
CREATE OR REPLACE VIEW high_demand_periods AS
SELECT 
    year,
    month,
    service_category,
    visit_count,
    avg_wait_days,
    RANK() OVER (PARTITION BY service_category ORDER BY visit_count DESC) as demand_rank
FROM monthly_trends
ORDER BY visit_count DESC;

-- Underserved demographics view
CREATE OR REPLACE VIEW underserved_demographics AS
SELECT 
    student_year,
    student_college,
    international_student,
    first_generation,
    total_visits,
    avg_wait_days,
    CASE 
        WHEN avg_wait_days > 14 THEN 'Critical'
        WHEN avg_wait_days > 7 THEN 'High'
        ELSE 'Normal'
    END as wait_time_category
FROM demographic_usage
WHERE total_visits > 0
ORDER BY avg_wait_days DESC;

-- Service capacity analysis view
CREATE OR REPLACE VIEW service_capacity_analysis AS
SELECT 
    service_category,
    student_college,
    demand,
    avg_wait,
    extended_wait_count,
    ROUND((extended_wait_count * 100.0 / demand), 2) as pct_extended_wait
FROM service_gaps
WHERE demand > 0
ORDER BY pct_extended_wait DESC;

-- Counselor efficiency view
CREATE OR REPLACE VIEW counselor_efficiency AS
SELECT 
    counselor_id,
    year,
    month,
    appointments,
    unique_students,
    total_minutes,
    ROUND(total_minutes / appointments, 2) as avg_appointment_duration,
    ROUND(appointments * 1.0 / unique_students, 2) as avg_visits_per_student
FROM counselor_workload
ORDER BY appointments DESC;

-- Student engagement patterns view
CREATE OR REPLACE VIEW student_engagement_patterns AS
SELECT 
    CASE 
        WHEN total_visits = 1 THEN 'One-time'
        WHEN total_visits BETWEEN 2 AND 4 THEN 'Occasional'
        WHEN total_visits BETWEEN 5 AND 10 THEN 'Regular'
        ELSE 'Frequent'
    END as engagement_level,
    COUNT(*) as student_count,
    ROUND(AVG(total_visits), 2) as avg_visits,
    ROUND(AVG(avg_visit_frequency), 2) as avg_days_between_visits
FROM student_retention
GROUP BY 
    CASE 
        WHEN total_visits = 1 THEN 'One-time'
        WHEN total_visits BETWEEN 2 AND 4 THEN 'Occasional'
        WHEN total_visits BETWEEN 5 AND 10 THEN 'Regular'
        ELSE 'Frequent'
    END
ORDER BY student_count DESC;

-- ============================================================================
-- Sample Analytical Queries
-- ============================================================================

-- Query 1: Peak usage times by service type
-- SELECT 
--     month,
--     service_category,
--     SUM(visit_count) as total_visits
-- FROM monthly_trends
-- WHERE year = 2023
-- GROUP BY month, service_category
-- ORDER BY total_visits DESC;

-- Query 2: Wait time analysis by demographics
-- SELECT 
--     student_college,
--     AVG(avg_wait_days) as avg_wait,
--     SUM(total_visits) as total_visits
-- FROM demographic_usage
-- GROUP BY student_college
-- HAVING SUM(total_visits) > 100
-- ORDER BY avg_wait DESC;

-- Query 3: Service utilization by international students
-- SELECT 
--     international_student,
--     service_category,
--     COUNT(*) as visits,
--     AVG(wait_days) as avg_wait
-- FROM service_records
-- GROUP BY international_student, service_category
-- ORDER BY visits DESC;

-- ============================================================================
-- Maintenance Scripts
-- ============================================================================

-- Repair partitions (run after loading new data)
-- MSCK REPAIR TABLE service_records;

-- Update table statistics
-- ANALYZE TABLE service_records COMPUTE STATISTICS;
-- ANALYZE TABLE demographic_usage COMPUTE STATISTICS;
-- ANALYZE TABLE monthly_trends COMPUTE STATISTICS;

-- ============================================================================
-- Data Quality Checks
-- ============================================================================

-- Check for NULL values in critical fields
-- SELECT 
--     COUNT(*) as total_records,
--     SUM(CASE WHEN student_id IS NULL THEN 1 ELSE 0 END) as null_student_ids,
--     SUM(CASE WHEN appointment_date IS NULL THEN 1 ELSE 0 END) as null_dates
-- FROM service_records;

-- Check for duplicate records
-- SELECT student_id, appointment_date, service_type, COUNT(*) as cnt
-- FROM service_records
-- GROUP BY student_id, appointment_date, service_type
-- HAVING COUNT(*) > 1;
