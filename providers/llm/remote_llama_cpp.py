# reference: https://github.com/ggerganov/llama.cpp/blob/master/examples/server/README.md
import logging
from config_reader import config
from providers.llm.remote_ob import RemoteLLM

logger = logging.getLogger(__name__)
llm_host = config.llm_host


class RemoteLLamaCPP(RemoteLLM):
  visual_mode = True
  async def generate(self, prompt, length=64, model_params={}, assist=True):
    if config.llm_remote_launch_process_automatically:
      await self.run_llm_service()
    data = {
      'prompt': prompt,
      'n_predict': length,
      'seed': -1,
      **model_params,
    }
    base64_data_url_offset = 22
    if 'visual_input' in data and data['visual_input']:
      data['image_data'] = [{'data': data['visual_input'][base64_data_url_offset:]}]
      del data['visual_input']
    if 'stop_tokens' in self.init_config:
      data['stop'] = ['</s>', *self.init_config['stop_tokens']]

    error, response = await super().remote_llm_api('POST', 'completion', data)
    if not error:
      logger.info(response)
      return False, prompt + response.get('content')
    else:
      return 'Error: ' + str(error), None

init = RemoteLLamaCPP