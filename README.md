☢️ This is a frozen, unfinished, experimental project. Use at your own risk ☢️  
(maybe do yourself a favor and just don't 😅)  
🡆 Use [`llm`](https://github.com/simonw/llm) by Simon Willison instead)

> *Written in Dec '23 ~ Jan '24, mostly.*  
> *Now deprecated.*

# MMI: Model Meta-Interface

MMI, the Model Meta-Interface, is a concept prototype for an application that acts as a universal controller for multiple LLMs.

**It's very lacking, and only has `max_tokens` exposed in the GUI.**  
**Some of the code is ugly, hasn't been cleaned, etc.**  
**It's a mess because I didn't have much of a plan. Just glued things together naively, quickly.**

----

## Requirements

- Requires Qt (tested on Debian 12 + KDE).
- Requires API keys for OpenAI and Anthropic.
- I haven't built `requirements.txt`. You'll have to inspect files to see what's what (`main.py`, `prompt.py`, `history.py`, and files in `gen/`).
- If you want to use Mixtral, it requires a manual download to be placed in `mod/Mixtral`. For instance:
  - 🔗 [`Mixtral-8x7B-Instruct-v0.1-hf-attn-4bit-moe-2bitgs8-metaoffload-HQQ`](https://huggingface.co/mobiuslabsgmbh/Mixtral-8x7B-Instruct-v0.1-hf-attn-4bit-moe-2bitgs8-metaoffload-HQQ)
  - I've removed the `qmodel.pt` file (22.5 GiB) but everything comes from that repo.
  - There might be additional steps to setup HQQ, see the model's card on HF. Generally, Python will tell you what's missing.

## Setup

It's not exactly straightforward, there are two major steps prior to launch: add your API keys, and edit the bash script with your preferred Python path.

Preparation:

- Clone this repo, `cd` into it.
- Edit `launch.sh` to set your own Python path (mine is `miniconda3`).
- If you need Mixtral, see below.
- Create a file named `.env` in the root folder.
- Edit it and add your API keys for OpenAI and Anthropic:

```sh
OPENAI_API_KEY = "…"
ANTHROPIC_API_KEY = "…"
```

Use:

- Launch GUI with `launch.sh` (or alternatively `python main.py`).
- Outputs are streamed to `stdout` (if started with `launch.sh`)
- Conversations are saved as plain text files (see notes below). No db.
- Re-launch for each new message.
- Re-select a conversation to continue it. (top-left dropdown menu) 
  - The system prompt will automatically refresh.
- To create a new conversation, type its name in the top-right text field (it takes precedence over the dropdown menu to the left). 

## How it works

- MMI lets you run linear conversations with multiple LLMs, each new message sending the whole history to keep context.
- Conversations are stored in `history/context/CONVERSATION_NAME` 
  - In `conv.json`
  - as individual `.md` files, one per message.
    - you may browse them using MKDocs or equivalent.
    - odd-numbered files are user messages; even-numbered are LLM outputs.
- When creating a new conversation, you may select an existing one first to retrieve its system prompt, then enter a new name.
- Editing `.md` files does NOT affect conversations (it's a one-way dump to disk). You want to edit `conv.json` to alter MMI's flow.
- `stdout.md` should self-explanatorily contain the last output (easy to monitor just that and keep the conversation running).
- system prompt is a bit finicky, avoid changing during a conversation.
- for convenience upon opening it, it will paste your clipboard content in the message text field.


## missing

Lots of missing features:

- No threading/parallel mode to compare LLM outputs.
- No easy way to edit conversations

For now, there is no "agency" to speak of, only the usual APIs: OpenAI, Anthropic. Optionally, it can run Mixtral 7x8B on a 24 GB GPU using HQQ.


## parting words

This project will likely not evolve anymore, as I've discovered Simon Willison's `llm` since and I'd rather build upon his brilliant project than waste time & energy redoing it worse.

I'm putting it here merely for reference (and lol later) and to test my git tags/release scripts. I've since learned much more about what already exists in the LLM tooling space, what needs to be done to improve such tools (and which should be custom-made). I have a much tighter vision to execute now. This also was initially a fun experiment to make a super basic Qt app; it should have been a pure CLI app otherwise.
