import openai
import sys

from azure_openai_setup import get_openai_client, set_openai_config, get_chat_completion

# Get OpenAI creds based on the OS environment variable 
# OPENAI_AUTH_TYPE
# = KeysFromEnv => get the credentials from OS env
# = KeysFromAKVWithCLIAuth => get the credentials from Azure Key Vault with CLI Auth
# = KeysFromAKVWithMI => get the credentials from Azure Key Vault with Managed Identity
# = KeysFromManagedId => authenticate with Managed Identity and get access to Azure Open AI

THE_MODEL = 'gpt-35-turbo-16k'
endpoint, key, version = set_openai_config()
#print(f"{endpoint}, {key}, {version}")
status, client = get_openai_client(aoai_endpoint = endpoint, 
                                   aoai_api_key = key, 
                                   aoai_version = version
                                  )
print(f"Connecting to Open AI returned status as {status}")

text = f"""
My ancestral home is in Mars. I mean the planet Mars that \
is in our Solar System. I spent my childhood there with my parents. \
As a child I used to play with Martian rocks. \
I moved to Earth when I was a teenager. \
I have a few friends on Earth who are cool. \
Though I miss my friends from Mars. \
Do you think people on Earth and people on Mars can be friends? \
Have you ever met with people from planets other than Mars? \
I know there are nice people in the moons of Jupiter. But they are so far away \
that it is difficult to communicate with them over WhatsApp, Facebook, Teams, Cell Phones or any other App! \
Once I wanted to purchase a 10 mg black pearl over Amazon from Europa, the moon of Jupiter. They said it will take \
10 years to deliver it. However, if I have Amazon Prime it might be possible to deliver in 5 years. \
That is too long a wait time for me to get the black pearl. \
So I checked with Disney. They said they have the black pearl from their \
Pirates of the Carribean (Curse of the Black Pearl) movie at their Studio. \
They can ship it overnight. But it will cost $ 1million.
"""
prompt = f"""Summarize the text delimited by triple backticks in three sentences. \
```{text}``` \
"""
print(f'-----------------------\nPrompt::\n{prompt}\n-----------------------')
my_prompt = [
              {
                "role": "user", 
                "content": f"{prompt}"
                }
              ]      
tokens_used, finish_reason, completion = get_chat_completion(
                                                the_client=client, 
                                                the_model=THE_MODEL,
                                                the_messages=my_prompt)
#print(f"Completion: {completion}\nTokens used: {tokens_used}\nFinish Reason: {finish_reason}")
print(f'-----------------------\nCompletion::\n{completion}\n-----------------------')