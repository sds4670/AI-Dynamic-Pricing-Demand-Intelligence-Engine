# Day 1 Quick Start Guide

Follow these 7 steps to complete Day 1. Estimated time: **30-45 minutes**

---

## ✅ Step 1: Create Azure Storage Account (5 min)

### Option A: Azure Portal
1. Go to https://portal.azure.com/
2. Click **+ Create a resource** → Search "Storage account"
3. Fill in:
   - Name: `pricingenginedata` (must be unique)
   - Region: Southeast Asia (or nearest to India)
   - Performance: Standard
   - Replication: LRS (cheapest)
4. Click **Create**
5. Once created, go to **Access Keys** and copy:
   - Storage account name
   - Key 1 (full access key)

### Option B: Azure CLI (faster)
```bash
az login
az group create --name pricing-engine-rg --location southeastasia
az storage account create --name pricingenginedata --resource-group pricing-engine-rg --location southeastasia --sku Standard_LRS
az storage account keys list --name pricingenginedata --resource-group pricing-engine-rg
```

**Save these values - you'll need them:**
```
AZURE_STORAGE_ACCOUNT = pricingenginedata
AZURE_STORAGE_KEY = [your-key-here]
```

---

## ✅ Step 2: Set Up Python Environment (5 min)

```bash
# Navigate to project
cd /workspaces/AI-Dynamic-Pricing-Demand-Intelligence-Engine

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Azure SDK
pip install azure-storage-blob==12.18.0 python-dotenv

# Verify
python -c "import azure.storage.blob; print('✓ Azure SDK ready')"
```

---

## ✅ Step 3: Configure Environment Variables (2 min)

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

Edit `.env` and add:
```env
AZURE_STORAGE_ACCOUNT=pricingenginedata
AZURE_STORAGE_KEY=your_access_key_here
```

**⚠️ NEVER commit .env to Git - it's already in .gitignore**

---

## ✅ Step 4: Initialize Azure Blob Storage (3 min)

```bash
# Creates container and folder structure
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

## ✅ Step 5: Upload Sample Data (3 min)

```bash
# Creates sample CSV and uploads to Azure
python upload_sample_data.py
```

Expected output:
```
🚀 Starting upload to Azure Blob Storage...

✓ Created sample CSV: sample_data/sample_sales.csv
✓ Uploaded: sample_data/sample_sales.csv → raw/sample_sales.csv

✅ Upload successful!
```

---

## ✅ Step 6: Download & Verify Data (3 min)

```bash
# Downloads file from Azure and shows preview
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

✅ Download and verification successful!
```

---

## ✅ Step 7: Run Automated Tests (5 min)

```bash
# Test Azure connection
pytest tests/test_azure_storage.py -v -s
```

Expected output:
```
test_azure_storage.py::TestAzureStorageSetup::test_env_variables PASSED [✓]
test_azure_storage.py::TestAzureStorageSetup::test_azure_sdk_installed PASSED [✓]
test_azure_storage.py::TestAzureStorageSetup::test_azure_connection PASSED [✓]
test_azure_storage.py::TestAzureStorageSetup::test_container_exists PASSED [✓]
test_azure_storage.py::TestAzureStorageSetup::test_sample_upload_download PASSED [✓]

✅ All tests passed!
```

---

## 🔍 Final Verification

Run this to confirm everything is working:

```bash
python -c "
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

print('🔍 Day 1 Verification\n')

load_dotenv()
account = os.getenv('AZURE_STORAGE_ACCOUNT')
key = os.getenv('AZURE_STORAGE_KEY')

print(f'✅ 1. Environment variables loaded')

connection_string = f'DefaultEndpointsProtocol=https;AccountName={account};AccountKey={key};EndpointSuffix=core.windows.net'
client = BlobServiceClient.from_connection_string(connection_string)
print(f'✅ 2. Connected to Azure')

container_client = client.get_container_client('pricing-engine-data')
blobs = list(container_client.list_blobs())
print(f'✅ 3. Found {len(blobs)} items in storage')

print(f'\n✅ Day 1 Complete!')
"
```

---

## 📁 Project Structure After Day 1

```
AI-Dynamic-Pricing-Demand-Intelligence-Engine/
├── .env                           # Your Azure credentials (DO NOT COMMIT)
├── .env.example                   # Template (already in .gitignore)
├── .gitignore                     # .env is ignored
├── setup_blob_storage.py          # Initialize container structure
├── upload_sample_data.py          # Upload CSV to Azure
├── download_blob_data.py          # Download & verify CSV
├── DAY1_AZURE_SETUP.md            # Detailed guide
├── requirements.txt
├── src/
│   ├── utils/
│   │   └── azure_clients.py       # Reusable Azure client
│   └── ...
├── tests/
│   └── test_azure_storage.py      # Automated tests
└── sample_data/
    └── sample_sales.csv           # Sample data (local copy)
```

---

## 🚀 What You've Accomplished

✅ Created Azure Storage Account  
✅ Set up folder structure in blob storage  
✅ Configured Python with Azure SDK  
✅ Authenticated from Python code  
✅ Uploaded and downloaded files  
✅ Verified end-to-end connectivity  
✅ Created reusable Python classes  
✅ Automated tests passing  

---

## ⚠️ Common Issues & Fixes

### Issue: "Invalid credentials"
```bash
# Verify your key is correct
az storage account keys list --name pricingenginedata --resource-group pricing-engine-rg
# Update .env with the correct key
```

### Issue: "Container not found"
```bash
# Run setup again
python setup_blob_storage.py
```

### Issue: "ModuleNotFoundError: No module named 'azure'"
```bash
# Install Azure SDK
pip install azure-storage-blob==12.18.0
```

### Issue: "python: command not found"
```bash
# Use python3
python3 setup_blob_storage.py
```

---

## 💰 Cost Note

- **This tutorial**: $0-1/month on free tier
- Storage: ~$0.02/GB/month (sample data is just 2.5 KB)
- Transactions: First 1M operations free
- **Total for your project data**: Negligible unless you upload TBs

---

## 📝 Files You'll Interact With

| File | Purpose | Run When |
|------|---------|----------|
| `.env` | Your Azure credentials | Edit once, commit to .gitignore |
| `setup_blob_storage.py` | Create container structure | Day 1, once |
| `upload_sample_data.py` | Upload CSV files | Day 1 + whenever adding datasets |
| `download_blob_data.py` | Verify files in Azure | Day 1 + testing |
| `src/utils/azure_clients.py` | Reusable Python class | Day 2+ (used by other code) |
| `tests/test_azure_storage.py` | Test connectivity | Day 1 + debugging |

---

## 📚 Next: Day 2 Preview

Tomorrow we'll:
1. Download real Kaggle datasets (Olist, Flipkart, Amazon India)
2. Upload them to Azure (`raw/olist.csv`, `raw/flipkart.csv`, `raw/amazon.csv`)
3. Set up Databricks workspace
4. Create PySpark notebooks
5. Process data: clean → aggregate → feature engineering

**Estimated time for Day 2:** 2 hours

---

## 🎯 Success Criteria

You've completed Day 1 when:
- ✅ Can upload a file to Azure Blob Storage from Python
- ✅ Can download a file from Azure Blob Storage to your machine
- ✅ All pytest tests pass
- ✅ `.env` file configured with your Azure credentials
- ✅ `pricing-engine-data` container has `raw/`, `processed/`, etc. folders

---

## 🆘 Need Help?

1. Check [DAY1_AZURE_SETUP.md](DAY1_AZURE_SETUP.md) for detailed explanations
2. Run `pytest tests/test_azure_storage.py -v -s` to debug
3. Check Azure Portal to verify account was created
4. Ensure `.env` has correct credentials

---

**Status: Ready to start Day 1 ✅**

*Let me know when you've completed these steps, and we'll move to Day 2!*
