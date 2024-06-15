import os, json#, pprint
from datetime import datetime
from typing import List, Dict
from pprint import pprint

sysprompt = """You are a diligent, productive, very sharp programmer. You love explaining your code and mentoring others. You don't hesitate to say "I don't know." You are well-liked by your peers, and shine in teams, because your code is generally simple, easy to read, and understand."""
# sysprompt = """You are an expert machine learning (ML) engineer, and a productive, efficient, very sharp programmer."""




class History:
    """
    Handles basic info and methods for history features.

    TODO: make it a super() to call it without instantiation (it's always the same, just needs refresh)
    """
    def __init__(self, dir: str = None):
        if dir is None:
            # Get the directory path of the main.py file
            main_dir: str = os.path.dirname(os.path.abspath(__file__))
            self.dir = os.path.join(main_dir, "context/history")
        else:
            self.dir = dir

    def list_conversations(self, dir: str = None):
        """List all subdirectories in the given base path."""
        if dir is None:
            dir = self.dir

        try:
            return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]
        except FileNotFoundError:
            return []




class Conversation:
    """
    Contains all the history and meta to manage single conversations.
    """
    def __init__(self, conv_id: str = "test_01"):
        context = History()

        self.id:        str = conv_id
        self.conv_dir:  str = os.path.join(context.dir, conv_id)
        self.json_path: str = os.path.join(self.conv_dir, 'conv.json')

        self.messages:  List[Dict[str, str]] = []
        
        if not os.path.exists(self.conv_dir):
            os.makedirs(self.conv_dir)
            with open(self.json_path, 'w') as f:
                json.dump(self.messages, f)
        else:
            self.messages = self.load()




    def load(self) -> List[Dict[str, str]]:
        """
        Loads and returns all messages from the JSON file.
        """
        try:
            with open(self.json_path, 'r') as f:
                self.messages = json.load(f)
            return self.messages

        except FileNotFoundError:
            print(f"File {self.json_path} not found.")
            return []

        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.json_path}.")
            return []




    def save(self, message: str, sysprompt: bool = False) -> None:
        """
        Saves a new message to the JSON file, and as a standalone markdown file.
        Add 2nd argument "True" to implicitly call set_sysprompt(message).
        """
        if not sysprompt:
            timestamp: str = datetime.now().strftime('%y%m%d_%H%M%S_%f')
            self.messages.append({timestamp: message})
            self.save_json(self.messages)
            self.save_md(message)

        elif sysprompt:
            self.set_sysprompt(message)

        else:
            raise MyBad('Conversation.save threw some error. Did you specify a wrong argument for sys? True|False')




    def save_json(self, messages: List[Dict[str, str]]) -> None:
        """
        Saves messages to .json file (already created at __init__).
        """
        with open(self.json_path, 'w') as f:
            json.dump(self.messages, f, indent=4)
        



    def save_md(self, message: str, sysprompt: bool = False) -> None:
        """
        Saves the latest `message` as `.md` file.
        Uses `len(conv.messages)` to get index number, so make sure it's updated."""

        if sysprompt:
            filename: str = os.path.join(self.conv_dir, "system.md")
            intro = f'### SYSTEM PROMPT\n\n**Timestamp: 0**\n\n'

        else:
            index = len(self.messages) - 1
            filename: str = os.path.join(self.conv_dir, f"{index:04d}.md")
            timestamp: str = datetime.now().strftime('%y%m%d_%H%M%S_%f')
            intro = f'### Message {index}\n\n**Timestamp: {timestamp}**\n\n'

        with open(filename, 'w') as md:
            md.write(intro + message)




    def get_sysprompt(self) -> str:
        """
        Retrieves the System Prompt (first item).

        Parameters:
        - new_value (str): The new value to set for the key '0'.
        """
        if self.messages != [] and '0' in self.messages[0]:
            return self.messages[0]['0']




    def set_sysprompt(self, message: str = sysprompt) -> None:
        """
        Sets the message (or default if empty) as System Prompt.

        Parameters:
        - message (str): The new value to set for the key '0'.
        """
        self.messages.insert(0, {'0': message})
        self.sysprompt: str = message
        self.save_json(self.messages)
        self.save_md(message, True)




    def save_md_structure(self, messages) -> None:
        """
        Saves messages to .md file; creates it if necessary. 
        Sort of deprecated, prefer using the simpler save_md(message).
        """
        for i, message in enumerate(self.messages):
            filename: str = os.path.join(self.conv_dir, f"{i:04d}.md")

            if not os.path.exists(filename):

                with open(filename, 'w') as md:
                    for key, value in message.items():
                        md.write(f"### Message {i}\n\nTimestamp: {key}\n\n{value}")




    def stream_out(self, output_path, message: str) -> None:
        """
        Writes streamer output to a Markdown file in real-time.
        Uses 'a' mode for appending.
        """
        with open(output_path, 'a') as md:
            md.write(message)




    def to_template(self, 
        model: str = 'mistral'
        ):
        """
        Assembles a full templated prompt, with context/history, optionally system prompt, ready to tokenize.

        Parameters:
        - model: Which model to template for.
        """
        match model:
            case 'mixtral 8x7b':
                return self.prompt_template_mistral()

            case ('gpt-3.5-turbo' | 
                  'gpt-4-turbo' |
                  'gpt-4o'
            ):
                return self.prompt_template_openai()

            case ('claude-3-opus-20240229' | 
                  'claude-3-sonnet-20240229' | 
                  'claude-3-haiku-20240307' |
                  'claude-2.1' | 
                  'claude-2.0' | 
                  'claude-instant-1.2'
            ):
                return self.prompt_template_anthropic()




    def prompt_template_mistral(self, 
        model: str = 'mistral'
        ) -> str:
        """
        Transforms self.messages into a string compliant with the Mistral chat template.
        """
        # <s> is a special token for beginning of string (BOS)
        history: str = "<s>"

        #      ↓ Dict[str, str]
        for i, message in enumerate(self.messages):
            for content in message.values():
                if i == 0:       # System prompt
                    history += " [INST] " + content + "\n"

                elif i == 1:     # handle special case 1, follows 0.
                    history += content + " [/INST] "

                elif i % 2 == 1: # User message (generic case)
                    history += " [INST] " + content + " [/INST] "

                else:            # Assistant message (generic)
                    history += content + "</s>"

        return history




    def prompt_template_openai(self, 
        model: str = "gpt-3.5-turbo"
        ) -> List:
        """
        Transforms self.messages into a JSON-compliant object for the OpenAI chat template.
        """
        messages_template = []
        for i, message in enumerate(self.messages):
            for content in message.values():
                if i == 0:   # System prompt
                    messages_template.insert(i, 
                        {"role": "system", "content": content}
                    )
                elif i%2==1: # User message
                    messages_template.insert(i, 
                        {"role": "user", "content": content}
                    )
                else:        # Assistant message
                    messages_template.insert(i, 
                        {"role": "assistant", "content": content}
                    )
        return messages_template




    def prompt_template_anthropic(self, 
        model: str = "claude-instant-1.2"
        ) -> List:
        """
        Transforms self.messages into a JSON-compliant object for the Anthropic chat template.
        """
        messages_template = []
        for i, message in enumerate(self.messages):
            for content in message.values():
                if i == 0:   # System prompt
                    pass # Do nothing, in Anthropic it's at the messages level.
                elif i%2==1: # User message
                    messages_template.insert(i, {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": content
                            }
                        ]
                    }
                    )
                else:        # Assistant message
                    messages_template.insert(i, {
                        "role": "assistant", 
                        "content": [
                            {
                                "type": "text",
                                "text": content
                            }
                        ]
                    }
                    )
        return messages_template



