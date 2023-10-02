<script setup>
const isModalVisible = ref(true)
const modalContent = ref('')
onMounted(() => {
  const { proxy } = getCurrentInstance()
  proxy.$root.$on('showModal', (content) => {
    modalContent.value = content
    isModalVisible.value = true
  })
})
</script>

<template>
  <div v-if="isModalVisible" class="w-full h-full min-h-screen fixed top-0 flex items-center justify-center">
    <div class="w-full absolute h-full min-h-screen top-0 bg-slate-700 bg-opacity-40 " @click="isModalVisible = false" />
    <div class=" top-0 bg-white w-1/2 h-3/4 z-40 rounded-md ">
      <div :is="modalContent" v-if="modalContent" />
    </div>
  </div>
</template>
