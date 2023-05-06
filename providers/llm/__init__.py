import importlib
gpt2_provider = lambda: importlib.import_module('providers.llm.gpt2_provider')
gptj_provider = lambda: importlib.import_module('providers.llm.gptj_provider')
cerebras_gpt_provider = lambda: importlib.import_module('providers.llm.cerebras_gpt')
llama_orig_provider = lambda: importlib.import_module('providers.llm.llama_orig_provider')
llama_hf_provider = lambda: importlib.import_module('providers.llm.llama_hf_provider')
mlc_chat_prebuilt_provider = lambda: importlib.import_module('providers.llm.mlc_chat_prebuilt_provider')
llama_cpp_provider = lambda: importlib.import_module('providers.llm.llama_cpp_provider')
ll_models = {
  'gpt2': gpt2_provider, 
  'gptj': gptj_provider, 
  'cerebras_gpt': cerebras_gpt_provider,
  'llama_orig': llama_orig_provider,
  'llama_hf': llama_hf_provider,
  'llama_cpp': llama_cpp_provider,
  'mlc_pb': mlc_chat_prebuilt_provider
}