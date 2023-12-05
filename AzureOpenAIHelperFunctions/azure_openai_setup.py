#!pip install azure-keyvault-secrets
#!pip install openai

import openai
import os
from langchain.embeddings import OpenAIEmbeddings

# The global variables with any default values
COMPLETION_MODEL = 'gpt-3.5-turbo'
COMPLETION_MODEL_DEPLOYMENT_NAME = ''
EMBEDDINGS_TEXT_MODEL_DEPLOYMENT_NAME = ''

def set_openai_config():
    #KeysFromEnv, KeysFromAKVWithMI, KeysFromAKVWithCLIAuth, KeysFromManagedId
    match os.getenv('OPENAI_AUTH_TYPE'):
        case 'KeysFromAKVWithCLIAuth':
            get_config_from_key_vault_cli_auth()
            print("Got Azure OpenAI Credentials from Azure Key Vault with Azure CLI Auth")
        case 'KeysFromAKVWithMI':
            get_config_from_key_vault_mi_auth()
            print("Got Azure OpenAI Credentials from Azure Key Vault with Azure Managed Identity Auth")
        case 'KeysFromManagedId':
            get_config_from_aad()
            print("Got Azure OpenAI Credentials using Azure Managed ID")
        case 'KeysFromEnv':
            get_config_from_os_env()
            print("Got Azure OpenAI Credentials from environment variables set in the OS")
        case _:
            print("Setup environment variable OPENAI_AUTH_TYPE to one of KeysFromEnv, KeysFromAKVWithMI, KeysFromAKVWithCLIAuth, KeysFromManagedId")
    return

# Read all the needed secrets from AKV
def set_openai_global_config_parameters(client):
    openai.api_key = client.get_secret('openai-api-key').value
    openai.api_base = client.get_secret('openai-endpoint').value
    openai.api_version = client.get_secret('openai-api-version').value
    openai.api_type = 'azure'
    global COMPLETION_MODEL_DEPLOYMENT_NAME
    global EMBEDDINGS_TEXT_MODEL_DEPLOYMENT_NAME
    COMPLETION_MODEL_DEPLOYMENT_NAME = client.get_secret('openai-gpt-35-turbo-deployment-name').value
    EMBEDDINGS_TEXT_MODEL_DEPLOYMENT_NAME = client.get_secret('openai-text-embedding-deployment-name').value
    return

# Return the global variables with their current value
def get_openai_global_config_parameters():
    return openai, COMPLETION_MODEL, COMPLETION_MODEL_DEPLOYMENT_NAME

# Use this only for debugging purposes, in case you need a quick and dirty
# way to add the keys to bypass the AKV approach.
def get_config_from_os_env():
    openai.api_key = os.getenv('OPENAI_KEY')
    openai.api_base = os.getenv('OPENAI_ENDPOINT')
    # 2023-03-15-preview
    openai.api_version = os.getenv('OPENAI_API_VERSION')
    openai.api_type = 'azure'
    #print("Key %s, URL %s, Version %s, Type %s" % (openai.api_key, openai.base, openai.api_version, openai.api_type))
    return

# Using Azure Key Vault to get Azure OpenAi Endpoint and Key
# to Authenticate Azure OpenAI to run API calls
# Using Azure CLI Auth for script to access Key Vault
def get_config_from_key_vault_cli_auth():
    from azure.keyvault.secrets import SecretClient
    
    from azure.identity import AzureCliCredential, ChainedTokenCredential
    azure_cli = AzureCliCredential()
    credential = ChainedTokenCredential(azure_cli)

    VAULT_URL = os.getenv('KEY_VAULT_URL')
    client = SecretClient(vault_url=VAULT_URL, credential=credential)
    set_openai_global_config_parameters(client)
    
    return

# Using Azure Key Vault to get Azure OpenAi Endpoint and Key
# to Authenticate Azure OpenAI to run API calls
# Using Managed Identity Auth for script to access Key Vault
def get_config_from_key_vault_mi_auth():
    from azure.keyvault.secrets import SecretClient
    
    from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential
    managed_identity = ManagedIdentityCredential()
    credential = ChainedTokenCredential(managed_identity)

    VAULT_URL = os.getenv('KEY_VAULT_URL')
    client = SecretClient(vault_url=VAULT_URL, credential=credential)
    set_openai_global_config_parameters(client)

    return

# Get the token or api secret from AAD
# and the remaining parameters from Key Vault
def get_config_from_aad():
    get_config_from_key_vault_mi_auth()

    from azure.identity import DefaultAzureCredential
    default_credential = DefaultAzureCredential()
    token = default_credential.get_token("https://cognitiveservices.azure.com/.default")
    openai.api_type = "azure_ad"
    openai.api_key = token.token
    print("Key:: %s, \nURL:: %s, \nVersion:: %s, \nType:: %s\n" % 
          (openai.api_key, openai.api_base, openai.api_version, openai.api_type))
    return

# Prompt Completion Function
def get_completion(
                    prompt, 
                    engine=None, 
                    model=None,
                    temperature=0
                ):
    messages = [{"role": "user", "content": prompt}]
    if engine is None:
        engine = COMPLETION_MODEL_DEPLOYMENT_NAME
    if model is None:
        model = COMPLETION_MODEL
    response = openai.ChatCompletion.create(
        engine=engine,
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message["content"]

# Prompt Message Function, most suitable for Chtbots
def get_completion_from_messages(
                        messages, 
                        engine=None, 
                        model=None,
                        temperature=0
                    ):
    if engine is None:
        engine = COMPLETION_MODEL_DEPLOYMENT_NAME
    if model is None:
        model = COMPLETION_MODEL
    response = openai.ChatCompletion.create(
        engine=engine,
        model=model,
        messages=messages,
        temperature=temperature # this is the degree of randomness of the model's output
    )
    #     print(str(response.choices[0].message))
    return response.choices[0].message["content"]

# Get the embeddings deployment name

def get_embeddings_text_model_deployment_name():
    return EMBEDDINGS_TEXT_MODEL_DEPLOYMENT_NAME
    
# Create the embedding instance
def get_azure_openai_embeddings(deployment=None):
    # set the environment variables needed for openai package to know to reach out to azure
    import os
    os.environ["OPENAI_API_TYPE"] = openai.api_type
    os.environ["OPENAI_API_BASE"] = openai.api_base
    os.environ["OPENAI_API_KEY"] = openai.api_key
    os.environ["OPENAI_API_VERSION"] = openai.api_version

    if deployment is None:
        deployment = EMBEDDINGS_TEXT_MODEL_DEPLOYMENT_NAME
    return OpenAIEmbeddings(deployment=deployment)

# Generate Embeddings
def get_embeddings_from_text(
                        text,
                        engine=None
                    ):
    if engine is None:
        engine = EMBEDDINGS_TEXT_MODEL_DEPLOYMENT_NAME 
    response = openai.Embedding.create(
        input=text,
        engine=engine
    )
    # print(str(response['data'][0]['embedding']))
    return response['data'][0]['embedding']
    
