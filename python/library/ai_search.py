import os
import logging
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents.indexes import SearchIndexClient

def getAISearchCredential(api_key):
  try:
    if api_key and not api_key.isspace():
      # the string is non-empty      
      logging.info("\nGot Azure Cognitive Search ADMIN API Key from environment variable")
      # Return credential
      return AzureKeyCredential(api_key)
    else:
      # the string is empty
      try:
        logging.info(f"\nCould not get API key from environment variable COG_SEARCH_ADMIN_KEY. Trying Managed ID")
        default_credential = DefaultAzureCredential()
        token = default_credential.get_token("https://cognitivesearch.azure.com/.default")
        logging.info("\nAuthenticated successfully with AAD token")
        return AzureKeyCredential(token.token)
      except:
        logging.error("\nSomething went wrong getting token with Managed Identity")
        return
  except:
    logging.error("\nSomething went wrong getting access key from environment variable")
    return
