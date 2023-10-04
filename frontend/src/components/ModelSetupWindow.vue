<script setup>
import { FvlSelect, FvlForm, FvlInput, FvlSearchSelect } from 'formvuelar'
import { reactive } from 'vue'
import { api } from '../tools'

const props = defineProps(['modelConfig'])
const showConfirmAlert = ref(false)
const modelLoadingInProgress = ref(false)
let model = props.modelConfig || {}
model.installPath = '$TTS_PATH/'
const options = { SO_VITS_SVC: 'SO_VITS_SVC', VITS: 'VITS' }
model._type = (model._type || options[0])

const ttsModels = { SO_VITS_SVC: true, VITS: true }
const stsModels = { SO_VITS_SVC: true }

model = reactive({ ...model })
const { proxy } = getCurrentInstance()
function reportError(text) {
  proxy.$root.$emit('showNotification', { message: text, type: 'error' })
}

function runInstall() {
  if (!model._type) return
  if (model._type === 'SO_VITS_SVC' && !model.baseVoice) return reportError('Base voice is required for voice-to-voice models')
  if (model.path.length > 0 && !(model.path.endsWith('/'))) return reportError('Repo path must end with a slash')
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
              proxy.$root.$emit('showNotification', { message: '✅ Model installed!' })
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
      <FvlInput name="repo" label="HuggingFace Repo" type="text" :value.sync="model.repo" />
      <FvlSelect
        label="Model type"
        name="type"
        placeholder="Model type"
        :selected.sync="model._type"
        :options="options"
        :disabled="props.modelConfig ? true : false"
      />
      <FvlInput name="path" label="Repo path" type="text" :value.sync="model.path" />
      <FvlInput name="installPath" label="Install path" type="text" :value.sync="model.installPath" />
      <FvlInput name="model" label="Model name" type="text" :value.sync="model.model" />
      <FvlInput v-if="model._type in ttsModels" name="voice" label="Voice" type="text" :value.sync="model.voice" />
      <FvlSearchSelect
        v-if="model._type in stsModels"
        name="baseVoice"
        :requred="true"
        label="Base voice"
        type="text"
        :selected.sync="model.baseVoice"
        :lazy-load="true"
        response-data-path="response"
        options-url="/api/voices"
        option-key="voice"
        option-value="voice"
        :search-keys="['voice']"
      />
      <span v-if="showConfirmAlert" class="text-orange-400 inline-block m-2">Please confirm the installation in the terminal!</span>
      <span v-if="modelLoadingInProgress" class="animate-spin inline-flex justify-center align-middle m-2"><hi-spinner-earring /></span>
      <span v-if="!(showConfirmAlert || modelLoadingInProgress)" class="fvl-submit-button m-2 inline-block cursor-pointer bg-opacity-70 float-right" @click="runInstall">
        <span class="fvl-submit-text">Install</span>
      </span>
    </FvlForm>
  </div>
</template>
