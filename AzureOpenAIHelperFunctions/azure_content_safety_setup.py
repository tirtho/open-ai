#!pip install azure-keyvault-secrets
#!pip install azure-ai-contentsafety

import os

def get_content_safety_config():
    #KeysFromEnv, KeysFromAKVWithMI, KeysFromAKVWithCLIAuth
    match os.getenv('OPENAI_AUTH_TYPE'):
        case 'KeysFromAKVWithCLIAuth':
            print("Getting Azure Content Safety Credentials from Azure Key Vault with Azure CLI Auth")
            return get_content_safety_config_from_key_vault_cli_auth()
        case 'KeysFromAKVWithMI':
            print("Getting Azure Content Safety Credentials from Azure Key Vault with Azure Managed Identity Auth")
            return get_content_safety_config_from_key_vault_mi_auth()
        case 'KeysFromEnv':
            print("Getting Azure Content Safety Credentials from environment variables set in the OS")
            return get_content_safety_config_from_os_env()
        case _:
            print("Setup environment variable OPENAI_AUTH_TYPE to one of KeysFromEnv, KeysFromAKVWithMI, KeysFromAKVWithCLIAuth")
    return 'NOT_FOUND', 'NOT_FOUND'

def get_content_safety_config_from_os_env():
    key = os.getenv('CONTENT_SAFETY_KEY')
    endpoint = os.getenv('CONTENT_SAFETY_ENDPOINT')
    return key, endpoint

# Using Azure Key Vault to get Azure Azure Content Safety Endpoint and Key
# to Authenticate Azure OpenAI to run API calls
# Using Azure CLI Auth for script to access Key Vault
def get_content_safety_config_from_key_vault_cli_auth():
    from azure.keyvault.secrets import SecretClient
    
    from azure.identity import AzureCliCredential, ChainedTokenCredential
    azure_cli = AzureCliCredential()
    credential = ChainedTokenCredential(azure_cli)

    VAULT_URL = os.getenv('KEY_VAULT_URL')
    client = SecretClient(vault_url=VAULT_URL, credential=credential)

    key = client.get_secret('content-safety-api-key').value
    endpoint = client.get_secret('content-safety-endpoint').value
    return key, endpoint

# Using Azure Key Vault to get Azure Content Safety Endpoint and Key
# to run API calls
# Using Managed Identity Auth for script to access Key Vault
def get_content_safety_config_from_key_vault_mi_auth():
    from azure.keyvault.secrets import SecretClient
    
    from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential
    managed_identity = ManagedIdentityCredential()
    credential = ChainedTokenCredential(managed_identity)

    VAULT_URL = os.getenv('KEY_VAULT_URL')
    client = SecretClient(vault_url=VAULT_URL, credential=credential)

    key = client.get_secret('content-safety-api-key').value
    endpoint = client.get_secret('content-safety-endpoint').value
    return key, endpoint

def get_content_safety(client, text_input):
    from azure.core.exceptions import HttpResponseError
    from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
    request = AnalyzeTextOptions(text=text_input, 
                             categories=[TextCategory.HATE, 
                                         TextCategory.SELF_HARM, 
                                         TextCategory.VIOLENCE,
                                         TextCategory.SEXUAL]
                            )
    try:
        response = client.analyze_text(request)
    except HttpResponseError as e:
        error_text = "Content Safety Results:\nAnalyze text failed."
        if e.error:
            error_text = error_text + "\nError code: {}\nError message: {}".format(e.error.code, e.error.message)
        print(error_text)
        return "FAILED"
    
    text = 'Content Safety Results:'
    # Check the severity (0 to 6)
    if response.hate_result:
        text = text + "\n\tHate severity: {}".format(response.hate_result.severity)
    if response.self_harm_result:
        text = text + "\n\tSelfHarm severity: {}".format(response.self_harm_result.severity)
    if response.violence_result:
        text = text + "\n\tViolence severity: {}".format(response.violence_result.severity)
    if response.sexual_result:
        text = text + "\n\tSexual severity: {}".format(response.sexual_result.severity)
    return text

# Create or update a Block List
def add_or_update_block_list(client, block_list_name, block_list_description):
    try:
        blocklist = client.create_or_update_text_blocklist(
                            blocklist_name=block_list_name, 
                            resource={"description": block_list_description})
        if blocklist:
            print("\nBlocklist created or updated: ")
            # print(f"Name: {blocklist.blocklist_name}, Description: {blocklist.description}")
            return blocklist.blocklist_name
    except HttpResponseError as e:
        print("\nCreate or update text blocklist failed: ")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
        print(e)
    return "FAILED"

# Add blocked text items to an existing Block List
def add_blocked_items(client, block_list_name, block_text_array):
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.contentsafety.models import (
        TextBlockItemInfo,
        AddBlockItemsOptions
    )
    from azure.core.exceptions import HttpResponseError
    
    block_items = []
    for block_text in block_text_array:
        block_items.append(TextBlockItemInfo(text = block_text))
 
    added_block_text_items = []
    try:
        result = client.add_block_items(
            blocklist_name=block_list_name,
            body=AddBlockItemsOptions(block_items=block_items),
        )
        if result and result.value:
            for block_item in result.value:
                added_block_text_items.append(block_item.text)
                # print(f"BlockItemId: {block_item.block_item_id}, Text: {block_item.text}, Description: {block_item.description}")
            return added_block_text_items
    except HttpResponseError as e:
        print("\nAdd block items failed: ")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
        print(e)
    return "FAILED"

# Get content safety with custom blocked text list
def get_content_safety_custom(client, block_list_names, text_input):
    from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.contentsafety.models import (
        TextBlockItemInfo,
        AddBlockItemsOptions
    )
    from azure.core.exceptions import HttpResponseError

    try:
        # After you edit your blocklist, it usually takes effect in 5 minutes, 
        # please wait some time before analyzing with blocklist after editing.
        analysis_result = client.analyze_text(AnalyzeTextOptions
                                                  (
                                                    text=text_input, 
                                                    blocklist_names=block_list_names, 
                                                    break_by_blocklists=False
                                                  )
                                             )
        text = 'Content Safety Results (blank if none found):'
        if analysis_result and analysis_result.blocklists_match_results:
            text = text + "\n  Blocklist match results: "
            for match_result in analysis_result.blocklists_match_results:
                text = text + "\n\tBlock item hit in text, Offset={}, Length={}".format(match_result.offset, match_result.length)
                text = text + "\n\tBlocklistName: {}, BlockItemId: {}".format(match_result.blocklist_name, match_result.block_item_id)
                text = text + "\n\tBlockItemText: {}".format(match_result.block_item_text)
        return text
    except HttpResponseError as e:
        print("\nAnalyze text failed: ")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
        print(e)
    return "FAILED"
# Analyze image content for safety
def get_image_safety(client, image_filepath):
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
    from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData
    
    # Build request
    with open(image_filepath, "rb") as file:
        request = AnalyzeImageOptions(image=ImageData(content=file.read()))

    # Analyze image
    try:
        response = client.analyze_image(request)
    except HttpResponseError as e:
        print("Analyze image failed.")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
        print(e)
        return "FAILED"

    text = 'Image Content Safety Results in file {}:'.format(image_filepath)
    # Check the severity (0 to 6)
    if response.hate_result:
        text = text + "\n\tHate severity: {}".format(response.hate_result.severity)
    if response.self_harm_result:
        text = text + "\n\tSelfHarm severity: {}".format(response.self_harm_result.severity)
    if response.violence_result:
        text = text + "\n\tViolence severity: {}".format(response.violence_result.severity)
    if response.sexual_result:
        text = text + "\n\tSexual severity: {}".format(response.sexual_result.severity)
    return text    
    