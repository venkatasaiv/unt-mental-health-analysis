#!/bin/bash

# Setup script for UNT Mental Health Analysis Project
# This script sets up the development environment and initializes the project

set -e  # Exit on error

echo "============================================================================"
echo "UNT Mental Health Analysis - Setup Script"
echo "============================================================================"

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8+ is required. Found: $python_version"
    exit 1
fi
print_success "Python version: $python_version"

# Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Dependencies installed"

# Create directory structure
print_status "Creating project directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/external
mkdir -p src/data_ingestion
mkdir -p src/processing
mkdir -p src/analysis
mkdir -p src/visualization
mkdir -p notebooks
mkdir -p config
mkdir -p tests
mkdir -p docs
mkdir -p logs
mkdir -p outputs
print_success "Directory structure created"

# Create empty __init__.py files
print_status "Creating Python package structure..."
touch src/__init__.py
touch src/data_ingestion/__init__.py
touch src/processing/__init__.py
touch src/analysis/__init__.py
touch src/visualization/__init__.py
touch tests/__init__.py
print_success "Python packages initialized"

# Generate sample data
print_status "Generating sample data..."
python src/data_generation/generate_sample_data.py
print_success "Sample data generated"

# Check for GCP credentials
print_status "Checking for GCP credentials..."
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    print_warning "GOOGLE_APPLICATION_CREDENTIALS not set"
    echo "To use GCP features, set this environment variable:"
    echo "export GOOGLE_APPLICATION_CREDENTIALS='/path/to/credentials.json'"
else
    print_success "GCP credentials configured"
fi

# Setup Git (if not already initialized)
if [ ! -d ".git" ]; then
    print_status "Initializing Git repository..."
    git init
    
    # Create .gitignore
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb_checkpoints/

# Data files
data/raw/*.csv
data/processed/*.csv
*.parquet
*.db

# Credentials
*.json
credentials/
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Distribution
dist/
build/
*.egg-info/

# GCP
.gcloudignore

# Temporary files
tmp/
temp/
*.tmp
EOF
    
    git add .
    git commit -m "Initial commit: Mental Health Analysis Project"
    print_success "Git repository initialized"
else
    print_warning "Git repository already exists"
fi

# Create environment template
print_status "Creating environment configuration template..."
cat > .env.example << 'EOF'
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=your-bucket-name
GCP_REGION=us-central1

# BigQuery
BIGQUERY_DATASET=mental_health

# Data paths
RAW_DATA_PATH=gs://your-bucket/raw
PROCESSED_DATA_PATH=gs://your-bucket/processed

# Spark Configuration
SPARK_MASTER=local[*]
SPARK_EXECUTOR_MEMORY=4g
SPARK_DRIVER_MEMORY=2g
EOF
print_success "Environment template created"

# Print completion message
echo ""
echo "============================================================================"
print_success "Setup Complete!"
echo "============================================================================"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Copy .env.example to .env and configure your settings"
echo "3. Set up GCP credentials if using Google Cloud Platform"
echo "4. Review the README.md for detailed usage instructions"
echo ""
echo "To run the analysis:"
echo "  - Generate sample data: python src/data_generation/generate_sample_data.py"
echo "  - Run Spark ETL: spark-submit src/processing/spark_etl.py"
echo "  - Run gap analysis: python src/analysis/service_gap_analysis.py"
echo ""
print_success "Happy analyzing!"
echo "============================================================================"
