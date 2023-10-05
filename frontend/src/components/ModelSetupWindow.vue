<script setup>
import { reactive } from 'vue'
import { api } from '../tools'
import locale from '../locale'
import { FvlSelect, FvlForm, FvlInput, FvlSearchSelect } from '@/libs/formvuelar'

const props = defineProps(['modelConfig'])
const showConfirmAlert = ref(false)
const modelLoadingInProgress = ref(false)
let model = props.modelConfig || {}
const options = { SO_VITS_SVC: 'SO_VITS_SVC', VITS: 'VITS', GGUF: 'GGUF' }
model._type = (model._type || options[0])

const ttsModels = { SO_VITS_SVC: true, VITS: true }
const stsModels = { SO_VITS_SVC: true }
const llModels = { GGUF: true }
if (model._type in ttsModels)
  model.installPath = '$TTS_PATH/'
if (model._type === 'GGUF') {
  model.installPath = '$path_to_llama_cpp_weights_dir'
  model.quant = '2_K'
}
model = reactive({ ...model })

const { proxy } = getCurrentInstance()
function reportError(text) {
  proxy.$root.$emit('showNotification', { message: text, type: 'error' })
}

function runInstall() {
  if (!model._type) return
  if (model._type === 'SO_VITS_SVC' && !model.baseVoice) return reportError(locale.no_base_voice)
  if (model.path.length > 0 && !(model.path.endsWith('/'))) return reportError(locale.wrong_repo_format)
  if (typeof (model.rename) === 'undefined' && model._type === 'VITS') model.rename = true
  api('POST', `models/install/${model._type}`, { body: JSON.stringify(model), headers: { 'content-type': 'application/json' } })
    .then((r) => {
      if (!r.response)
        throw new Error(r.error)
      const task_id = r.response.task_id
      const taskCheckInterval = setInterval(() => {
        api('GET', `models/install/${task_id}`).then((j) => {
          if (!j.response)
            throw new Error(j.error)
          switch (j.response.status) {
            case 'not found':
            case 'error':
              modelLoadingInProgress.value = false
              clearInterval(taskCheckInterval)
              throw new Error(j.response.error || 'Task not found')
            case 'running':
              break
            case 'done':
              modelLoadingInProgress.value = false
              clearInterval(taskCheckInterval)
              proxy.$root.$emit('showNotification', { message: locale.model_installed })
              proxy.$root.$emit('hideModal')
              proxy.$root.$emit('refreshModels')
          }
        }).catch(reportError)
      }, 10000)
      modelLoadingInProgress.value = true
    })
    .catch(reportError)
    .finally(() => {
      showConfirmAlert.value = false
    })
  showConfirmAlert.value = true
}
</script>

<template>
  <div>
    <FvlForm :data="model" url="#" class="relative">
      <FvlInput name="repo" :label="locale.hf_repo" type="text" :value.sync="model.repo" />
      <FvlSelect
        :label="locale.model_type"
        name="type"
        :placeholder="locale.model_type"
        :selected.sync="model._type"
        :options="options"
        :disabled="props.modelConfig ? true : false"
      />
      <FvlInput name="path" :label="locale.repo_path" type="text" :value.sync="model.path" />
      <FvlInput name="installPath" :label="locale.install_path" type="text" :value.sync="model.installPath" />
      <FvlInput name="model" :label="locale.model_filename" type="text" :value.sync="model.model" />
      <FvlInput v-if="model._type in ttsModels" name="voice" :label="locale.voice" type="text" :value.sync="model.voice" />
      <FvlSelect
        v-if="model.quants"
        :label="locale.quant"
        name="Quantization"
        :placeholder="locale.quant"
        :selected.sync="model.quant"
        :options="model.quants.reduce((prev, cur) => { prev[cur] = cur; return prev }, {})"
      />
      <FvlSearchSelect
        v-if="model._type in stsModels"
        name="baseVoice"
        :requred="true"
        :label="locale.base_voice"
        type="text"
        :selected.sync="model.baseVoice"
        :lazy-load="true"
        response-data-path="response"
        options-url="/api/voices"
        option-key="voice"
        option-value="voice"
        :search-keys="['voice']"
      />
      <span v-if="showConfirmAlert" class="text-orange-400 inline-block m-2">{{ locale.confirm_install }}</span>
      <span v-if="modelLoadingInProgress" class="animate-spin inline-flex justify-center align-middle m-2"><hi-spinner-earring /></span>
      <span v-if="!(showConfirmAlert || modelLoadingInProgress)" class="fvl-submit-button m-2 inline-block cursor-pointer bg-opacity-70 float-right" @click="runInstall">
        <span class="fvl-submit-text">{{ locale.install }}</span>
      </span>
    </FvlForm>
  </div>
</template>
