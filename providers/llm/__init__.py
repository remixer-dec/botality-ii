import importlib
gpt2_provider = lambda: importlib.import_module('providers.llm.gpt2_provider')
gptj_provider = lambda: importlib.import_module('providers.llm.gptj_provider')
llama_orig_provider = lambda: importlib.import_module('providers.llm.llama_orig_provider')
llama_hf_provider = lambda: importlib.import_module('providers.llm.llama_hf_provider')

ll_models = {
  'gpt2': gpt2_provider, 
  'gptj': gptj_provider, 
  'llama_orig': llama_orig_provider,
  'llama_hf': llama_hf_provider
}