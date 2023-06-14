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

### Prerequisites
You need 
- [Python 3.x](https://www.python.org/)
  -   Your Python installation should include [pip](https://pip.pypa.io/en/stable/)
- Azure Subscription with enough permissions to 
  - [Create Azure Open AI Service](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/overview)
  - [Create Azure AI Content Safety Service](https://learn.microsoft.com/en-us/azure/cognitive-services/content-safety/overview)
  - [Create or 'Key Vault Secrets Officer' access rights to Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/overview)
- [Jupyter Notebook](https://docs.jupyter.org/en/latest/install/notebook-classic.html)

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
- You will find instructions [here](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal)
#### Azure AI Content Safety API 
This is needed if you want to run the  notebooks under ResponsibleAI. Otherwise skip this section.
- Create and instance of Azure Content Safety
- Note down 
  - The API key as <b>content-safety-api-key</b>
  - The API Endpoint as <b>content-safety-endpoint</b>
- You will find instructions [here](https://learn.microsoft.com/en-us/azure/cognitive-services/content-safety/overview)
#### Azure Key Vault
- Create an Azure Key Vault (AKV) in your subscription. You will find instructions [here](https://learn.microsoft.com/en-us/azure/key-vault/general/quick-create-portal)
- In the AKV add your Azure Active Directory (AAD) ID with the <b>Key Vault Secrets Officer</b> role. Also, make sure this AAD ID is allowed to login to the corresponding Azure Subscription.
- Add the following Secrets in the AKV. These are items you have already obtained from the above steps for each of the Azure Services.
  - Name <b>openai-api-key</b> & value obtained from above steps
  - Name <b>openai-endpoint</b> & value obtained from above steps
  - Name <b>openai-gpt-35-turbo-deployment-name</b> & value obtained from above steps
  - Name <b>openai-text-embedding-deployment-name</b> & value obtained from above steps
  - Name <b>openai-api-version</b> & value obtained from above steps
  - Name <b>content-safety-api-key</b> & value obtained from above steps
  - Name <b>content-safety-endpoint</b> & value obtained from above steps
#### Authentication
In order to run the APIs you need to authenticate either with secrets or Managed Identity.
In our default scenario, you have stored all your API keys in AKV in the previous step.
Now, you need to authenticate to AKV with with your AAD credentials or with Managed Identity, to read those API keys.
For authentication mode, in your OS set the environment variable <b>OPENAI_AUTH_TYPE</b> to the value
  - <i>KeysFromAKVWithCLIAuth</i> if you are going to authenticate to Azure with your default credentials from CLI
  - <i>KeysFromAKVWithMI</i> if you are going to authenticate to Azure with your Managed Identity. In this case, you need to make sure your Managed Identity has <b>Key Vault Secrets Officer</b> role in your AKV. 
#### Python packages
- pip install azure-ai-contentsafety
- pip install azure-identity
- pip install azure-keyvault, azure-keyvault-certificates, azure-keyvault-keys, azure-keyvault-secrets
- pip install openai
- pip install numpy, num2words, pandas, matplotlib, scipy, scikit-learn, tiktoken
### Operation
Opem a CommandPromt/terminal/shell and go to the open-ai folder from this code-base.
In your OS set the environment variables
- <b>KEY_VAULT_URL</b> to the value from the AKV instance
- <b>OPENAI_AUTH_TYPE</b> to KeysFromAKVWithCLIAuth
- <b>PYTHONPATH</b> to <i>%cd%\AzureOpenAIHelperFunctions</i> for Windows (or ./AzureOpenAIHelperFunctions for Linux)
An example env.bat file is availble here in this codebase as well.

Make sure you have logged in to Azure from command line or from a browser.

Now, to run the notebooks, run 
> jupyter notebook

This will open up Jupyter Notebook and display all the folders where you have notebooks.

If you do not want to run the notebooks, but the python codes in the PythonCommandLine folder, go to that folder and run
the python files from there.

