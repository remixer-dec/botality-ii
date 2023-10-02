<script setup>
import NotFound from '../views/NotFound.vue'

const props = defineProps(['headers', 'data', 'keys', 'canBeInstalled'])
const { proxy } = getCurrentInstance()

function showInstallWindow() {
  proxy.$root.$emit('showModal', NotFound)
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
      <tr v-for="model, idx in props.data" :key="idx">
        <td v-for="k, index in props.keys" :key="index">
          <span v-if="props.headers[index] === 'Repo'">
            <a :href="`https://huggingface.co/${model[k]}`">{{ model[k] }}</a>
          </span>
          <span v-else>{{ model[k] }}</span>
        </td>
        <td v-if="canBeInstalled" class=" cursor-pointer" @click="showInstallWindow()">
          <hi-download-alt />
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
