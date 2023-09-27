<!-- eslint-disable vue/no-mutating-props -->
<script setup>
import { FvlSwitch, FvlSelect, FvlTagSelect, FvlForm, FvlSlider } from 'formvuelar'

defineProps({
  configObj: { type: Object, required: true }
})
</script>

<template>
  <div>
    <FvlForm :data="configObj" url="#/select " class="relative">
      <div v-for="option, idx in configObj" :key="idx">
        <FvlSwitch
          v-if="option.type === Boolean"
          class="relative"
          :label="idx"
          :name="idx"
          :checked.sync="option.value"
        />
        <FvlSelect
          v-if="option.type === 'select'"
          :label="idx"
          :name="idx"
          :placeholder="idx"
          :allow-empty="false"
          :options="option.options"
          :selected.sync="option.value"
          class="w-full"
        />
        <FvlTagSelect
          v-if="option.type === 'tags'"
          :selected.sync="option.value"
          :options="option.options"
          :search-keys="['value']"
          :allow-new="false"
          option-key="value"
          option-value="value"
          :name="idx"
          :label="idx"
          placeholder="Select..."
        />
        <FvlSlider
          v-if="option.type === 'slider'"
          :value.sync="option.value"
          :name="idx"
          :label="idx"
          :min="option.min"
          :max="option.max"
        />
      </div>
    </FvlForm>
  </div>
</template>
