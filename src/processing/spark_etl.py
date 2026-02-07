"""
Spark ETL Pipeline for Mental Health Service Analysis
Processes raw data, performs transformations, and prepares for analysis
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, sum, when, datediff, 
    to_date, year, month, dayofweek, hour,
    dense_rank, row_number, lag
)
from pyspark.sql.window import Window
from pyspark.sql.types import *
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MentalHealthETL:
    """ETL Pipeline for Mental Health Service Data"""
    
    def __init__(self, app_name="MentalHealthAnalysis"):
        """Initialize Spark session with optimized configurations"""
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
            .enableHiveSupport() \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark session initialized successfully")
    
    def extract_data(self, gcs_path):
        """
        Extract data from GCS bucket
        
        Args:
            gcs_path (str): GCS path to raw data
            
        Returns:
            DataFrame: Raw data
        """
        logger.info(f"Extracting data from {gcs_path}")
        
        # Define schema for better performance
        schema = StructType([
            StructField("student_id", StringType(), True),
            StructField("appointment_date", DateType(), True),
            StructField("service_type", StringType(), True),
            StructField("counselor_id", StringType(), True),
            StructField("duration_minutes", IntegerType(), True),
            StructField("student_year", StringType(), True),
            StructField("student_college", StringType(), True),
            StructField("student_status", StringType(), True),
            StructField("international_student", BooleanType(), True),
            StructField("first_generation", BooleanType(), True),
            StructField("referral_source", StringType(), True),
            StructField("wait_days", IntegerType(), True),
            StructField("no_show", BooleanType(), True),
            StructField("follow_up_scheduled", BooleanType(), True)
        ])
        
        df = self.spark.read \
            .option("header", "true") \
            .schema(schema) \
            .csv(gcs_path)
        
        logger.info(f"Extracted {df.count()} records")
        return df
    
    def transform_data(self, df):
        """
        Apply transformations to clean and enrich data
        
        Args:
            df (DataFrame): Raw data
            
        Returns:
            DataFrame: Transformed data
        """
        logger.info("Starting data transformations")
        
        # Data quality checks and cleaning
        df_clean = df.filter(col("student_id").isNotNull()) \
                    .filter(col("appointment_date").isNotNull()) \
                    .dropDuplicates(["student_id", "appointment_date", "service_type"])
        
        # Add temporal features
        df_enriched = df_clean \
            .withColumn("year", year(col("appointment_date"))) \
            .withColumn("month", month(col("appointment_date"))) \
            .withColumn("day_of_week", dayofweek(col("appointment_date"))) \
            .withColumn("is_weekend", when(col("day_of_week").isin([1, 7]), True).otherwise(False))
        
        # Categorize service types
        df_enriched = df_enriched.withColumn(
            "service_category",
            when(col("service_type").isin(["Individual Counseling", "Therapy Session"]), "Counseling")
            .when(col("service_type").isin(["Crisis Support", "Emergency"]), "Crisis")
            .when(col("service_type").isin(["Group Therapy", "Workshop"]), "Group")
            .otherwise("Other")
        )
        
        # Calculate student engagement metrics
        window_spec = Window.partitionBy("student_id").orderBy("appointment_date")
        
        df_enriched = df_enriched \
            .withColumn("visit_number", row_number().over(window_spec)) \
            .withColumn("prev_visit_date", lag("appointment_date").over(window_spec)) \
            .withColumn(
                "days_since_last_visit",
                when(col("prev_visit_date").isNotNull(),
                     datediff(col("appointment_date"), col("prev_visit_date")))
                .otherwise(None)
            )
        
        # Flag high-risk patterns
        df_enriched = df_enriched.withColumn(
            "high_risk_indicator",
            when((col("wait_days") > 14) | 
                 (col("service_category") == "Crisis") |
                 (col("no_show") == True), True)
            .otherwise(False)
        )
        
        logger.info(f"Transformations complete. Records: {df_enriched.count()}")
        return df_enriched
    
    def create_aggregate_views(self, df):
        """
        Create aggregated views for analysis
        
        Args:
            df (DataFrame): Transformed data
            
        Returns:
            dict: Dictionary of aggregated DataFrames
        """
        logger.info("Creating aggregate views")
        
        aggregates = {}
        
        # Service utilization by demographics
        aggregates['demographic_usage'] = df.groupBy(
            "student_year", "student_college", "international_student", "first_generation"
        ).agg(
            count("*").alias("total_visits"),
            avg("duration_minutes").alias("avg_duration"),
            avg("wait_days").alias("avg_wait_days"),
            sum(when(col("no_show"), 1).otherwise(0)).alias("no_shows")
        )
        
        # Monthly trends
        aggregates['monthly_trends'] = df.groupBy("year", "month", "service_category").agg(
            count("*").alias("visit_count"),
            avg("wait_days").alias("avg_wait_days"),
            countDistinct("student_id").alias("unique_students")
        ).orderBy("year", "month")
        
        # Service gaps analysis
        aggregates['service_gaps'] = df.groupBy("service_category", "student_college").agg(
            count("*").alias("demand"),
            avg("wait_days").alias("avg_wait"),
            sum(when(col("wait_days") > 7, 1).otherwise(0)).alias("extended_wait_count")
        )
        
        # Counselor workload
        aggregates['counselor_workload'] = df.groupBy("counselor_id", "year", "month").agg(
            count("*").alias("appointments"),
            sum("duration_minutes").alias("total_minutes"),
            countDistinct("student_id").alias("unique_students")
        )
        
        # Student retention
        aggregates['student_retention'] = df.groupBy("student_id").agg(
            count("*").alias("total_visits"),
            min("appointment_date").alias("first_visit"),
            max("appointment_date").alias("last_visit"),
            avg("days_since_last_visit").alias("avg_visit_frequency")
        )
        
        logger.info(f"Created {len(aggregates)} aggregate views")
        return aggregates
    
    def load_to_hive(self, df, table_name, partition_by=None):
        """
        Load data to Hive table
        
        Args:
            df (DataFrame): Data to load
            table_name (str): Target table name
            partition_by (list): Columns to partition by
        """
        logger.info(f"Loading data to Hive table: {table_name}")
        
        if partition_by:
            df.write \
                .mode("overwrite") \
                .partitionBy(*partition_by) \
                .saveAsTable(f"mental_health.{table_name}")
        else:
            df.write \
                .mode("overwrite") \
                .saveAsTable(f"mental_health.{table_name}")
        
        logger.info(f"Successfully loaded to {table_name}")
    
    def save_to_gcs(self, df, gcs_path, format="parquet"):
        """
        Save DataFrame to GCS
        
        Args:
            df (DataFrame): Data to save
            gcs_path (str): GCS destination path
            format (str): Output format (parquet, csv, etc.)
        """
        logger.info(f"Saving data to {gcs_path}")
        
        df.write \
            .mode("overwrite") \
            .format(format) \
            .save(gcs_path)
        
        logger.info(f"Data saved successfully")
    
    def run_pipeline(self, input_path, output_path):
        """
        Execute complete ETL pipeline
        
        Args:
            input_path (str): GCS path to raw data
            output_path (str): GCS path for processed data
        """
        logger.info("=" * 80)
        logger.info("Starting Mental Health ETL Pipeline")
        logger.info("=" * 80)
        
        # Extract
        raw_df = self.extract_data(input_path)
        
        # Transform
        transformed_df = self.transform_data(raw_df)
        
        # Create aggregates
        aggregates = self.create_aggregate_views(transformed_df)
        
        # Load to Hive
        self.load_to_hive(transformed_df, "service_records", partition_by=["year", "month"])
        
        for name, agg_df in aggregates.items():
            self.load_to_hive(agg_df, name)
        
        # Save to GCS
        self.save_to_gcs(transformed_df, f"{output_path}/service_records")
        
        for name, agg_df in aggregates.items():
            self.save_to_gcs(agg_df, f"{output_path}/aggregates/{name}")
        
        # Generate summary statistics
        self.print_summary(transformed_df)
        
        logger.info("=" * 80)
        logger.info("ETL Pipeline Completed Successfully")
        logger.info("=" * 80)
    
    def print_summary(self, df):
        """Print summary statistics"""
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY STATISTICS")
        logger.info("=" * 80)
        
        total_records = df.count()
        unique_students = df.select("student_id").distinct().count()
        
        logger.info(f"Total Records: {total_records:,}")
        logger.info(f"Unique Students: {unique_students:,}")
        logger.info(f"Date Range: {df.agg({'appointment_date': 'min'}).collect()[0][0]} to {df.agg({'appointment_date': 'max'}).collect()[0][0]}")
        
        logger.info("\nService Category Distribution:")
        df.groupBy("service_category").count().orderBy(col("count").desc()).show()
        
        logger.info("=" * 80 + "\n")
    
    def stop(self):
        """Stop Spark session"""
        self.spark.stop()
        logger.info("Spark session stopped")


def main():
    """Main execution function"""
    # Configuration
    INPUT_PATH = "gs://your-bucket/raw/mental_health_data.csv"
    OUTPUT_PATH = "gs://your-bucket/processed"
    
    # Initialize and run ETL
    etl = MentalHealthETL()
    
    try:
        etl.run_pipeline(INPUT_PATH, OUTPUT_PATH)
    except Exception as e:
        logger.error(f"ETL Pipeline failed: {str(e)}", exc_info=True)
        raise
    finally:
        etl.stop()


if __name__ == "__main__":
    main()
