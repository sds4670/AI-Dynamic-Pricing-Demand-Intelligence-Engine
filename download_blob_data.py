"""
download_blob_data.py
Downloads files from Azure Blob Storage and verifies them

Usage:
    python download_blob_data.py
"""

from azure.storage.blob import BlobServiceClient
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT", "pricingenginedata")
ACCOUNT_KEY = os.getenv("AZURE_STORAGE_KEY")
CONTAINER_NAME = "pricing-engine-data"


def download_file_from_blob(blob_path: str, local_file_path: str) -> bool:
    """
    Download a file from Azure Blob Storage.
    
    Args:
        blob_path: Path in blob storage
        local_file_path: Local destination path
        
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


def list_blobs_in_container() -> None:
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
    blob_count = 0
    for blob in blobs:
        if blob.name != ".gitkeep":  # Skip empty folder markers
            blob_count += 1
            size_kb = blob.size / 1024 if blob.size else 0
            print(f"  ├── {blob.name} ({size_kb:.1f} KB)")
    
    if blob_count == 0:
        print("  (no files found)")


def verify_csv_data(file_path: str) -> None:
    """Verify and display CSV data."""
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        
        print(f"\n📊 CSV Data Preview ({file_path}):\n")
        print(df.head(10).to_string(index=False))
        print(f"\n📈 Summary:")
        print(f"  ├── Rows: {len(df)}")
        print(f"  ├── Columns: {len(df.columns)}")
        print(f"  └── Column names: {', '.join(df.columns)}")
    except ImportError:
        print("⚠ pandas not installed, skipping CSV preview")
        print(f"✓ File downloaded to: {file_path}")
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
