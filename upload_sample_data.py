"""
upload_sample_data.py
Uploads sample CSV files to Azure Blob Storage

Usage:
    python upload_sample_data.py
"""

from azure.storage.blob import BlobServiceClient
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT", "pricingenginedata")
ACCOUNT_KEY = os.getenv("AZURE_STORAGE_KEY")
CONTAINER_NAME = "pricing-engine-data"


def upload_file_to_blob(local_file_path: str, blob_path: str) -> bool:
    """
    Upload a file to Azure Blob Storage.
    
    Args:
        local_file_path: Path to local file
        blob_path: Path in blob storage (e.g., 'raw/data.csv')
        
    Returns:
        True if successful, False otherwise
    """
    
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


def create_sample_csv() -> str:
    """
    Create a sample CSV for testing.
    
    Returns:
        Path to created CSV file
    """
    
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
