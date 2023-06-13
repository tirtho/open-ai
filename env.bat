@echo off
SET PYTHONPATH=%cd%\AzureOpenAIHelperFunctions
SET OPENAI_ENDPOINT=https://myopenaiinstance.openai.azure.com/
SET OPENAI_KEY=1234xxxx1234
SET OPENAI_API_VERSION=2023-03-15-preview

REM The options for Azure OpenAI Auth are KeysFromEnv, KeysFromAKVWithMI, KeysFromAKVWithCLIAuth, KeysFromManagedId
SET OPENAI_AUTH_TYPE=KeysFromAKVWithCLIAuth
SET KEY_VAULT_URL=https://prod-core-key-vault.vault.azure.net/