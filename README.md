# open-ai

### Summary
- Open AI Notebooks with examples on
  - Prompt Engineering
  - Content Safety APIs
  - Embedding APIs
  - LangChain
  - Misc
- Command line Python code example to leverage the Open AI libraries

All examples use AAD auth and use Managed Identity to authenticate against Azure Open AI or authenticate against an Azure Key Vault and retrieves keys to access the Open AI and other APIs. So, there is no need to store keys/secrets in code or anywhere in the OS or any file store.

### Setup
#### Azure Open AI
- Create an instance of Azure Open AI in your Azure Subscription.
- Deploy the <i>gpt-35-turbo</i> and <i>text-embedding-ada-002</i> models
- Note down
  - The Azure Open AI key as <b>openai-api-key</b>
  - The Azure Open AI Endpoint as <b>openai-endpoint</b>
  - The Deployment Name as <b>openai-gpt-35-turbo-deployment-name</b> for the <i>gpt-35-turbo</i> model deployed in the above steps
  - The Deployment Name as <b>openai-text-embedding-deployment-name</b> for the <i>text-embedding-ada-002</i> model deployed in the above steps
  - The Azure Open AI version as <b>openai-api-version</b>
- You will find instructions here - https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal
#### Azure AI Content Safety API 
This is needed if you want to run the  notebooks under ResponsibleAI. Otherwise skip this section.
- Create and instance of Azure Content Safety
- Note down 
  - The API key as <b>content-safety-api-key</b>
  - The API Endpoint as <b>content-safety-endpoint</b>
- You will find instructions here - https://learn.microsoft.com/en-us/azure/cognitive-services/content-safety/overview
#### Azure Key Vault
- Create an Azure Key Vault (AKV) in your subscription. You will find instructions here - https://learn.microsoft.com/en-us/azure/key-vault/general/quick-create-portal.
- In the AKV add your Azure Active Directory (AAD) ID with the "Key Vault Secrets Officer" role. Also, make sure this AAD ID is allowed to login to the corresponding Azure Subscription.
- Add the following Secrets in the AKV. These are items you have already obtained from the above steps for each of the Azure Services.
  - Name <b>openai-api-key</b> & value obtained from above steps
  - Name <b>openai-endpoint</b> & value obtained from above steps
  - Name <b>openai-gpt-35-turbo-deployment-name</b> & value obtained from above steps
  - Name <b>openai-text-embedding-deployment-name</b> & value obtained from above steps
  - Name <b>openai-api-version</b> & value obtained from above steps
  - Name <b>content-safety-api-key</b> & value obtained from above steps
  - Name <b>content-safety-endpoint</b> & value obtained from above steps


