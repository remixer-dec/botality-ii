<script setup>
const message = ref('')
const show = ref(false)
const lastTimeout = ref(0)
const isError = ref(false)
const duration = ref(8000)

watchEffect(() => {
  if (message.value) {
    show.value = true
    clearTimeout(lastTimeout)
    lastTimeout.value = setTimeout(() => {
      show.value = false
      isError.value = false
      message.value = ''
      duration.value = 8000
    }, duration.value)
  }
})

function showNotification(event) {
  message.value = event.message

  if (event.type === 'error')
    isError.value = true

  if (event.duration)
    duration.value = event.duration
}

onMounted(() => {
  const { proxy } = getCurrentInstance()
  proxy.$on('showNotification', showNotification)
})
</script>

<template>
  <transition name="fade" mode="out-in">
    <div v-if="show" class="fixed max-w-[400px] top-4 right-4 p-4 text-black rounded-md shadow-lg z-40 bg-white" :class="{ 'bg-red-400': isError, 'text-white': isError }" v-html="message" />
  </transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
