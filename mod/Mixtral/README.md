---
license: apache-2.0
tags:
- moe
train: false
inference: false
pipeline_tag: text-generation
---
## Mixtral-8x7B-Instruct-v0.1-hf-attn-4bit-moe-2bitgs8-metaoffload-HQQ
This is a version of the 
<a href="https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1"> Mixtral-8x7B-Instruct-v0.1 model</a> quantized with a mix of 4-bit and 2-bit via Half-Quadratic Quantization (HQQ). More specifically, the attention layers are quantized to 4-bit and the experts are quantized to 2-bit. 

This model was designed to get the best quality at a budget of ~13GB of VRAM. It reaches an impressive <b>70.01</b> LLM leaderboard score, not too far from the original model's <b>72.62</b>.

![image/gif](https://cdn-uploads.huggingface.co/production/uploads/636b945ef575d3705149e982/-gwGOZHDb9l5VxLexIhkM.gif)

----------------------------------------------------------------------------------------------------------------------------------
</p>

## Performance
| Models            | Mixtral Original | HQQ quantized    |
|-------------------|------------------|------------------|
| Runtime VRAM      | 94 GB            | <b>13.6 GB</b>     |  
| ARC (25-shot)     | 70.22            | 68.26            |
| Hellaswag (10-shot)|     87.63       |   85.73         |
| MMLU (5-shot)      |      71.16      |  68.69          |
| TruthfulQA-MC2    | 64.58            | 64.52            |
| Winogrande (5-shot)| 81.37           | 80.19            |
| GSM8K (5-shot)|      60.73      |        52.69    |
| Average|   72.62         |  70.01         |

### Basic Usage
To run the model, install the HQQ library from https://github.com/mobiusml/hqq and use it as follows:
``` Python
import transformers 
from threading import Thread

model_id = 'mobiuslabsgmbh/Mixtral-8x7B-Instruct-v0.1-hf-attn-4bit-moe-2bitgs8-metaoffload-HQQ'
#Load the model
from hqq.engine.hf import HQQModelForCausalLM, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)
model     = HQQModelForCausalLM.from_quantized(model_id)

#Optional: set backend/compile
#You will need to install CUDA kernels apriori
# git clone https://github.com/mobiusml/hqq/
# cd hqq/kernels && python setup_cuda.py install
from hqq.core.quantize import *
HQQLinear.set_backend(HQQBackend.ATEN_BACKPROP)


def chat_processor(chat, max_new_tokens=100, do_sample=True):
    tokenizer.use_default_system_prompt = False
    streamer = transformers.TextIteratorStreamer(tokenizer, timeout=10.0, skip_prompt=True, skip_special_tokens=True)

    generate_params = dict(
        tokenizer("<s> [INST] " + chat + " [/INST] ", return_tensors="pt").to('cuda'),
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        top_p=0.90,
        top_k=50,
        temperature= 0.6,
        num_beams=1,
        repetition_penalty=1.2,
    )

    t = Thread(target=model.generate, kwargs=generate_params)
    t.start()
    outputs = []
    for text in streamer:
        outputs.append(text)
        print(text, end="", flush=True)

    return outputs

################################################################################################
#Generation
outputs = chat_processor("How do I build a car?", max_new_tokens=1000, do_sample=False)
```


### Quantization

You can reproduce the model using the following quant configs:

``` Python
from hqq.engine.hf import HQQModelForCausalLM, AutoTokenizer

model_id  = "mistralai/Mixtral-8x7B-Instruct-v0.1"
model     = HQQModelForCausalLM.from_pretrained(model_id, use_auth_token=hf_auth, cache_dir=cache_path)

#Quantize params
from hqq.core.quantize import *
attn_prams     = BaseQuantizeConfig(nbits=4, group_size=64, offload_meta=True) 
experts_params = BaseQuantizeConfig(nbits=2, group_size=8, offload_meta=True)

zero_scale_group_size                              = 128
attn_prams['scale_quant_params']['group_size']     = zero_scale_group_size
attn_prams['zero_quant_params']['group_size']      = zero_scale_group_size
experts_params['scale_quant_params']['group_size'] = zero_scale_group_size
experts_params['zero_quant_params']['group_size']  = zero_scale_group_size

quant_config = {}
#Attention
quant_config['self_attn.q_proj'] = attn_prams
quant_config['self_attn.k_proj'] = attn_prams
quant_config['self_attn.v_proj'] = attn_prams
quant_config['self_attn.o_proj'] = attn_prams
#Experts
quant_config['block_sparse_moe.experts.w1'] = experts_params
quant_config['block_sparse_moe.experts.w2'] = experts_params
quant_config['block_sparse_moe.experts.w3'] = experts_params

#Quantize
model.quantize_model(quant_config=quant_config, compute_dtype=torch.float16);
model.eval();
```
