import os
import logging
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret(secret_name: str) -> str:
    """
    Retrieves a secret from Azure Key Vault.
    """
    key_vault_name = os.environ.get("KEY_VAULT_NAME")
    if not key_vault_name:
        logging.warning("KEY_VAULT_NAME environment variable not set. Returning mock secret.")
        return "mock-secret-value"

    kv_uri = f"https://{key_vault_name}.vault.azure.net"

    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=kv_uri, credential=credential)
        retrieved_secret = client.get_secret(secret_name)
        return retrieved_secret.value
    except Exception as e:
        logging.error(f"Failed to retrieve secret '{secret_name}' from Key Vault: {str(e)}")
        raise
