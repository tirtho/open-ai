#!pip install azure-keyvault-secrets
#!pip install openai

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
import os
import requests

def set_openai_config():
    #KeysFromEnv, KeysFromAKVWithMI, KeysFromAKVWithCLIAuth, KeysFromManagedId
    match os.getenv('OPENAI_AUTH_TYPE'):
        case 'KeysFromAKVWithCLIAuth':
            print("Getting Azure OpenAI Credentials from Azure Key Vault with Azure CLI Auth")
            return get_config_from_key_vault_cli_auth()
        case 'KeysFromAKVWithMI':
            print("Getting Azure OpenAI Credentials from Azure Key Vault with Azure Managed Identity Auth")
            return get_config_from_key_vault_mi_auth()
        case 'KeysFromManagedId':
            print("Getting Azure OpenAI Credentials using Azure Managed ID")
            return get_config_from_aad()
        case 'KeysFromEnv':
            print("Getting Azure OpenAI Credentials from environment variables set in the OS")
            return get_config_from_os_env()
        case _:
            print("Setup environment variable OPENAI_AUTH_TYPE to one of KeysFromEnv, KeysFromAKVWithMI, KeysFromAKVWithCLIAuth, KeysFromManagedId")
    return None, None, None

# Read all the needed secrets from AKV
def set_openai_global_config_parameters(client):
    api_key = client.get_secret('openai-api-key').value
    api_endpoint = client.get_secret('openai-endpoint').value
    api_version = client.get_secret('openai-api-version').value
    return api_endpoint, api_key, api_version

# Use this only for debugging purposes, in case you need a quick and dirty
# way to add the keys to bypass the AKV approach.
def get_config_from_os_env():
    api_key = os.getenv('OPENAI_API_KEY')
    api_endpoint = os.getenv('OPENAI_API_ENDPOINT')
    api_version = os.getenv('OPENAI_API_VERSION')
    #print("Key %s, URL %s, Version %s, Type %s" % (openai.api_key, openai.base, openai.api_version, openai.api_type))
    return api_endpoint, api_key, api_version
 

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
    return set_openai_global_config_parameters(client)
    
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
    return set_openai_global_config_parameters(client)

# Get the token or api secret from AAD
# and the remaining parameters from Key Vault
def get_config_from_aad():
    key, endpoint, version = get_config_from_key_vault_mi_auth()

    from azure.identity import DefaultAzureCredential
    default_credential = DefaultAzureCredential()
    token = default_credential.get_token("https://cognitiveservices.azure.com/.default")
    print("Key:: %s, \nEndpoint:: %s, \nVersion:: %s\n" % 
          (key, endpoint, version))
    return endpoint, token.token, verson

def get_openai_client(aoai_endpoint, aoai_api_key, aoai_version):
  try:
    #--- api_key = os.getenv("OPENAI_API_KEY")
    if aoai_api_key and not aoai_api_key.isspace():
      # the string is non-empty
      client = AzureOpenAI(
                api_key=aoai_api_key,
                azure_endpoint=aoai_endpoint,
                api_version=aoai_version
              )
      print("\nGot OPENAI API Key from environment variable")
      return True, client
    else:
      # the string is empty
      try:
        print(f"\nCould not get API key from environment variable OPENAI_API_KEY. Trying Managed ID")
        token_provider = get_bearer_token_provider (
          DefaultAzureCredential(),
          "https://cognitiveservices.azure.com/.default"          
        )
        client = AzureOpenAI(
          azure_ad_token_provider=token_provider,
          azure_endpoint=aoai_endpoint,
          api_version=aoai_version
        )
        print("\nAuthenticated successfully with AAD token")
        return True, client
      except:
        print("\nSomething went wrong getting token with Managed Identity")
        return False, None
  except:
    print("\nSomething went wrong getting access key from environment variable")
    return False, None

# Returns total tokens used and the chat completion
def get_chat_completion(the_client, the_model, the_messages):
    completion = the_client.chat.completions.create(
        model=the_model,
        messages=the_messages,
        temperature=0,
        max_tokens=1000,
        #top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return completion.usage.total_tokens, completion.choices[0].finish_reason, completion.choices[0].message.content  

# Find cosine similarty between the vectors
import numpy as np
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Return vectors for a given text using the ADA model
def generate_embedding(the_client, the_model, the_text):
    response = the_client.embeddings.create(
                  input=the_text, 
                  model=the_model
                )
    return response.data[0].embedding