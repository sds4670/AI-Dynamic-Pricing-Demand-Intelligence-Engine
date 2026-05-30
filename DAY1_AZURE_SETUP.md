# Day 1: Azure Blob Storage Setup & Python Integration

**Goal:** Set up Azure Blob Storage, connect it from Python, and upload/download your first dataset.

---

## 📋 What We're Building Today

```
┌─────────────────────────────────────────────────┐
│  Your Local Machine                             │
│  ┌──────────────────────────────────────────┐   │
│  │ Python Script (pricing_engine)           │   │
│  │ ├── Load CSV locally                     │   │
│  │ └── Connect to Azure Blob Storage ←──┐   │   │
│  └──────────────────────────────────────┼───┘   │
└─────────────────────────────────────────┼───────┘
                                          │
                          ┌───────────────▼──────────┐
                          │  Azure Blob Storage      │
                          │  Container:              │
                          │  ├── raw/                │
                          │  │   ├── olist.csv       │
                          │  │   ├── flipkart.csv    │
                          │  │   └── amazon.csv      │
                          │  └── processed/          │
                          └──────────────────────────┘
```

By end of Day 1:
- ✅ Azure Storage Account created
- ✅ Container with folders set up  
- ✅ Python client authenticated
- ✅ Upload/download working
- ✅ Code ready for production use

---

## 🎯 Step 1: Create Azure Storage Account

### Option A: Using Azure Portal (GUI)

1. Go to [Azure Portal](https://portal.azure.com/)
2. Click **Create a resource** → Search "Storage account"
3. Fill form:
   - **Resource Group**: Create new → `pricing-engine-rg`
   - **Storage Account Name**: `pricingenginedata` (must be globally unique, lowercase)
   - **Region**: Select closest to your users (e.g., `Southeast Asia` for India)
   - **Performance**: Standard
   - **Replication**: Locally-redundant storage (LRS) - cheapest for dev

4. Click **Review + Create** → **Create**

5. Wait 1-2 minutes for deployment to complete

6. Go to resource → **Access Keys** → Copy:
   - Storage account name
   - Key 1 (access key)

### Option B: Using Azure CLI (Faster)

```bash
# Login to Azure
az login

# Create resource group
az group create \
  --name pricing-engine-rg \
  --location southeastasia

# Create storage account
az storage account create \
  --name pricingenginedata \
  --resource-group pricing-engine-rg \
  --location southeastasia \
  --sku Standard_LRS

# Get access keys
az storage account keys list \
  --name pricingenginedata \
  --resource-group pricing-engine-rg
```

**⚠️ Save this info:**
```
Storage Account Name: pricingenginedata
Access Key 1: [your-key-here]
```

---

## 🔧 Step 2: Set Up Python Environment

### 1. Create Virtual Environment

```bash
# Navigate to project
cd /workspaces/AI-Dynamic-Pricing-Demand-Intelligence-Engine

# Create venv
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify
python --version  # Should be 3.9+
```

### 2. Install Azure SDK

```bash
# Install Azure Storage Blob SDK
pip install azure-storage-blob==12.18.0

# Verify installation
python -c "import azure.storage.blob; print('✓ Azure SDK installed')"
```

---

## 🌐 Step 3: Create Container & Folder Structure

### Create Python Script: `setup_blob_storage.py`

```python
"""
setup_blob_storage.py
Sets up Azure Blob Storage containers and folders for pricing engine
Run this ONCE to initialize storage
"""

from azure.storage.blob import BlobServiceClient, ContainerClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure credentials
ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT", "pricingenginedata")
ACCOUNT_KEY = os.getenv("AZURE_STORAGE_KEY")

def setup_blob_storage():
    """Create containers and folder structure in Azure Blob Storage."""
    
    if not ACCOUNT_KEY:
        raise ValueError("❌ AZURE_STORAGE_KEY not found in environment variables!")
    
    # Create connection string
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={ACCOUNT_NAME};"
        f"AccountKey={ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    
    # Initialize Blob Service Client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    print(f"✓ Connected to storage account: {ACCOUNT_NAME}")
    
    # Define containers and their folder structure
    containers_config = {
        "pricing-engine-data": {
            "folders": ["raw", "processed", "delta", "models", "logs"]
        }
    }
    
    # Create containers and folders
    for container_name, config in containers_config.items():
        try:
            # Create container
            container_client = blob_service_client.create_container(name=container_name)
            print(f"✓ Created container: {container_name}")
        except Exception as e:
            # Container might already exist
            print(f"⚠ Container '{container_name}' already exists or error: {e}")
            container_client = blob_service_client.get_container_client(container_name)
        
        # Create folder structure by uploading empty blobs
        for folder in config["folders"]:
            folder_blob_name = f"{folder}/.gitkeep"
            try:
                container_client.upload_blob(
                    name=folder_blob_name,
                    data=b"",  # Empty file to create folder
                    overwrite=True
                )
                print(f"  ├── Created folder: {folder}/")
            except Exception as e:
                print(f"  └── Error creating folder {folder}: {e}")
    
    print("\n✅ Azure Blob Storage initialized successfully!")
    print("\nFolder structure created:")
    print("""
    pricing-engine-data/
    ├── raw/              (raw CSV datasets)
    ├── processed/        (cleaned data after PySpark)
    ├── delta/            (Delta Lake tables)
    ├── models/           (trained model artifacts)
    └── logs/             (processing logs)
    """)

if __name__ == "__main__":
    setup_blob_storage()
```

### Run the Setup Script

```bash
# Make sure .env is configured (next step)
python setup_blob_storage.py
```

Expected output:
```
✓ Connected to storage account: pricingenginedata
✓ Created container: pricing-engine-data
  ├── Created folder: raw/
  ├── Created folder: processed/
  ├── Created folder: delta/
  ├── Created folder: models/
  └── Created folder: logs/

✅ Azure Blob Storage initialized successfully!
```

---

## 🔐 Step 4: Configure Environment Variables

### 1. Create `.env` File

```bash
# From project root
cp .env.example .env
nano .env  # or use your editor
```

### 2. Add Azure Credentials

Edit `.env`:

```env
# ===== Azure Storage =====
AZURE_STORAGE_ACCOUNT=pricingenginedata
AZURE_STORAGE_KEY=your_access_key_here

# ===== Application =====
ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

**⚠️ SECURITY:**
- Never commit `.env` to Git
- `.env` is already in `.gitignore`
- Rotate keys every 90 days in production

### 3. Verify

```bash
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
account = os.getenv('AZURE_STORAGE_ACCOUNT')
key = os.getenv('AZURE_STORAGE_KEY')
print(f'✓ Account: {account}')
print(f'✓ Key: {key[:20]}...' if key else '✗ Key missing')
"
```

---

## ⬆️ Step 5: Upload Your First Dataset

### Create Upload Script: `upload_sample_data.py`

```python
"""
upload_sample_data.py
Uploads sample CSV files to Azure Blob Storage
"""

from azure.storage.blob import BlobServiceClient
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT")
ACCOUNT_KEY = os.getenv("AZURE_STORAGE_KEY")
CONTAINER_NAME = "pricing-engine-data"

def upload_file_to_blob(local_file_path: str, blob_path: str):
    """Upload a file to Azure Blob Storage."""
    
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={ACCOUNT_NAME};"
        f"AccountKey={ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    # Check if file exists locally
    if not Path(local_file_path).exists():
        print(f"❌ File not found: {local_file_path}")
        return False
    
    # Upload file
    with open(local_file_path, "rb") as data:
        try:
            container_client.upload_blob(blob_path, data, overwrite=True)
            print(f"✓ Uploaded: {local_file_path} → {blob_path}")
            return True
        except Exception as e:
            print(f"❌ Error uploading {local_file_path}: {e}")
            return False

def create_sample_csv():
    """Create a sample CSV for testing."""
    
    sample_data = """date,product_id,price,quantity,category
2024-01-01,P001,299.99,45,Electronics
2024-01-01,P002,499.99,28,Electronics
2024-01-01,P003,99.99,156,Home
2024-01-02,P001,299.99,52,Electronics
2024-01-02,P002,449.99,31,Electronics
2024-01-02,P003,99.99,142,Home
2024-01-03,P001,279.99,67,Electronics
2024-01-03,P002,499.99,24,Electronics
2024-01-03,P003,109.99,168,Home
2024-01-04,P001,299.99,48,Electronics
2024-01-04,P002,479.99,35,Electronics
2024-01-04,P003,99.99,151,Home
"""
    
    # Create sample data directory
    Path("sample_data").mkdir(exist_ok=True)
    
    # Write sample CSV
    sample_file = "sample_data/sample_sales.csv"
    with open(sample_file, "w") as f:
        f.write(sample_data)
    
    print(f"✓ Created sample CSV: {sample_file}")
    return sample_file

def main():
    """Upload sample data to Azure."""
    
    print("🚀 Starting upload to Azure Blob Storage...\n")
    
    # Create sample data
    sample_file = create_sample_csv()
    
    # Upload to Azure
    success = upload_file_to_blob(
        local_file_path=sample_file,
        blob_path="raw/sample_sales.csv"
    )
    
    if success:
        print("\n✅ Upload successful!")
        print(f"File available at: https://{ACCOUNT_NAME}.blob.core.windows.net/pricing-engine-data/raw/sample_sales.csv")
    else:
        print("\n❌ Upload failed!")

if __name__ == "__main__":
    main()
```

### Run Upload

```bash
python upload_sample_data.py
```

Expected output:
```
🚀 Starting upload to Azure Blob Storage...

✓ Created sample CSV: sample_data/sample_sales.csv
✓ Uploaded: sample_data/sample_sales.csv → raw/sample_sales.csv

✅ Upload successful!
File available at: https://pricingenginedata.blob.core.windows.net/pricing-engine-data/raw/sample_sales.csv
```

---

## ⬇️ Step 6: Download & Verify Data

### Create Download Script: `download_blob_data.py`

```python
"""
download_blob_data.py
Downloads files from Azure Blob Storage and verifies them
"""

from azure.storage.blob import BlobServiceClient
import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT")
ACCOUNT_KEY = os.getenv("AZURE_STORAGE_KEY")
CONTAINER_NAME = "pricing-engine-data"

def download_file_from_blob(blob_path: str, local_file_path: str):
    """Download a file from Azure Blob Storage."""
    
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={ACCOUNT_NAME};"
        f"AccountKey={ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Create downloads directory
    Path(local_file_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Download file
    try:
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=blob_path
        )
        
        with open(local_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        print(f"✓ Downloaded: {blob_path} → {local_file_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading {blob_path}: {e}")
        return False

def list_blobs_in_container():
    """List all blobs in the container."""
    
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={ACCOUNT_NAME};"
        f"AccountKey={ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    print(f"\n📁 Files in container '{CONTAINER_NAME}':\n")
    
    blobs = container_client.list_blobs()
    for blob in blobs:
        if blob.name != ".gitkeep":  # Skip empty folder markers
            size_kb = blob.size / 1024 if blob.size else 0
            print(f"  ├── {blob.name} ({size_kb:.1f} KB)")

def verify_csv_data(file_path: str):
    """Verify and display CSV data."""
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        df = pd.read_csv(file_path)
        
        print(f"\n📊 CSV Data Preview ({file_path}):\n")
        print(df.head(10).to_string())
        print(f"\n📈 Summary:")
        print(f"  ├── Rows: {len(df)}")
        print(f"  ├── Columns: {len(df.columns)}")
        print(f"  └── Columns: {', '.join(df.columns)}")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

def main():
    """Download and verify blob data."""
    
    print("📥 Starting download from Azure Blob Storage...\n")
    
    # List available files
    list_blobs_in_container()
    
    # Download sample file
    print("\n📥 Downloading file...\n")
    success = download_file_from_blob(
        blob_path="raw/sample_sales.csv",
        local_file_path="downloads/sample_sales.csv"
    )
    
    if success:
        # Verify the data
        verify_csv_data("downloads/sample_sales.csv")
        print("\n✅ Download and verification successful!")
    else:
        print("\n❌ Download failed!")

if __name__ == "__main__":
    main()
```

### Run Download

```bash
python download_blob_data.py
```

Expected output:
```
📥 Starting download from Azure Blob Storage...

📁 Files in container 'pricing-engine-data':

  ├── raw/sample_sales.csv (2.5 KB)

📥 Downloading file...

✓ Downloaded: raw/sample_sales.csv → downloads/sample_sales.csv

📊 CSV Data Preview (downloads/sample_sales.csv):

         date product_id   price  quantity     category
0  2024-01-01       P001  299.99        45  Electronics
1  2024-01-01       P002  499.99        28  Electronics
...

📈 Summary:
  ├── Rows: 12
  ├── Columns: 5
  └── Columns: date, product_id, price, quantity, category

✅ Download and verification successful!
```

---

## 🔄 Step 7: Create Reusable Azure Client Class

Update `src/utils/azure_clients.py` with this production-ready version:

This file already exists with our `AzureStorageClient` class. Let's create a test for it:

```python
"""
test_azure_storage.py
Tests Azure Blob Storage connectivity and operations
"""

import pytest
import os
from pathlib import Path
from dotenv import load_dotenv
from src.utils.azure_clients import AzureStorageClient

load_dotenv()

class TestAzureStorageClient:
    """Test Azure Storage operations."""
    
    @pytest.fixture
    def storage_client(self):
        """Initialize storage client."""
        return AzureStorageClient(
            container_name="pricing-engine-data"
        )
    
    def test_connection(self, storage_client):
        """Test storage account connection."""
        assert storage_client.account_name is not None
        print(f"✓ Connected to: {storage_client.account_name}")
    
    def test_list_blobs(self, storage_client):
        """Test listing blobs."""
        blobs = storage_client.list_blobs("raw/")
        print(f"✓ Found {len(blobs)} blobs in raw/")
        assert isinstance(blobs, list)
    
    def test_upload_download(self, storage_client):
        """Test file upload and download."""
        
        # Create test file
        test_file = "test_data.txt"
        with open(test_file, "w") as f:
            f.write("Test data for Azure Blob Storage")
        
        # Upload
        blob_url = storage_client.upload_file(
            local_path=test_file,
            blob_path="raw/test_data.txt"
        )
        print(f"✓ Uploaded: {blob_url}")
        
        # Verify exists
        exists = storage_client.blob_exists("raw/test_data.txt")
        assert exists
        print(f"✓ Verified blob exists")
        
        # Download
        downloaded_file = "downloads/test_data_downloaded.txt"
        storage_client.download_file(
            blob_path="raw/test_data.txt",
            local_path=downloaded_file
        )
        
        # Verify content
        with open(downloaded_file, "r") as f:
            content = f.read()
        assert content == "Test data for Azure Blob Storage"
        print(f"✓ Downloaded and verified")
        
        # Cleanup
        storage_client.delete_blob("raw/test_data.txt")
        Path(test_file).unlink()
        print(f"✓ Cleanup complete")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
```

Run the test:

```bash
pytest tests/test_azure_storage.py -v -s
```

---

## ✅ Step 8: Verification Checklist

Run this to verify everything is working:

```bash
python -c "
import os
from dotenv import load_dotenv
from src.utils.azure_clients import AzureStorageClient
import pandas as pd

print('🔍 Day 1 Verification Checklist\n')

# 1. Environment
load_dotenv()
account = os.getenv('AZURE_STORAGE_ACCOUNT')
key = os.getenv('AZURE_STORAGE_KEY')
print(f'✅ 1. Environment variables: Account={account}, Key={\"*\" * 10}...')

# 2. Azure Connection
try:
    client = AzureStorageClient()
    print(f'✅ 2. Azure connection successful')
except Exception as e:
    print(f'❌ 2. Azure connection failed: {e}')

# 3. List blobs
try:
    blobs = client.list_blobs('raw/')
    print(f'✅ 3. Blob listing: {len(blobs)} files found')
except Exception as e:
    print(f'❌ 3. Blob listing failed: {e}')

# 4. Download test
try:
    client.download_file('raw/sample_sales.csv', '/tmp/test.csv')
    df = pd.read_csv('/tmp/test.csv')
    print(f'✅ 4. Download and read CSV: {len(df)} rows')
except Exception as e:
    print(f'❌ 4. Download failed: {e}')

print('\\n✅ Day 1 Complete! Ready for Day 2')
"
```

Expected output:
```
🔍 Day 1 Verification Checklist

✅ 1. Environment variables: Account=pricingenginedata, Key=**********...
✅ 2. Azure connection successful
✅ 3. Blob listing: 1 files found
✅ 4. Download and read CSV: 12 rows

✅ Day 1 Complete! Ready for Day 2
```

---

## 📝 Day 1 Summary

### What We Accomplished

| Task | Status |
|------|--------|
| Created Azure Storage Account | ✅ |
| Set up container with folder structure | ✅ |
| Configured Python environment & Azure SDK | ✅ |
| Created Azure client authentication | ✅ |
| Uploaded sample CSV to blob storage | ✅ |
| Downloaded and verified data | ✅ |
| Created reusable Python classes | ✅ |
| Tested end-to-end connectivity | ✅ |

### Files Created

- `setup_blob_storage.py` - Initialize containers
- `upload_sample_data.py` - Upload CSV files
- `download_blob_data.py` - Download and verify data
- `tests/test_azure_storage.py` - Automated tests

### Costs Estimate

**For this tutorial:** ~$0-1/month (free tier has generous limits)
- Storage: $0.0184/GB/month (first 50 TB)
- Sample CSV: ~2.5 KB
- Total: Negligible

---

## 🚀 Next Steps (Day 2 Preview)

Tomorrow we'll:
1. Download real Kaggle datasets (Olist, Flipkart, Amazon)
2. Upload them to Azure Blob Storage
3. Set up Databricks workspace
4. Create first PySpark notebook
5. Process data: clean, aggregate, feature engineering

---

## 🆘 Troubleshooting

### Issue: "Invalid account credentials"
```bash
# Verify credentials
az storage account show-connection-string --name pricingenginedata --resource-group pricing-engine-rg

# Update .env with correct key
```

### Issue: "Container not found"
```bash
# List containers
az storage container list --account-name pricingenginedata --account-key $AZURE_STORAGE_KEY

# Run setup_blob_storage.py again
python setup_blob_storage.py
```

### Issue: "File not found in downloads"
```bash
# Verify file exists in Azure
python -c "
from src.utils.azure_clients import AzureStorageClient
client = AzureStorageClient()
blobs = client.list_blobs('raw/')
print('Files:', blobs)
"
```

---

## 📚 Additional Resources

- [Azure Storage Documentation](https://learn.microsoft.com/en-us/azure/storage/)
- [Azure Storage Blob SDK for Python](https://pypi.org/project/azure-storage-blob/)
- [Connection Strings & Keys](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage)

---

**Status: ✅ Day 1 Complete**

Next: [Day 2 - Databricks & Data Pipeline](DAY2_DATABRICKS_SETUP.md) (coming soon)
