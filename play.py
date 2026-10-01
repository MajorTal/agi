import os

import openai

from aws_private import secret


openai.api_key = secret("OPENAI_API_KEY", "openai-api-key")
assert openai.api_key


def demo():
    res = openai.Completion.create(
                model="text-davinci-002",
                prompt="my name is:",
                temperature=0.6,
            )
    print(res)




print("here")
if __name__ == "__main__":
    demo()