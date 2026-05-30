"""
Azure clients for storage and OpenAI operations.
"""

import os
from typing import Optional, List
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.identity import DefaultAzureCredential
from src.utils.logger import logger


class AzureStorageClient:
    """Client for interacting with Azure Blob Storage."""
    
    def __init__(
        self,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        container_name: Optional[str] = None
    ):
        """
        Initialize Azure Storage client.
        
        Args:
            account_name: Azure storage account name
            account_key: Storage account key
            container_name: Default container name
        """
        self.account_name = account_name or os.getenv("AZURE_STORAGE_ACCOUNT")
        self.account_key = account_key or os.getenv("AZURE_STORAGE_KEY")
        self.container_name = container_name or "pricing-engine-data"
        
        if not self.account_name:
            raise ValueError("Azure storage account name not configured")
        
        # Create blob service client
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={self.account_name};"
            f"AccountKey={self.account_key};"
            f"EndpointSuffix=core.windows.net"
        )
        
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        
        logger.info(f"Azure Storage client initialized for container: {self.container_name}")
    
    def upload_file(self, local_path: str, blob_path: str, overwrite: bool = True) -> str:
        """
        Upload file to Azure Blob Storage.
        
        Args:
            local_path: Local file path
            blob_path: Path in blob storage
            overwrite: Whether to overwrite existing file
            
        Returns:
            Blob URL
        """
        with open(local_path, "rb") as data:
            self.container_client.upload_blob(blob_path, data, overwrite=overwrite)
        
        logger.info(f"Uploaded {local_path} to {blob_path}")
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_path}"
    
    def download_file(self, blob_path: str, local_path: str) -> None:
        """
        Download file from Azure Blob Storage.
        
        Args:
            blob_path: Path in blob storage
            local_path: Local file path to save
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_path
        )
        
        with open(local_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        logger.info(f"Downloaded {blob_path} to {local_path}")
    
    def list_blobs(self, prefix: str = "") -> List[str]:
        """
        List blobs in container with optional prefix.
        
        Args:
            prefix: Filter by prefix
            
        Returns:
            List of blob names
        """
        blobs = [blob.name for blob in self.container_client.list_blobs(name_starts_with=prefix)]
        return blobs
    
    def delete_blob(self, blob_path: str) -> None:
        """
        Delete blob from storage.
        
        Args:
            blob_path: Path in blob storage
        """
        self.container_client.delete_blob(blob_path)
        logger.info(f"Deleted {blob_path}")
    
    def blob_exists(self, blob_path: str) -> bool:
        """Check if blob exists."""
        try:
            self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_path
            ).get_blob_properties()
            return True
        except Exception:
            return False


class AzureOpenAIClient:
    """Client for Azure OpenAI API calls."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None
    ):
        """
        Initialize Azure OpenAI client.
        
        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint URL
            deployment: Deployment name
        """
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
        
        if not all([self.api_key, self.endpoint]):
            raise ValueError("Azure OpenAI credentials not configured")
        
        logger.info(f"Azure OpenAI client initialized for deployment: {self.deployment}")
    
    def get_config(self) -> dict:
        """
        Get configuration for LangChain Azure OpenAI LLM.
        
        Returns:
            Configuration dictionary for AzureChatOpenAI
        """
        return {
            "api_key": self.api_key,
            "azure_endpoint": self.endpoint,
            "deployment_name": self.deployment,
            "api_version": "2023-05-15",
            "temperature": 0.3,
            "max_tokens": 2000
        }


def get_storage_client(container_name: Optional[str] = None) -> AzureStorageClient:
    """Factory function to get Azure Storage client."""
    return AzureStorageClient(container_name=container_name)


def get_openai_client() -> AzureOpenAIClient:
    """Factory function to get Azure OpenAI client."""
    return AzureOpenAIClient()
