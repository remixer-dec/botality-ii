<!-- eslint-disable no-invalid-this -->
<!-- eslint-disable vue/no-mutating-props -->
<script setup>
import locale from '../locale'
import KVEditor from './KVEditor.vue'
import { FvlSwitch, FvlSelect, FvlTagSelect, FvlForm, FvlSlider, FvlInput, FvlSearchSelect } from '@/libs/formvuelar'

defineProps({
  configObj: { type: Object, required: true }
})
// original FvlSlider component does not support step prop, implement via labelclass
FvlSlider.mounted = [function () {
  if (this.$props.labelClass.startsWith('step:')) {
    const step = this.$props.labelClass.split(':')[1]
    this.$el.getElementsByTagName('input')[0].setAttribute('step', step)
    // this.$props.labelClass = ''
  }
}]
</script>

<template>
  <div>
    <FvlForm :data="configObj" url="#/select " class="relative">
      <div v-for="option, idx in configObj" :key="idx" :class="`${idx} ${option.type}`">
        <span :aria-disabled="option.depends ? !option.depends(configObj) : false" class="relative inline-block w-full confbox">
          <div class=" absolute top-0 right-2 text-gray-100 z-20 hover:z-40 hint" :hint-content="locale.get(idx)">
            <hi-bulb-off />
          </div>
          <FvlSwitch
            v-if="option.type === 'bool'"
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
            :placeholder="locale.select_tag"
          />
          <FvlSlider
            v-if="String(option.type).endsWith('slider')"
            :title="option.value"
            :value.sync="option.value"
            :name="idx"
            :label="idx"
            :min="option.min"
            :max="option.max"
            :label-class="option.step ? `step:${option.step}` : ''"
          />
          <FvlTagSelect
            v-if="option.type === 'freetags'"
            :selected.sync="option.value"
            :search-keys="['value']"
            :allow-new="true"
            option-key="value"
            option-value="value"
            :name="idx"
            :label="idx"
            :type="option.subtype"
            :placeholder="locale.add_tag"
          />
          <FvlInput
            v-if="option.type === 'text'"
            :label="idx"
            :name="idx"
            type="text"
            :value.sync="option.value"
            :placeholder="idx"
          />
          <KVEditor v-if="option.type === 'kv'" :obj="option.value" :name="idx" />
          <FvlSearchSelect
            v-if="option.type === 'search-select'"
            :name="idx"
            :label="idx"
            :selected.sync="option.value"
            :lazy-load="true"
            response-data-path="response"
            :options-url="option.link"
            :option-key="option.okey"
            :option-value="option.ovalue"
            :search-keys="[option.search]"
            :placeholder="option.value"
          />
          <RouterLink
            v-if="option.type === 'custom'" class="fvl-submit-button m-2 inline-block cursor-pointer bg-opacity-70"
            :to="option.link || ''"
          >
            <span class="fvl-submit-text">{{ locale.manage_models }} {{ idx }}</span>
          </RouterLink>
        </span>
      </div>
    </FvlForm>
  </div>
</template>

<style scoped>
form .list, .form .list > div {
  display: inline-block;
}
span[aria-disabled] > div {
  opacity: .4;
  pointer-events: none;
  z-index: 2;
}
.confbox:hover .hint {
  @apply text-gray-400
}
.hint:hover{
  @apply text-yellow-500
}
.hint:hover:before {
  float: left;
  z-index: 10;
  background: rgba(0, 0, 0,.8);
  color: #fff;
  content: attr(hint-content);
  max-width: 330px;
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 0 6px 1px rgba(0,0,0,.2);
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
