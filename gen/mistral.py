import transformers
import os
from threading import Thread
from hqq.engine.hf import HQQModelForCausalLM, AutoTokenizer
from hqq.core.quantize import *

from history import Conversation    # MMI modules


def chat_stream_mistral(
        conv_id, 
        chat, 
        max_new_tokens=100, 
        do_sample=True
    ):
    """
    Model I/O processor & output streamer.
    """
    model_id = '/srv/ai/dev/ultragency/ami-latest/mod/Mixtral'
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model     = HQQModelForCausalLM.from_quantized(model_id)

    ## Set backend/compile                                   Pick one for CUDA ↓
    #HQQLinear.set_backend(HQQBackend.ATEN_BACKPROP)         ## best for training
    HQQLinear.set_backend(HQQBackend.ATEN)                   ## best for inference

    tokenizer.use_default_system_prompt = False
    streamer = transformers.TextIteratorStreamer(tokenizer, 
                                                 timeout=10.0, 
                                                 skip_prompt=True, 
                                                 skip_special_tokens=True)

    generate_params = dict(
        tokenizer(chat, return_tensors="pt").to('cuda'),
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        top_p=0.90,
        top_k=50,
        temperature= 0.6,
        num_beams=1,
        repetition_penalty=1.2,
    )

    # global conv_id  # ↓ Create Conversation object (JSON)
    conv = Conversation(conv_id)

    output_path: str = os.path.join(conv.conv_dir, "stdout.md")
    if os.path.isfile(output_path):
        os.remove(output_path)

    t = Thread(target=model.generate, kwargs=generate_params)
    t.start()
    outputs = []
    for text in streamer:
        outputs.append(text)
        print(text, end="", flush=True)
        conv.stream_out(output_path, text)  ## Append each text piece as it comes
    
    return outputs
