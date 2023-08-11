import logging
from config_reader import config
from providers.llm.remote_ob import RemoteLLM

logger = logging.getLogger(__name__)
llm_host = config.llm_host
assistant_mode = True


class RemoteLLamaCPP(RemoteLLM):
  async def generate(self, prompt, length=64, model_params={}, assist=True):
    if config.llm_remote_launch_process_automatically:
      self.run_llm_service()
    data = {
      'prompt': prompt,
      'max_length': length,
      'seed': -1,
      **model_params,
    }
    error, response = await super().remote_llm_api('POST', 'completion', data)
    if not error:
      logger.info(response)
      return False, prompt + response.get('content')
    else:
      return 'Error: ' + str(error), None

init = RemoteLLamaCPP