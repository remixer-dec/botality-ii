<script setup>
import Vue, { ref, getCurrentInstance, inject, onMounted } from 'vue'
import { api } from '../tools'
import { globalState } from '../state'

const { proxy } = getCurrentInstance()
onMounted(() => {
  proxyRef.value = proxy
})
</script>

<script>
const msg = ref('')
const history = ref([])
const isProcessing = ref(false)
const scrollable = ref(null)
const proxyRef = ref(null)
function getBotReply(text) {
  const msg = { text }
  isProcessing.value = true
  api('POST', 'chat', { body: JSON.stringify(msg), headers: { 'content-type': 'application/json' } }).then((json) => {
    if (json.error)
      throw new Error(json.error)

    history.value.push({ text: highlightCommands(json.response.text), fromBot: true })
    isProcessing.value = false
    scrollToBottom()
  }).catch((e) => {
    reportError(e)
    isProcessing.value = false
  })
}

function reportError(text) {
  proxyRef.value.$root.$emit('showNotification', { message: text, type: 'error' })
}

function highlightCommands(text) {
  return text.replace(/([/][a-z0-9_.]+)([ ,;\n\r])/img, '<b class="command" data-command="$1">$1</b>$2')
}

function messageClickHandler(e) {
  const command = e.target.getAttribute('data-command')
  if (command)
    msg.value = `${command} `
}

function sendMessage() {
  if (msg.value === '/clear') return [history.value, msg.value] = [[], '']
  history.value.push(
    {
      text: highlightCommands(msg.value)
    }
  )
  getBotReply(msg.value)
  msg.value = ''
  scrollToBottom()
}

function scrollToBottom() {
  Vue.nextTick(() => {
    scrollable.value.scrollTop = scrollable.value.scrollHeight
  })
}

function* messageIterator() {
  let index = history.value.length - 1

  while (true) {
    const direction = yield (index >= 0 && index < history.value.length ? history.value[index].text : '')
    if (history.value.length === 0) continue
    if (direction === 'down')
      index = (index + 1) % history.value.length

    else if (direction === 'up')
      index = --index < 0 ? history.value.length - 1 : index
  }
}
const msgIterator = messageIterator()
</script>

<template>
  <div>
    <div v-if="globalState.botIsRunning" class="flex flex-col relative h-screen p-8 w-full pb-12 2xl:px-48">
      <div ref="scrollable" class="w-full mb-10 h-full box-border overflow-y-auto">
        <div class="flex flex-col justify-end">
          <div v-for="message, index in history" :key="index" class="message" :class="{ 'message-bot': message.fromBot }">
            <div @click="messageClickHandler" v-html="message.text" />
          </div>
        </div>
      </div>
      <div class="fixed bottom-4 left-0 w-full flex px-0 2xl:px-40">
        <div class="w-full h-10 p-2 bg-white mx-8 rounded-lg flex items-center">
          <div v-if="isProcessing" class="absolute text-gray-400 pointer-events-none">
            <div class="relative -top-10 animate-pulse">
              <span class="animate-spin inline-flex justify-center align-middle"><hi-spinner-earring /></span>
              processing
            </div>
          </div>
          <input
            v-model="msg" type="text"
            placeholder="Type your message"
            class="w-full focus:outline-none"
            @keydown.enter="sendMessage"
            @keydown.up="msg = msgIterator.next('up').value || msg"
            @keydown.down="msg = msgIterator.next('down').value || msg"
          >
          <span class="button bg-[#38b2ac] text-white text-2xl rounded-[50%] w-8 h-8 cursor-pointer hover:bg-cyan-600" @click="sendMessage">
            <hi-navigation />
          </span>
        </div>
      </div>
    </div>
    <div v-else class="flex flex-col w-full align-center justify-center h-screen items-center">
      <div class="text-xl">
        <hi-wifi-off />
      </div>
      Please start the bot to chat with it.
    </div>
  </div>
</template>

<style scoped>
.message {
  @apply bg-white p-4 m-2 rounded-lg w-max relative self-end max-w-full md:max-w-lg whitespace-pre-wrap
}
.message::after {
  content: '';
  @apply absolute w-0 h-0 border-12 border-r-0 border-t-transparent
  border-b-transparent border-l-white -bottom-0.5 right-0 transform rotate-24 -rotate-z-240
}
.message.message-bot {
  @apply self-start
}
.message.message-bot::after {
  @apply right-auto left-0 rotate-z-0
}
</style>

<style>
.message [data-command] {
  @apply text-blue-400 cursor-pointer
}
</style>
