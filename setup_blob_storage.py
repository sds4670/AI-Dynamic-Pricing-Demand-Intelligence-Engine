"""
setup_blob_storage.py
Sets up Azure Blob Storage containers and folders for pricing engine
Run this ONCE to initialize storage

Usage:
    python setup_blob_storage.py
"""

from azure.storage.blob import BlobServiceClient
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
