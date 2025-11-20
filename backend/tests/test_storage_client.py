import unittest
from unittest.mock import MagicMock, patch
import os
from shared import storage_client

class TestStorageClient(unittest.TestCase):

    @patch('shared.storage_client.BlobServiceClient')
    @patch.dict(os.environ, {'AzureWebJobsStorage': 'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=key;EndpointSuffix=core.windows.net'})
    def test_upload_to_blob(self, mock_blob_service_client):
        # Setup
        mock_client_instance = mock_blob_service_client.from_connection_string.return_value
        mock_container_client = mock_client_instance.get_container_client.return_value
        mock_blob_client = mock_container_client.get_blob_client.return_value
        
        mock_container_client.exists.return_value = False # Simulate container not existing

        # Execute
        storage_client.upload_to_blob("test-container", "test-blob", b"data")

        # Verify
        mock_container_client.create_container.assert_called_once()
        mock_blob_client.upload_blob.assert_called_once_with(b"data", overwrite=True)

    @patch('shared.storage_client.BlobServiceClient')
    def test_upload_to_blob_no_connection_string(self, mock_blob_service_client):
        # Setup
        # Ensure env var is missing
        with patch.dict(os.environ, {}, clear=True):
             # Execute
             storage_client.upload_to_blob("test-container", "test-blob", b"data")

        # Verify
        mock_blob_service_client.from_connection_string.assert_not_called()

    @patch('shared.storage_client.BlobServiceClient')
    @patch.dict(os.environ, {'AzureWebJobsStorage': 'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=key;EndpointSuffix=core.windows.net'})
    def test_delete_blob(self, mock_blob_service_client):
        # Setup
        mock_client_instance = mock_blob_service_client.from_connection_string.return_value
        mock_blob_client = mock_client_instance.get_blob_client.return_value
        mock_blob_client.exists.return_value = True

        # Execute
        storage_client.delete_blob("test-container", "test-blob")

        # Verify
        mock_blob_client.delete_blob.assert_called_once()

if __name__ == '__main__':
    unittest.main()
