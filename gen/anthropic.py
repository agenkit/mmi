import anthropic
from typing import List, Dict


def chat_stream_anthropic(
    model: str = 'claude-instant-1.2', 
    system: str = '',
    messages: List = [],
    max_tokens: int = 1000,
    temperature: int = 0,
    ):
    client = anthropic.Anthropic()

    outputs: str = ""
    with client.messages.stream(
        model       = str(model),
        max_tokens  = int(max_tokens),
        system      = str(system),
        messages    = messages,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            outputs += text

    return ''.join(outputs)


def chat_processor_anthropic(
    model: str = 'claude-instant-1.2', 
    system: str = '',
    messages: List = [],
    max_tokens: int = 1000,
    temperature: int = 0,
    ):

    client = anthropic.Anthropic()
    message = client.messages.create(
        model       = str(model),
        max_tokens  = int(max_tokens),
        system      = str(system),
        messages    = messages,
    )
    outputs = message.content[0].text
    return outputs
