from openai import OpenAI
from typing import List, Dict


def chat_stream_openai(
    model:   str = 'gpt-3.5-turbo', 
    messages: List = []
    ) -> str:
    """
    Sends request and streams output to stdout.

    Parameters:
    - model
    - messages
    """
    client = OpenAI()
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    outputs: str = ""
    for chunk in stream:
        word = chunk.choices[0].delta.content or ""
        print(word, end="")
        outputs += word

    return ''.join(outputs)


def chat_processor_openai(
    model:   str = 'gpt-3.5-turbo', 
    messages: List = []
    ) -> str:
    """
    Sends request and retrieves output.
    NO STREAMING.

    Parameters:
    - model
    - messages
    """
    client = OpenAI()
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
    )
    outputs = chat_completion.choices[0].message.content
    return outputs
