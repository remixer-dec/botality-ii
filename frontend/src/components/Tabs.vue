<!-- eslint-disable vue/no-mutating-props -->
<script setup>
import { onMounted } from 'vue'

const props = defineProps(['items'])
const selectedItem = ref('')
defineExpose({ selectedItem })
onMounted(() => {
  selectedItem.value = props.items[0].name
})
</script>

<template>
  <div>
    <span v-for="item, idx in props.items" :key="idx">
      <span
        class="inline-block mr-1 p-1 bg-white  rounded-md cursor-pointer px-2 tab"
        :class="{ selected: selectedItem === item.name }"
        @click="selectedItem = item.name"
      >
        {{ item.name }}
      </span>
    </span>
  </div>
</template>

<style scoped>
.tab {
  @apply border-1 border-[#38b2ac] text-[#38b2ac];
}
.selected {
  @apply bg-[#38b2ac] text-white
}
</style>
