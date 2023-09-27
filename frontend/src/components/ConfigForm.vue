<!-- eslint-disable vue/no-mutating-props -->
<script setup>
import { FvlSwitch, FvlSelect, FvlTagSelect, FvlForm, FvlSlider, FvlInput } from 'formvuelar'

defineProps({
  configObj: { type: Object, required: true }
})
</script>

<template>
  <div>
    <FvlForm :data="configObj" url="#/select " class="relative">
      <div v-for="option, idx in configObj" :key="idx" :class="`${idx} ${option.type}`">
        <span :aria-disabled="option.depends ? !option.depends(configObj) : false">
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
          <FvlTagSelect
            v-if="option.type === 'numbertags'"
            :selected.sync="option.value"
            options=""
            :search-keys="['value']"
            :allow-new="true"
            option-key="value"
            option-value="value"
            :name="idx"
            :label="idx"
            type="number"
            placeholder="Add..."
          />
          <FvlInput
            v-if="option.type === 'text'"
            :label="idx"
            :name="idx"
            type="text"
            :value.sync="option.value"
            :placeholder="idx"
          />
          <span v-if="option.type === 'list'" class="fvl-submit-button m-2 inline-block cursor-pointer bg-opacity-70">
            <span class="fvl-submit-text">Manage {{ idx }}</span>
          </span>
        </span>
      </div>
    </FvlForm>
  </div>
</template>

<style scoped>
form .list, .form .list > div {
  display: inline-block;
}
span[aria-disabled] {
  opacity: .4;
  pointer-events: none;
  z-index: 2;
}
</style>

<style>
input[type='number'] {
    -moz-appearance:textfield;
}

input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
}
</style>
