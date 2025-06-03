#!pip install azure-keyvault-secrets

import os

from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.models import Vector
from azure.search.documents.indexes.models import (  
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    PrioritizedFields,  
    SemanticField,  
    SearchField,  
    SemanticSettings,  
    VectorSearch,  
    VectorSearchAlgorithmConfiguration,  
)  

# The global variables
COGNITIVE_SEARCH_ENDPOINT_VALUE = ''
COGNITIVE_SEARCH_KEY_VALUE = ''
COGNITIVE_SEARCH_INDEX_VALUE = ''

def vector_search_config_name_from_index_name(index_name):
    return index_name + "-vector-config"

def semantic_search_config_name_from_index_name(index_name):
    return index_name + "-semantic-config"

def create_cognitive_search_index(index_name, search_index_client):
    
    # postfixing the index name
    VECTOR_SEARCH_CONFIG_NAME = vector_search_config_name_from_index_name(index_name)
    SEMANTIC_SEARCH_CONFIG_NAME = semantic_search_config_name_from_index_name(index_name)

    # reference docs :
    # https://learn.microsoft.com/en-us/python/api/azure-search-documents/azure.search.documents.indexes.models.searchfield?view=azure-python
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, 
                        filterable=True, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String,
                        searchable=True),
        SearchableField(name="content", type=SearchFieldDataType.String,
                        searchable=True),
        SearchableField(name="bill_id", type=SearchFieldDataType.String,
                        filterable=True, searchable=True),
        SearchableField(name="metadata", type=SearchFieldDataType.String,
                        filterable=True, searchable=True),
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, filterable=False, 
                    sortable=False, facetable=False, 
                    dimensions=1536, 
                    vector_search_configuration=VECTOR_SEARCH_CONFIG_NAME)
    ]

    vector_search_config = get_vector_configuration(index_name)

    # reference docs : 
    # https://learn.microsoft.com/en-us/azure/search/semantic-how-to-query-request?tabs=portal%2Cportal-query#2---create-a-semantic-configuration
    # https://learn.microsoft.com/en-us/python/api/azure-search-documents/azure.search.documents.indexes.models.semanticconfiguration?view=azure-python-preview
    semantic_search_config = get_semantic_configuration(index_name)
    
    # Create the semantic settings with the configuration
    semantic_settings = SemanticSettings(configurations=[semantic_search_config])

    # Create the search index with the semantic settings
    index = SearchIndex(name=index_name, fields=fields,
                        vector_search=vector_search_config, semantic_settings=semantic_settings)

    # Delete index if it exists, to do a clean start
    search_index_client.delete_index(index_name)
    # Add the index
    result = search_index_client.create_or_update_index(index)
    return result

def get_vector_configuration(index_name):
    return VectorSearch(
                algorithm_configurations=[
                    VectorSearchAlgorithmConfiguration(
                        name=vector_search_config_name_from_index_name(index_name),
                        kind="hnsw",
                        hnsw_parameters={
                            "m": 4,
                            "efConstruction": 400,
                            "metric": "cosine"
                        }
                    )
                ]
            )
    
def get_semantic_configuration(index_name):
    return SemanticConfiguration(
                name=semantic_search_config_name_from_index_name(index_name),
                prioritized_fields=PrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    prioritized_keywords_fields=[SemanticField(field_name="bill_id")],
                    prioritized_content_fields=[SemanticField(field_name="content")]
                )
            )
    
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

