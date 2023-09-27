<script setup>
import { FvlSelect, FvlForm } from 'formvuelar'
import { reactive } from 'vue'
import { api } from '../tools'

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
        this.item.type = 'slider'
        break
      case 'array':
        this.item.type = 'text'
        if (schema.enum)
          this.item.type = 'tags'
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

async function refreshData() {
  const schema = await api('GET', 'schema')
  const config = await api('GET', 'config')
  const botConfigKeys = ['ignore_mode', 'threaded_initialization', 'active_modules']
  syncConfigOptions(botConfigKeys, botConfig, config, schema.properties)
  syncConfigOptions('mm_', mmConfig, config, schema.properties)
}

const botConfig = reactive({
  ignore_mode: { value: 'both', type: 'select', options: [] },
  threaded_initialization: { value: false, type: Boolean },
  active_modules: { value: [], type: 'tags', options: [] }
})

const mmConfig = reactive({
  mm_management_policy: { value: [], type: 'select', options: '' },
  mm_autounload_after_seconds: { value: '0', type: 'slider', min: 0, max: 3600 },
  mm_ram_cached_model_count_limit: { value: '10', type: 'slider', min: 0, max: 30 },
  mm_vram_cached_model_count_limit: { value: '10', type: 'slider', min: 0, max: 30 }
})

refreshData().then(() => {
  const allConfigs = { ...mmConfig, ...botConfig }

  for (const item in allConfigs)
    watch(() => allConfigs[item].value, v => itemChanged(item, v), { deep: true })
})

function itemChanged(name, value) {
  api('PATCH', 'config', { body: JSON.stringify({ [name]: value }) })
    .then((r) => {
      if (r.error)
        notification.value.$emit('showNotification', { message: r.error, type: 'error' })
      else
        notification.value.$emit('showNotification', { message: '✅ saved', type: 'ok', duration: 500 })
    })
    .catch((e) => {
      notification.value.$emit('showNotification', { message: e, type: 'error' })
    })
}
const inis = reactive({ value: '.env (default)', options: ['.env (default)'] })
</script>

<template>
  <div class="w-full flex box-border">
    <Notification ref="notification" />
    <FormWrapper>
      <div slot="header" class="relative">
        <hi-code class="align-sub" :data="inis" />
        Bot configuration
        <FvlForm url="#/inis" class="absolute right-0 -top-5">
          <FvlSelect
            label=""
            name="preset"
            placeholder="default"
            :allow-empty="false"
            :options="inis.options"
            :selected.sync="inis.value"
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
  </div>
</template>

<style scoped>
.fvl-select {
  @apply relative
}
</style>
