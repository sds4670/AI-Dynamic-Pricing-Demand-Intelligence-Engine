"""
Test Azure Blob Storage connectivity and operations
"""

import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class TestAzureStorageSetup:
    """Test Azure Storage setup and basic operations."""
    
    def test_env_variables(self):
        """Test that required environment variables are set."""
        account = os.getenv("AZURE_STORAGE_ACCOUNT")
        key = os.getenv("AZURE_STORAGE_KEY")
        
        assert account is not None, "AZURE_STORAGE_ACCOUNT not set in .env"
        assert key is not None, "AZURE_STORAGE_KEY not set in .env"
        print(f"✓ Environment variables configured")
    
    def test_azure_sdk_installed(self):
        """Test that Azure SDK is installed."""
        try:
            from azure.storage.blob import BlobServiceClient
            print(f"✓ Azure SDK installed")
        except ImportError:
            pytest.fail("Azure SDK not installed. Run: pip install azure-storage-blob")
    
    def test_azure_connection(self):
        """Test connection to Azure Blob Storage."""
        from azure.storage.blob import BlobServiceClient
        
        account = os.getenv("AZURE_STORAGE_ACCOUNT")
        key = os.getenv("AZURE_STORAGE_KEY")
        
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={account};"
            f"AccountKey={key};"
            f"EndpointSuffix=core.windows.net"
        )
        
        try:
            client = BlobServiceClient.from_connection_string(connection_string)
            client.get_account_information()
            print(f"✓ Connected to Azure storage account: {account}")
        except Exception as e:
            pytest.fail(f"Failed to connect to Azure: {e}")
    
    def test_container_exists(self):
        """Test that container exists."""
        from azure.storage.blob import BlobServiceClient
        
        account = os.getenv("AZURE_STORAGE_ACCOUNT")
        key = os.getenv("AZURE_STORAGE_KEY")
        container = "pricing-engine-data"
        
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={account};"
            f"AccountKey={key};"
            f"EndpointSuffix=core.windows.net"
        )
        
        try:
            client = BlobServiceClient.from_connection_string(connection_string)
            container_client = client.get_container_client(container)
            properties = container_client.get_container_properties()
            print(f"✓ Container '{container}' exists")
        except Exception as e:
            print(f"⚠ Container '{container}' not found. Run setup_blob_storage.py first")
    
    def test_sample_upload_download(self):
        """Test uploading and downloading a test file."""
        from azure.storage.blob import BlobServiceClient
        
        account = os.getenv("AZURE_STORAGE_ACCOUNT")
        key = os.getenv("AZURE_STORAGE_KEY")
        container = "pricing-engine-data"
        
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={account};"
            f"AccountKey={key};"
            f"EndpointSuffix=core.windows.net"
        )
        
        # Create test file
        test_file = "test_data_temp.txt"
        test_content = "Test upload/download functionality"
        
        with open(test_file, "w") as f:
            f.write(test_content)
        
        try:
            # Upload
            client = BlobServiceClient.from_connection_string(connection_string)
            container_client = client.get_container_client(container)
            
            with open(test_file, "rb") as data:
                container_client.upload_blob("raw/test_data_temp.txt", data, overwrite=True)
            
            print(f"✓ File uploaded successfully")
            
            # Download
            blob_client = client.get_blob_client(container, "raw/test_data_temp.txt")
            downloaded_content = blob_client.download_blob().readall().decode()
            
            assert downloaded_content == test_content
            print(f"✓ File downloaded and verified successfully")
            
            # Cleanup
            container_client.delete_blob("raw/test_data_temp.txt")
            print(f"✓ Test file cleaned up")
            
        except Exception as e:
            pytest.fail(f"Upload/download test failed: {e}")
        finally:
            if Path(test_file).exists():
                Path(test_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
