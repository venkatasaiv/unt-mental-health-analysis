"""
GCP Data Ingestion Module
Upload and manage data in Google Cloud Storage
"""

from google.cloud import storage
from google.cloud import bigquery
import os
import logging
from pathlib import Path
from typing import List, Optional
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GCPDataIngestion:
    """Handle data ingestion to Google Cloud Platform"""
    
    def __init__(self, project_id: str, bucket_name: str):
        """
        Initialize GCP clients
        
        Args:
            project_id: GCP project ID
            bucket_name: GCS bucket name
        """
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(project=project_id)
        self.bigquery_client = bigquery.Client(project=project_id)
        
        logger.info(f"Initialized GCP clients for project: {project_id}")
        logger.info(f"Using bucket: {bucket_name}")
    
    def create_bucket_if_not_exists(self, location: str = "US"):
        """
        Create GCS bucket if it doesn't exist
        
        Args:
            location: Bucket location
        """
        try:
            bucket = self.storage_client.get_bucket(self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} already exists")
        except Exception:
            bucket = self.storage_client.create_bucket(
                self.bucket_name,
                location=location
            )
            logger.info(f"Created bucket {self.bucket_name} in {location}")
        
        return bucket
    
    def upload_file(
        self, 
        source_file_path: str, 
        destination_blob_name: str
    ) -> str:
        """
        Upload a file to GCS
        
        Args:
            source_file_path: Local file path
            destination_blob_name: Destination path in GCS
            
        Returns:
            GCS URI of uploaded file
        """
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        logger.info(f"Uploading {source_file_path} to gs://{self.bucket_name}/{destination_blob_name}")
        
        blob.upload_from_filename(source_file_path)
        
        gcs_uri = f"gs://{self.bucket_name}/{destination_blob_name}"
        logger.info(f"Upload complete: {gcs_uri}")
        
        return gcs_uri
    
    def upload_directory(
        self, 
        source_dir: str, 
        destination_prefix: str = ""
    ) -> List[str]:
        """
        Upload entire directory to GCS
        
        Args:
            source_dir: Local directory path
            destination_prefix: Prefix for GCS paths
            
        Returns:
            List of GCS URIs
        """
        uploaded_files = []
        source_path = Path(source_dir)
        
        logger.info(f"Uploading directory {source_dir} to GCS")
        
        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_path)
                destination_blob = f"{destination_prefix}/{relative_path}".lstrip('/')
                
                gcs_uri = self.upload_file(str(file_path), destination_blob)
                uploaded_files.append(gcs_uri)
        
        logger.info(f"Uploaded {len(uploaded_files)} files")
        return uploaded_files
    
    def download_file(
        self, 
        source_blob_name: str, 
        destination_file_path: str
    ):
        """
        Download a file from GCS
        
        Args:
            source_blob_name: Source path in GCS
            destination_file_path: Local destination path
        """
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(source_blob_name)
        
        logger.info(f"Downloading gs://{self.bucket_name}/{source_blob_name} to {destination_file_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)
        
        blob.download_to_filename(destination_file_path)
        logger.info("Download complete")
    
    def list_blobs(self, prefix: Optional[str] = None) -> List[str]:
        """
        List all blobs in bucket with optional prefix
        
        Args:
            prefix: Optional prefix to filter blobs
            
        Returns:
            List of blob names
        """
        bucket = self.storage_client.bucket(self.bucket_name)
        blobs = list(bucket.list_blobs(prefix=prefix))
        
        blob_names = [blob.name for blob in blobs]
        logger.info(f"Found {len(blob_names)} blobs with prefix '{prefix}'")
        
        return blob_names
    
    def create_bigquery_dataset(
        self, 
        dataset_id: str, 
        location: str = "US"
    ):
        """
        Create BigQuery dataset if it doesn't exist
        
        Args:
            dataset_id: Dataset ID
            location: Dataset location
        """
        dataset_ref = f"{self.project_id}.{dataset_id}"
        
        try:
            self.bigquery_client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_ref} already exists")
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = location
            dataset = self.bigquery_client.create_dataset(dataset)
            logger.info(f"Created dataset {dataset_ref}")
    
    def load_gcs_to_bigquery(
        self,
        gcs_uri: str,
        dataset_id: str,
        table_id: str,
        schema: Optional[List[bigquery.SchemaField]] = None,
        write_disposition: str = "WRITE_TRUNCATE"
    ):
        """
        Load data from GCS to BigQuery
        
        Args:
            gcs_uri: GCS URI of source file
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            schema: Table schema (optional)
            write_disposition: Write disposition
        """
        table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True if schema is None else False,
            write_disposition=write_disposition,
        )
        
        if schema:
            job_config.schema = schema
        
        logger.info(f"Loading {gcs_uri} to {table_ref}")
        
        load_job = self.bigquery_client.load_table_from_uri(
            gcs_uri,
            table_ref,
            job_config=job_config
        )
        
        load_job.result()  # Wait for job to complete
        
        logger.info(f"Loaded {load_job.output_rows} rows to {table_ref}")
    
    def create_external_table(
        self,
        gcs_uri: str,
        dataset_id: str,
        table_id: str,
        schema: List[bigquery.SchemaField]
    ):
        """
        Create external table pointing to GCS data
        
        Args:
            gcs_uri: GCS URI pattern (can include wildcards)
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            schema: Table schema
        """
        table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
        
        external_config = bigquery.ExternalConfig("CSV")
        external_config.source_uris = [gcs_uri]
        external_config.options.skip_leading_rows = 1
        external_config.schema = schema
        
        table = bigquery.Table(table_ref, schema=schema)
        table.external_data_configuration = external_config
        
        table = self.bigquery_client.create_table(table)
        logger.info(f"Created external table {table_ref}")
    
    def setup_data_pipeline(self, config_file: str):
        """
        Setup complete data pipeline from configuration
        
        Args:
            config_file: Path to YAML configuration file
        """
        logger.info("Setting up data pipeline from configuration")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Create bucket
        self.create_bucket_if_not_exists(
            location=config.get('bucket_location', 'US')
        )
        
        # Upload data files
        if 'upload_files' in config:
            for upload in config['upload_files']:
                self.upload_file(
                    upload['source'],
                    upload['destination']
                )
        
        # Create BigQuery dataset
        if 'bigquery_dataset' in config:
            self.create_bigquery_dataset(
                config['bigquery_dataset'],
                location=config.get('dataset_location', 'US')
            )
        
        # Load tables
        if 'tables' in config:
            for table in config['tables']:
                self.load_gcs_to_bigquery(
                    table['gcs_uri'],
                    config['bigquery_dataset'],
                    table['table_id']
                )
        
        logger.info("Data pipeline setup complete")


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload data to GCP')
    parser.add_argument('--project-id', required=True, help='GCP project ID')
    parser.add_argument('--bucket', required=True, help='GCS bucket name')
    parser.add_argument('--source', required=True, help='Source file or directory')
    parser.add_argument('--destination', required=True, help='Destination path in GCS')
    parser.add_argument('--is-directory', action='store_true', help='Source is a directory')
    
    args = parser.parse_args()
    
    # Initialize ingestion
    ingestion = GCPDataIngestion(args.project_id, args.bucket)
    
    # Create bucket if needed
    ingestion.create_bucket_if_not_exists()
    
    # Upload data
    if args.is_directory:
        ingestion.upload_directory(args.source, args.destination)
    else:
        ingestion.upload_file(args.source, args.destination)
    
    logger.info("Data ingestion complete!")


if __name__ == "__main__":
    main()
