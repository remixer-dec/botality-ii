<script setup>
const message = ref('')
const show = ref(false)
const lastTimeout = ref(0)
const isError = ref(false)
const duration = ref(8000)
const lockRemoval = ref(false)

watchEffect(() => {
  if (message.value) {
    show.value = true
    clearTimeout(lastTimeout.value)
    lastTimeout.value = setTimeout(hideNotification, duration.value)
  }
})

function hideNotification() {
  if (lockRemoval.value)
    return watchOnce(lockRemoval, hideNotification)

  show.value = false
  isError.value = false
  message.value = ''
  duration.value = 8000
}

function showNotification(event) {
  message.value = event.message

  isError.value = event.type === 'error'

  if (event.duration)
    duration.value = event.duration
}

onMounted(() => {
  const { proxy } = getCurrentInstance()
  proxy.$root.$on('showNotification', showNotification)
})
</script>

<template>
  <transition name="fade" mode="out-in">
    <div
      v-if="show"
      class="fixed max-w-[400px] p-4 text-black rounded-md shadow-lg z-40 bg-white" :class="{ 'bg-red-400': isError, 'text-white': isError }"
      @mouseover="lockRemoval = true"
      @mouseleave="lockRemoval = false"
      v-html="message"
    />
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
