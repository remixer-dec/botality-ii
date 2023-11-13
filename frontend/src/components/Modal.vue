<script setup>
import { getCurrentInstance } from 'vue'

const isModalVisible = ref(false)
const modalContent = ref('')
const modalProps = ref({})

const { proxy } = getCurrentInstance()
proxy.$router.beforeEach((to, from, next) => {
  if (isModalVisible.value) {
    isModalVisible.value = false
    return next(false)
  }
  next()
})

onMounted(() => {
  proxy.$root.$on('showModal', (content) => {
    modalProps.value = content.data
    modalContent.value = content.component
    isModalVisible.value = true
  })
  proxy.$root.$on('hideModal', () => {
    isModalVisible.value = false
  })
})
</script>

<template>
  <div v-if="isModalVisible" class="w-full h-full min-h-screen fixed top-0 flex items-center justify-center">
    <div class="w-full absolute h-full min-h-screen top-0 bg-slate-700 bg-opacity-40 " @click="isModalVisible = false" />
    <div
      class="top-0 bg-white w-full md:w-1/2 min-h-full md:min-h-1/2 h-auto z-40 rounded-md shadow-md
     sm:ml-[256px] xl:ml-0 max-h-screen overflow-y-auto"
    >
      <div :is="modalContent" v-if="modalContent" v-bind="modalProps" />
    </div>
  </div>
</template>
