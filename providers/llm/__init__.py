import importlib
gpt2_provider = lambda: importlib.import_module('providers.llm.pytorch.gpt2_provider')
gptj_provider = lambda: importlib.import_module('providers.llm.pytorch.gptj_provider')
cerebras_gpt_provider = lambda: importlib.import_module('providers.llm.pytorch.cerebras_gpt')
llama_orig_provider = lambda: importlib.import_module('providers.llm.pytorch.llama_orig_provider')
llama_hf_provider = lambda: importlib.import_module('providers.llm.pytorch.llama_hf_provider')
mlc_chat_prebuilt_provider = lambda: importlib.import_module('providers.llm.mlc_chat_prebuilt_provider')
llama_cpp_provider = lambda: importlib.import_module('providers.llm.llama_cpp_provider')
remote_ob_provider = lambda: importlib.import_module('providers.llm.remote_ob')

pytorch_models = {
  'gpt2': gpt2_provider, 
  'gptj': gptj_provider, 
  'cerebras_gpt': cerebras_gpt_provider,
  'llama_orig': llama_orig_provider,
  'llama_hf': llama_hf_provider,
}

external_backends = {
  'llama_cpp': llama_cpp_provider,
  'mlc_pb': mlc_chat_prebuilt_provider,
  'remote_ob': remote_ob_provider
}