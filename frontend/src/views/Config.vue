<script setup>
import { FvlSelect, FvlForm } from 'formvuelar'
import { api } from '../tools'
import { globalState } from '../state'

const notification = ref(null)
const reductor = (pr, cur) => {
  if ('length' in pr)
    pr.push({ value: cur })
  else
    pr[cur] = cur
  return pr
}

class ConfigItem {
  constructor(schema) {
    this.item = reactive({ value: null, options: null })
    switch (schema.type) {
      case 'boolean':
        this.item.type = Boolean
        break
      case 'string':
        this.item.type = 'text'
        if (schema.enum)
          this.item.type = 'select'
        break
      case 'integer':
      case 'number':
        this.item.type = 'slider'
        break
      case 'array':
      case 'object':
        this.item.type = 'list'
        if (schema.enum || schema?.items?.enum)
          this.item.type = 'tags'
        break
      default:
        console.log(schema.type)
    }
  }
}

function syncConfigOption(target, option, config, schema) {
  const item = target[option]
  target[option] = item === undefined ? new ConfigItem(schema[option]).item : item

  const options = schema[option].enum || schema[option]?.items?.enum || target[option].options
  if (options)
    target[option].options = options.reduce(reductor, schema[option].type === 'array' ? [] : {})
  target[option].value = schema[option].type === 'integer' ? String(config[option]) : config[option]
}

function syncConfigOptions(options, target, config, schema) {
  if (typeof options == 'string') {
    const prefix = options
    options = []
    for (const key in schema) {
      if (key.startsWith(prefix))
        options.push(key)
    }
  }
  for (const key of options)
    syncConfigOption(target, key, config, schema)
}

let isRefreshing = false
async function refreshData() {
  isRefreshing = true
  const schema = await api('GET', 'schema')
  const config = await api('GET', 'config')
  const env = await api('GET', 'bot/env')
  const botConfigKeys = ['ignore_mode', 'threaded_initialization', 'active_modules', 'adminlist', 'blacklist', 'whitelist']
  syncConfigOptions(botConfigKeys, botConfig, config, schema.properties)
  syncConfigOptions('mm_', mmConfig, config, schema.properties)
  syncConfigOptions('llm_', llmConfig, config, schema.properties)
  syncConfigOptions('sd_', sdConfig, config, schema.properties)
  syncConfigOptions('tts_', ttsConfig, config, schema.properties)
  syncConfigOptions('stt_', sttConfig, config, schema.properties)
  syncConfigOptions('tta_', ttaConfig, config, schema.properties)
  envs.options = env.response.all.reduce(reductor, {})
  envs.value = env.response.active
  setTimeout(() => {
    isRefreshing = false
  }, 500)
}

const botConfig = reactive({
  active_modules: { value: [], type: 'tags', options: [] },
  threaded_initialization: { value: false, type: Boolean },
  ignore_mode: { value: 'both', type: 'select', options: [] },
  adminlist: { value: [], type: 'numbertags' },
  blacklist: { value: [], type: 'numbertags', depends: o => o.ignore_mode.value !== 'whitelist' },
  whitelist: { value: [], type: 'numbertags', depends: o => o.ignore_mode.value !== 'blacklist' }
})

const mmConfig = reactive({
  mm_management_policy: { value: [], type: 'select', options: '' },
  mm_autounload_after_seconds: { value: '0', type: 'slider', min: 0, max: 3600 },
  mm_ram_cached_model_count_limit: { value: '10', type: 'slider', min: 0, max: 30 },
  mm_vram_cached_model_count_limit: { value: '10', type: 'slider', min: 0, max: 30 }
})

const isLLMBackendRemote = o => o.llm_backend.value.startsWith('remote')
const isLLMRemoteAndAutoLaunchOn = o => isLLMBackendRemote(o) && o.llm_remote_launch_process_automatically.value
const isLLMBackendLlamaCpp = o => o.llm_backend.value === 'llama_cpp'
const llmConfig = reactive({
  llm_backend: { value: '', type: 'select', options: [] },
  llm_python_model_type: { value: '', type: 'select', options: [], depends: o => o.llm_backend.value.startsWith('py') },
  llm_host: { value: '', type: 'text', depends: isLLMBackendRemote },
  llm_remote_model_name: { value: '', type: 'text', depends: isLLMBackendRemote },
  llm_remote_launch_process_automatically: { value: '', type: Boolean, depends: isLLMBackendRemote },
  llm_remote_launch_dir: { value: '', type: 'text', depends: isLLMRemoteAndAutoLaunchOn },
  llm_remote_launch_command: { value: '', type: 'text', depends: isLLMRemoteAndAutoLaunchOn },
  llm_remote_launch_waittime: { value: '', type: 'text', depends: isLLMRemoteAndAutoLaunchOn },
  llm_lcpp_gpu_layers: { value: '0', type: 'slider', depends: isLLMBackendLlamaCpp },
  llm_lcpp_max_context_size: { value: '0', type: 'slider', depends: isLLMBackendLlamaCpp }
})

const sdConfig = reactive({
  sd_host: { value: '', type: 'text' }
})

const ttsConfig = reactive({
  tts_mode: { value: '', type: 'select', options: [] },
  tts_enable_backends: { value: [], type: 'tags', options: [] },
  tts_host: { value: '', type: 'text', depends: o => o.tts_mode.value !== 'local' }
})

const sttConfig = reactive({
  stt_backend: { value: '', type: 'select', options: [] }
})

const ttaConfig = reactive({
  tta_duration: { value: 3, type: 'slider' }
})

function reportError(text) {
  notification.value.$emit('showNotification', { message: text, type: 'error' })
}

refreshData().then(() => {
  const allConfigs = { ...mmConfig, ...botConfig, ...sdConfig, ...ttsConfig, ...ttaConfig, ...sttConfig }

  for (const item in allConfigs)
    watch(() => allConfigs[item].value, v => itemChanged(item, v, allConfigs[item]), { deep: true })
  watch(envs, (e) => {
    if (!isRefreshing) {
      api('PUT', 'bot/env', { body: JSON.stringify(envs.value), headers: { 'content-type': 'application/json' } })
        .then((r) => {
          if (r.error)
            throw new Error(r.error)

          refreshData()
        })
        .catch(reportError)
    }
  })
})

function itemChanged(name, value, meta) {
  if (isRefreshing) return
  if (meta.type === 'numbertags')
    value = value.map(x => parseInt(x))
  api('PATCH', 'config', { body: JSON.stringify({ [name]: value }) })
    .then((r) => {
      if (r.error)
        reportError(r.error)
      else
        notification.value.$emit('showNotification', { message: '✅ saved', type: 'ok', duration: 500 })
    })
    .catch(reportError)
}
const envs = reactive({ value: 'Loading...', options: ['Loading...'] })
</script>

<template>
  <div class="w-full flex box-border flex-wrap justify-around">
    <Notification ref="notification" />
    <FormWrapper>
      <div slot="header" class="relative">
        <hi-code class="align-sub" :data="envs" />
        Bot configuration
        <FvlForm v-show="!globalState.botIsRunning" url="#" class="absolute right-0 -top-5">
          <FvlSelect
            label=""
            name="preset"
            placeholder="default"
            :allow-empty="false"
            :options="envs.options"
            :selected.sync="envs.value"
          />
        </FvlForm>
      </div>
      <ConfigForm slot="content" :config-obj="botConfig" />
    </FormWrapper>
    <FormWrapper>
      <div slot="header">
        <hi-cpu class=" align-sub" />
        Memory manager
      </div>
      <ConfigForm slot="content" :config-obj="mmConfig" />
    </FormWrapper>
    <FormWrapper>
      <div slot="header">
        <hi-chat class=" align-sub" />
        Large language models
      </div>
      <ConfigForm slot="content" :config-obj="llmConfig" />
    </FormWrapper>
    <FormWrapper>
      <div slot="header">
        <hi-brush-big class=" align-sub" />
        Stable Diffusion
      </div>
      <ConfigForm slot="content" :config-obj="sdConfig" />
    </FormWrapper>
    <FormWrapper>
      <div slot="header">
        <hi-music-note class=" align-sub" />
        Speech-to-Text
      </div>
      <ConfigForm slot="content" :config-obj="sttConfig" />
    </FormWrapper>
    <FormWrapper>
      <div slot="header">
        <hi-microphone class=" align-sub" />
        Text-to-audio
      </div>
      <ConfigForm slot="content" :config-obj="ttaConfig" />
    </FormWrapper>
    <FormWrapper>
      <div slot="header">
        <hi-volume-2 class=" align-sub" />
        Text-to-Speech
      </div>
      <ConfigForm slot="content" :config-obj="ttsConfig" />
    </FormWrapper>
  </div>
</template>

<style scoped>
.fvl-select {
  @apply relative
}
</style>
