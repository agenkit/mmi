import os, sys
from dotenv import load_dotenv
from typing import List, Dict
from PyQt5.QtWidgets import (
           QApplication,
           QDialog
)
from PyQt5.QtGui import (
           QFont, 
           QFontDatabase
)

from prompt    import InputDialog
from history   import Conversation, History
from gen.mistral   import chat_stream_mistral
from gen.openai    import chat_stream_openai
from gen.anthropic import chat_stream_anthropic

# TODO: see NOTE.md

load_dotenv()  # take environment variables from .env

OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise RuntimeError("API key not found. Set the OPENAI_API_KEY environment variable in `.env`.")

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if ANTHROPIC_API_KEY is None:
    raise RuntimeError("API key not found. Set the ANTHROPIC_API_KEY environment variable in `.env`.")


class MyBad(Exception):
    """
    An Exception-derived class to handle my bad coding or just work-in-progress.
    🔗 https://stackoverflow.com/questions/49224770
    Later on, we might make some error.py file but for now it's PO (premature…).
    """
    def __init__(self, msg='Error because of my code, not a real problem. Ignore for now.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
        # NOTE: super() alone returns a temporary object of the superclass
        #       that then allows you to call that superclass’s methods.


def generate(
             model: str, 
             conv: List[Dict[str, str]], 
             message: str, 
             max_new_tokens: int
            ):
    """
    Send a message request to model, with conv as context, 
    to generate a new message of maximum length.

    Parameters:
    - model: designation of the model
    - conv
    - message
    - max_new_tokens
    """
    prompt_templated = conv.to_template(model)

    match model:
        case 'mixtral 8x7b':
            outputs = chat_stream_mistral(
                conv.id, 
                prompt_templated, 
                max_new_tokens=max_new_tokens, 
                do_sample=True
            )
            return ''.join(outputs)

        case ('gpt-3.5-turbo' | 
              'gpt-4-turbo' |
              'gpt-4o'
        ):
            os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
            outputs = chat_stream_openai(
                model, 
                prompt_templated
            )
            return outputs

        case ('claude-3-opus-20240229' | 
              'claude-3-sonnet-20240229' | 
              'claude-3-haiku-20240307' |
              'claude-2.1' | 
              'claude-2.0' | 
              'claude-instant-1.2'
        ):
            os.environ['ANTHROPIC_API_KEY'] = ANTHROPIC_API_KEY
            outputs = chat_stream_anthropic(
                model=model, 
                system=conv.get_sysprompt(),
                messages=prompt_templated,
                max_tokens=max_new_tokens
                # temperature=
            )
            return outputs  # https://docs.anthropic.com/claude/reference/messages_post

        case _:
            raise MyBad('Probably made a mistake in model select here.')


def run():

    app = QApplication(sys.argv)
    font = QFont("SauceCodePro Nerd Font", pointSize=13, weight=QFont.Normal)
    app.setFont(font)

    dialog = InputDialog()
    dialog.show()

    result = dialog.exec_()  # Display the dialog and block until closed
    
    print(f'Exit code: {result}')
    if result != QDialog.Accepted:
        print("Exiting MMI.")
        raise sys.exit(0)
    else:
        (conv_id, 
         sysprompt, 
         user_prompt, 
         max_new_tokens,
         model
        ) = dialog.collect_inputs() 

    conv = Conversation(conv_id)

    if sysprompt != conv.get_sysprompt():
        conv.save(sysprompt, True)
        print(f'\n🡇 Updated system prompt 🡇\n\n{sysprompt}\n')

    if user_prompt and user_prompt != "":
        conv.save(user_prompt)
        outputs = generate(model, conv, user_prompt, max_new_tokens)
        conv.save(outputs)
    else:
        print(f'Empty user prompt: no generation.')


if __name__ == "__main__":
    run()
