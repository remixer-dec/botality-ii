<script setup>
import { api } from '../tools'
import SetupWindow from './ModelSetupWindow.vue'

const props = defineProps(['headers', 'data', 'keys', 'modelType', 'canBeInstalled'])
const { proxy } = getCurrentInstance()

function showInstallWindow(modelConfig) {
  modelConfig._type = props.modelType
  proxy.$root.$emit('showModal', { component: SetupWindow, data: { modelConfig } })
}

function deleteModel(modelConfig) {
  modelConfig._type = props.modelType
  if (confirm('Are you sure?')) {
    api('POST', `models/uninstall/${modelConfig._type}`,
      { body: JSON.stringify(modelConfig), headers: { 'content-type': 'application/json' } }).then(() => {
      proxy.$root.$emit('refreshModels')
    })
    alert('Please confirm that you want to delete the model in the terminal')
  }
}
</script>

<template>
  <table class=" w-full">
    <thead>
      <tr class="cursor-default">
        <th v-for="header, index of props.headers" :key="index" class="text-left underline">
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
        <td v-if="canBeInstalled" class=" cursor-pointer" @click="showInstallWindow(model)">
          <hi-download-alt />
        </td>
        <td v-else class=" cursor-pointer" @click="deleteModel(model)">
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
</style>
