import openai
import sys

from azure_openai_setup import set_openai_config, get_completion

# Get OpenAI creds based on the OS environment variable 
# OPENAI_AUTH_TYPE
# = KeysFromEnv => get the credentials from OS env
# = KeysFromAKVWithCLIAuth => get the credentials from Azure Key Vault with CLI Auth
# = KeysFromAKVWithMI => get the credentials from Azure Key Vault with Managed Identity
# = KeysFromManagedId => authenticate with Managed Identity and get access to Azure Open AI
set_openai_config()

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
response = get_completion(prompt)
print(f'-----------------------\nCompletion::\n{response}\n-----------------------')