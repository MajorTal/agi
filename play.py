import os

import openai


openai.api_key = os.getenv("OPENAI_API_KEY")
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