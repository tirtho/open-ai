#!pip install azure-keyvault-secrets
#!pip install openai

import openai
import os

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

    openai.api_key = client.get_secret('openai-api-key').value
    openai.api_base = client.get_secret('openai-endpoint').value
    openai.api_version = client.get_secret('openai-api-version').value
    openai.api_type = 'azure'
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

    openai.api_key = client.get_secret('openai-api-key').value
    openai.api_base = client.get_secret('openai-endpoint').value
    openai.api_version = client.get_secret('openai-api-version').value
    openai.api_type = 'azure'
    return


# Prompt Completion Function
def get_completion(
                    prompt, 
                    engine="tr-non-prod-openai-gpt-35-turbo0301", 
                    model="gpt-3.5-turbo",
                    temperature=0
                ):
    messages = [{"role": "user", "content": prompt}]
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
                        engine="tr-non-prod-openai-gpt-35-turbo0301", 
                        model="gpt-3.5-turbo", 
                        temperature=0
                    ):
    response = openai.ChatCompletion.create(
        engine=engine,
        model=model,
        messages=messages,
        temperature=temperature # this is the degree of randomness of the model's output
    )
    #     print(str(response.choices[0].message))
    return response.choices[0].message["content"]

# Generate Embeddings
def get_embeddings_from_text(
                        text,
                        engine="tr-non-prod-openai-text-embedding-ada"
                    ):
    response = openai.Embedding.create(
        input=text,
        engine=engine
    )
    # print(str(response['data'][0]['embedding']))
    return response['data'][0]['embedding']
    
