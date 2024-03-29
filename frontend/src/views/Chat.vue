<script setup>
import Vue, { ref, getCurrentInstance, onMounted, computed } from 'vue'
import { api } from '../tools'
import { globalState } from '../state'
import locale from '../locale'

const { proxy } = getCurrentInstance()
onMounted(() => {
  proxyRef.value = proxy
})
</script>

<script>
const msg = ref('')
const history = ref([])
const onlyUserHistory = computed(() => history.value.filter(x => !x.fromBot))
const formattedHistory = computed(() => history.value.map(x => ({ ...x, text: highlightCommands(x.text) })))
const processingPromises = ref([])
const isProcessing = ref(false)
const scrollable = ref(null)
const proxyRef = ref(null)

function getBotReply(text) {
  const msg = { text }
  isProcessing.value = true
  const request = api('POST', 'chat', { body: JSON.stringify(msg), headers: { 'content-type': 'application/json' } })
  processingPromises.value.push(request)
  request.then((json) => {
    if (json.error)
      throw new Error(json.error)
    history.value.push({
      text: json.response.text,
      voice: b64ToBlobLink(json.response.voice, 'audio/ogg'),
      photos: json.response.photos ? json.response.photos.map(x => b64ToBlobLink(x, 'image/png')) : null,
      fromBot: true
    })
    scrollToBottom()
  }).catch(reportError).finally(() => {
    Promise.allSettled(processingPromises.value).then(requestPromiseCompletionChecker)
  })
}

function b64ToBlobLink(b64, mime) {
  if (!b64) return
  const binaryData = atob(b64)
  const byteArray = new Uint8Array(binaryData.length)
  for (let i = 0; i < binaryData.length; i++)
    byteArray[i] = binaryData.charCodeAt(i)
  const blob = new Blob([byteArray], { type: mime })
  return URL.createObjectURL(blob)
}

function requestPromiseCompletionChecker(arr) {
  if (arr.length === processingPromises.value.length) {
    isProcessing.value = false
    processingPromises.value.length = 0
  }
  else { Promise.allSettled(processingPromises.value).then(requestPromiseCompletionChecker) }
}

function reportError(text) {
  proxyRef.value.$root.$emit('showNotification', { message: text, type: 'error' })
}

function highlightCommands(text) {
  if (!text) return
  return text.replace(/([/][a-z0-9_.]+)([ ,;\n\r])/img, '<b class="command" data-command="$1">$1</b>$2')
}

function messageClickHandler(e) {
  const command = e.target.getAttribute('data-command')
  if (command)
    msg.value = `${command} `
}

function sendMessage() {
  msg.value = msg.value.trim()
  if (msg.value.length === 0) return
  if (msg.value === '/clear') return [history.value, msg.value] = [[], '']
  history.value.push(
    {
      text: msg.value
    }
  )
  getBotReply(msg.value)
  msg.value = ''
  shoudResetIteratorIndex.value = true
  scrollToBottom()
}

function scrollToBottom() {
  Vue.nextTick(() => {
    scrollable.value.scrollTop = scrollable.value.scrollHeight
  })
}

function* messageIterator() {
  const history = onlyUserHistory
  let index = history.value.length - 1

  while (true) {
    const direction = yield (index >= 0 && index < history.value.length ? history.value[index].text : '')
    if (history.value.length === 0) continue
    index = shoudResetIteratorIndex.value ? history.value.length - 1 : index
    if (direction === 'down')
      index = (index + 1) % history.value.length

    else if (direction === 'up')
      index = --index < 0 ? history.value.length - 1 : index
  }
}
const msgIterator = messageIterator()
const shoudResetIteratorIndex = ref(false)

function smoothScroll(e) {
  e.parentElement.scrollIntoView({
    behavior: 'smooth',
    block: 'end'
  })
}
</script>

<template>
  <div>
    <div v-if="globalState.botIsRunning" class="flex flex-col relative h-screen p-8 w-full pb-12 2xl:px-48">
      <div ref="scrollable" class="w-full mb-10 h-full box-border overflow-y-auto">
        <transition-group name="new_message" tag="div" class="flex flex-col justify-end" @after-enter="smoothScroll">
          <div v-for="message, index in formattedHistory" :key="index" class="message" :class="{ 'message-bot': message.fromBot }">
            <div v-if="message.photos" v-once>
              <img v-for="photo, idx in message.photos" :key="idx" :src="photo">
            </div>
            <div v-if="message.text" v-once @click="messageClickHandler" v-html="message.text" />
            <div v-if="message.voice" v-once>
              <audio controls :src="message.voice" />
            </div>
          </div>
        </transition-group>
      </div>
      <div class="fixed bottom-1 sm:bottom-4 left-0 w-full flex px-0 2xl:px-40">
        <div class="w-full h-10 p-2 bg-white mx-1 sm:mx-8 rounded-lg flex items-center">
          <div v-if="isProcessing" class="absolute text-gray-400 pointer-events-none">
            <div v-once class="relative -top-10 animate-pulse">
              <span class="animate-spin inline-flex justify-center align-middle"><hi-spinner-earring /></span>
              {{ locale.processing }}
            </div>
          </div>
          <input
            v-model="msg" type="text"
            :placeholder="locale.empty_message"
            class="w-full focus:outline-none"
            @keydown.enter="sendMessage"
            @keydown.up="msg = msgIterator.next('up').value || msg"
            @keydown.down="msg = msgIterator.next('down').value || msg"
          >
          <span class="button bg-main text-white text-2xl rounded-[50%] ml-2 w-8 h-8 cursor-pointer hover:bg-cyan-600 flex-shrink-0" @click="sendMessage">
            <hi-navigation />
          </span>
        </div>
      </div>
    </div>
    <Offline :message="locale.chat_offline" />
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
audio {
  -webkit-filter: brightness(2)
}

.new_message-enter-active, .new_message-leave-active {
  transition: all .4s, margin-left .3s, padding-right .2s;
}
.new_message-enter-active.message.message-bot, .new_message-leave-active.message.message-bot,
.new_message-enter-active.message.message-bot div, .new_message-leave-active.message.message-bot div {
  transition-delay: .2s;
}
.new_message-enter, .new_message-leave-to {
  opacity: 0;
  transform: translateY(4px);
  padding-right: 0;
  position: relative;
}

.new_message-enter.message.message-bot, .new_message-leave-to.message.message-bot {
  margin-left: -4px;
  padding-right: auto;
}

.new_message-enter-active div, .new_message-leave-active div {
  transition: all .5s;
  overflow: hidden;
  position: relative;
}
.new_message-enter div,.new_message-leave-to div {
  opacity: 0;
  transform: translateY(-4px);
}
</style>

<style>
.message [data-command] {
  @apply text-blue-400 cursor-pointer
}
</style>
