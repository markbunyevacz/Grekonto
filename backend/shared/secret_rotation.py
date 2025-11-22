import os
import logging
import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from . import table_service

def get_secret_client():
    """Get Azure Key Vault Secret Client"""
    key_vault_name = os.environ.get("KEY_VAULT_NAME")
    if not key_vault_name:
        logging.error("KEY_VAULT_NAME not set")
        return None
    
    kv_uri = f"https://{key_vault_name}.vault.azure.net"
    credential = DefaultAzureCredential()
    return SecretClient(vault_url=kv_uri, credential=credential)

def get_secret_age(secret_name: str) -> int:
    """Get secret age in days"""
    try:
        client = get_secret_client()
        if not client:
            return -1
        
        secret = client.get_secret(secret_name)
        created = secret.properties.created_on
        age = (datetime.datetime.utcnow() - created.replace(tzinfo=None)).days
        return age
    except Exception as e:
        logging.error(f"Error getting secret age: {str(e)}")
        return -1

def should_rotate_secret(secret_name: str, max_age_days: int = 30) -> bool:
    """Check if secret should be rotated"""
    age = get_secret_age(secret_name)
    if age < 0:
        return False
    return age >= max_age_days

def get_all_secrets_status():
    """Get status of all secrets"""
    secrets_to_check = [
        "email-password",
        "aoc-api-key",
        "drive-service-account",
        "dropbox-access-token"
    ]
    
    status = {}
    for secret_name in secrets_to_check:
        age = get_secret_age(secret_name)
        should_rotate = should_rotate_secret(secret_name, max_age_days=30)
        status[secret_name] = {
            "age_days": age,
            "should_rotate": should_rotate,
            "max_age_days": 30
        }
    
    return status

