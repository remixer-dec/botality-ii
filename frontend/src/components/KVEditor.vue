<script setup>
import Vue, { isReactive, isRef } from 'vue'
import { FvlInput, FvlForm, FvlSelect } from '@/libs/formvuelar'

const props = defineProps(['obj', 'name'])
const emit = defineEmits(['change'])

const itemsHidden = ref(true)
const editableItemName = ref('')
const editableKey = ref('')
const editableValue = ref('')
const editableType = ref('String')
const typeOptions = {
  String: 'string',
  Boolean: 'bool',
  parseInt: 'int',
  parseFloat: 'float'
}

function openEditor(key) {
  editableKey.value = ''
  editableValue.value = ''
  editableItemName.value = editableItemName.value === key ? '' : key
}

function saveKV(key, obj) {
  if (key !== editableKey.value)
    delete obj[key]

  Vue.set(obj, editableKey.value, editableValue.value)
  editableItemName.value = ''
  editableKey.value = ''
  editableType.value = 'String'
  emit('change', props.name, obj)
}
function addNewItem(obj) {
  const NEW_NAME = '<NEW_ITEM_NAME>'
  if (Object.keys(obj).length === 0)
    Vue.set(obj, NEW_NAME, '')
  else
    obj[NEW_NAME] = ''
  editableKey.value = ''
  editableValue.value = ''
  editableItemName.value = NEW_NAME
}

function deleteItem(key, obj) {
  if (confirm(`Delete ${key}?`)) {
    Vue.delete(obj, key)
    emit('change', props.name, obj)
    editableItemName.value = ''
  }
}
</script>

<template>
  <FvlForm url="#">
    <span class="fvl-input-label ml-2">
      {{ props.name }}
    </span>
    <div v-if="itemsHidden" class="fvl-submit-button mt-0 mb-2 bg-slate-300 mx-2 cursor-pointer" @click="itemsHidden = false">
      <hi-arrows-vertical />
      Expand
    </div>
    <div v-else class="bg-slate-200 bg-opacity-20 rounded-md m-2 overflow-hidden">
      <div v-for="value, key in props.obj" :key="key" class="relative grid overflow-hidden">
        <span class="px-2 bg-slate-300 text-white">{{ key }}
          <span class="float-right">
            <span class="cursor-pointer" @click="openEditor(key)"><hi-pencil /></span>
            <span class="cursor-pointer" @click="deleteItem(key, props.obj)"><hi-trash /></span>
          </span>
        </span>
        <pre v-if="key !== editableItemName" class="p-2 overflow-x-auto text-gray-600">{{ value }}</pre>
        <span v-else>
          <div v-if="editableKey === ''" :set="[editableKey, editableValue] = [key, value]" />
          <FvlInput
            label="key"
            name="key"
            type="text"
            :value.sync="editableKey"
            :placeholder="key"
          />
          <FvlInput
            label="value"
            name="value"
            type="text"
            :value.sync="editableValue"
            :placeholder="value"
          />
          <FvlSelect
            label="type"
            name="type"
            :allow-empty="false"
            :options="typeOptions"
            :selected.sync="editableType"
            class="w-full"
          />
          <div class="fvl-submit-button bg-slate-300 cursor-pointer rounded-none mb-2" @click="saveKV(key, props.obj)">OK</div>
        </span>
      </div>
      <div v-if="editableItemName !== '<NEW_ITEM_NAME>'" class="min-h-6">
        <span class="px-2 bg-slate-300 text-white float-right cursor-pointer" @click="addNewItem(props.obj)">Add new item</span>
      </div>
    </div>
  </FvlForm>
</template>

<style scoped>
</style>
