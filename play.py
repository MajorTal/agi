import os

import openai


openai.api_key = os.getenv("OPENAI_API_KEY")

res = openai.Completion.create(
            model="text-davinci-002",
            prompt="my name is:",
            temperature=0.6,
        )

print(res)
