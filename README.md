# open-ai

### Summary
- Open AI Notebooks with examples on
  - Prompt Engineering
  - Content Safety APIs
  - Embedding APIs
  - LandChain
  - Misc
- Command line Python code example to leverage the Open AI libraries

All examples use AAD auth and use Managed Identity to authenticate against Azure Open AI or authenticate against an Azure Key Vault and retrieves keys to access the Open AI and other APIs. So, there is no need to store keys/secrets in code or anywhere in the OS or any file store.

### Setup
#### Azure Open AI
- Create an instance of Azure Open AI in your Azure Subscription.
- Deploy the gpt-35-turbo and text-embedding-ada-002 models
- Note down
  - The Azure Open AI key
  - The Azure Open AI Endpoint
  - The Deployment Names for the gpt-35-turbo and text-embedding-ada-002 models deployed in the above step
  - The Azure Open AI version 
- You will find instructions here - https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal
#### Azure Key Vault
- Create an Azure Key Vault (AKV) in your subscription. You will find instructions here - https://learn.microsoft.com/en-us/azure/key-vault/general/quick-create-portal.
- In the AKV add your Azure Active Directory (AAD) ID with the "Key Vault Secrets Officer" role. Also, make sure this AAD ID is allowed to login to the corresponding Azure Subscription.
- Add the following Secrets in the AKV
  - 


