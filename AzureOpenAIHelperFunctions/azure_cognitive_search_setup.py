#!pip install azure-keyvault-secrets

import os

# The global variables
COGNITIVE_SEARCH_ENDPOINT_VALUE = ''
COGNITIVE_SEARCH_KEY_VALUE = ''
COGNITIVE_SEARCH_INDEX_VALUE = ''

def set_cognitive_search_config():
    #KeysFromEnv, KeysFromAKVWithMI, KeysFromAKVWithCLIAuth
    match os.getenv('OPENAI_AUTH_TYPE'):
        case 'KeysFromAKVWithCLIAuth':
            print("Getting Azure Cognitive Search Credentials from Azure Key Vault with Azure CLI Auth")
            get_cognitive_search_config_from_key_vault_cli_auth()
        case 'KeysFromAKVWithMI':
            print("Getting Azure Cognitive Search Credentials from Azure Key Vault with Azure Managed Identity Auth")
            get_cognitive_search_config_from_key_vault_mi_auth()
        case 'KeysFromEnv':
            print("Getting Azure Cognitive Search Credentials from environment variables set in the OS")
            get_cognitive_search_config_from_os_env()
        case _:
            print("Setup environment variable OPENAI_AUTH_TYPE to one of KeysFromEnv, KeysFromAKVWithMI, KeysFromAKVWithCLIAuth")
    return get_cognitive_search_global_config_parameters()

def get_cognitive_search_config_from_os_env():
    global COGNITIVE_SEARCH_KEY_VALUE
    global COGNITIVE_SEARCH_ENDPOINT_VALUE
    global COGNITIVE_SEARCH_INDEX_VALUE
    COGNITIVE_SEARCH_KEY_VALUE = os.getenv('COGNITIVE_SEARCH_KEY')
    COGNITIVE_SEARCH_ENDPOINT_VALUE = os.getenv('COGNITIVE_SEARCH_ENDPOINT')
    COGNITIVE_SEARCH_INDEX_VALUE = os.getenv('COGNITIVE_SEARCH_INDEX')
    return

# Set the global config variables after reading all the needed secrets from AKV
def set_cognitive_search_global_config_parameters(client):
    global COGNITIVE_SEARCH_KEY_VALUE
    global COGNITIVE_SEARCH_ENDPOINT_VALUE
    global COGNITIVE_SEARCH_INDEX_VALUE
    COGNITIVE_SEARCH_KEY_VALUE = client.get_secret('cognitive-search-api-key').value
    COGNITIVE_SEARCH_ENDPOINT_VALUE = client.get_secret('cognitive-search-endpoint').value
    COGNITIVE_SEARCH_INDEX_VALUE = client.get_secret('cognitive-search-index').value
    return

# Return all the global config variables
def get_cognitive_search_global_config_parameters():
    return COGNITIVE_SEARCH_KEY_VALUE, COGNITIVE_SEARCH_ENDPOINT_VALUE, COGNITIVE_SEARCH_INDEX_VALUE

# Using Azure Key Vault to get Azure Cognitive Search Endpoint and Key
# to Authenticate Azure OpenAI to run API calls
# Using Azure CLI Auth for script to access Key Vault
def get_cognitive_search_config_from_key_vault_cli_auth():
    from azure.keyvault.secrets import SecretClient
    
    from azure.identity import AzureCliCredential, ChainedTokenCredential
    azure_cli = AzureCliCredential()
    credential = ChainedTokenCredential(azure_cli)

    VAULT_URL = os.getenv('KEY_VAULT_URL')
    client = SecretClient(vault_url=VAULT_URL, credential=credential)
    set_cognitive_search_global_config_parameters(client)
    
    return

# Using Azure Key Vault to get Azure Cognitive Search Endpoint and Key
# to run API calls
# Using Managed Identity Auth for script to access Key Vault
def get_cognitive_search_config_from_key_vault_mi_auth():
    from azure.keyvault.secrets import SecretClient
    
    from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential
    managed_identity = ManagedIdentityCredential()
    credential = ChainedTokenCredential(managed_identity)

    VAULT_URL = os.getenv('KEY_VAULT_URL')
    client = SecretClient(vault_url=VAULT_URL, credential=credential)
    set_cognitive_search_global_config_parameters(client)
    
    return

