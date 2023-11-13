<script setup>
import { api } from '../tools'
import locale from '../locale'
import SetupWindow from './ModelSetupWindow.vue'

const props = defineProps(['headers', 'data', 'keys', 'modelType', 'canBeInstalled', 'canBeSelected'])
const { proxy } = getCurrentInstance()

function reportError(text) {
  proxy.$root.$emit('showNotification', { message: text, type: 'error' })
}

function showInstallWindow(modelConfig) {
  modelConfig._type = props.modelType
  proxy.$root.$emit('showModal', { component: SetupWindow, data: { modelConfig } })
}

function deleteModel(modelConfig) {
  modelConfig._type = props.modelType
  if (confirm(locale.are_you_sure)) {
    api('POST', `models/uninstall/${modelConfig._type}`,
      { body: JSON.stringify(modelConfig), headers: { 'content-type': 'application/json' } }).then(() => {
      proxy.$root.$emit('refreshModels')
    }).catch(reportError)
    alert(locale.confirm_uninstall)
  }
}

function selectModel(modelConfig) {
  api('POST', `models/select/${props.modelType}`,
    { body: JSON.stringify(modelConfig), headers: { 'content-type': 'application/json' } })
    .then((r) => {
      if (r.error) throw new Error(r.error)
      else proxy.$root.$emit('showNotification', { message: locale.model_selected_ok })
      proxy.$root.$emit('refreshModels')
    }).catch(reportError)
}
</script>

<template>
  <table class=" w-full">
    <thead>
      <tr class="cursor-default">
        <th v-for="header, index of props.headers" :key="index" class="text-left underline text-xs align-top md:text-base">
          {{ header }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="model, idx in props.data" v-show="!model.hide" :key="idx">
        <td v-for="k, index in props.keys" :key="index">
          <span v-if="props.headers[index] === 'Repo'">
            <a :href="`https://huggingface.co/${model[k]}`">{{ model[k] }}</a>
          </span>
          <span v-else>{{ model[k] }}</span>
        </td>
        <div v-if="canBeSelected">
          <td v-if="model.selected" class=" cursor-default">
            <hi-check-circle />
          </td>
          <td v-else class=" cursor-pointer text-center" @click="selectModel(model)">
            <hi-circle />
          </td>
        </div>
        <td v-if="canBeInstalled" class=" cursor-pointer text-center" @click="showInstallWindow(model)">
          <hi-download-alt />
        </td>
        <td v-else class=" cursor-pointer text-center" @click="deleteModel(model)">
          <hi-trash />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
tr:nth-child(even) {
  @apply bg-slate-100
}
th:last-child {
  @apply text-center
}
td {
  @apply text-xs md:text-base
}
</style>
