<script setup>
import { RouterLink } from 'vue-router'
import { onMounted, onUnmounted } from 'vue'
import { toggleBot, isBotAlive } from '../botControl'
import router, { routes } from '../router'
import { globalState } from '@/state'

const textGlow = ref(false)
const menuItems = ref(routes.filter(x => !x._hide))
const isCurrentPathSelected = item => currentPathName.value.name === item.name
const currentPathName = toRef(reactive(router), 'currentRoute')
let pingInterval
onMounted(() => {
  isBotAlive()
  pingInterval = setInterval(isBotAlive, 30000)
})
onUnmounted(() => {
  clearInterval(pingInterval)
})
</script>

<template>
  <div class="fixed left-0 top-0 w-64 min-h-screen" style="background: linear-gradient(180deg, #3d8066 0%, #0a2f62 100%);">
    <h1 class="text-white p-4 text-3xl logo w-full text-center" :class="{ 'text-glow': textGlow }" @click="textGlow = !textGlow">
      Botality
    </h1>
    <RouterLink
      v-for="item, index in menuItems" :key="index" class=" inline-block text-white w-full p-4 hover:bg-slate-800"
      :class="{ 'text-glow': textGlow, 'selected-route': isCurrentPathSelected(item) }"
      :to="item.basePath"
    >
      <component :is="item.icon" class="align-text-bottom mr-4 text-xl" />
      {{ item.name }}
    </RouterLink>
    <div class="absolute w-full bottom-0 left-0 bg-main bg-opacity-20" @click="toggleBot">
      <div class="relative w-full h-full">
        <transition name="botstate">
          <div v-if="globalState.botIsRunning" class="w-full h-full absolute bg-green-400 bg-opacity-30 pointer-events-none" />
        </transition>
        <transition name="botstatelock">
          <div v-if="globalState.botStateLocked" class="w-full h-full absolute bg-blue-400 bg-opacity-20 pointer-events-none" />
        </transition>
        <div
          class="p-4 flex cursor-pointer"
          :class="{
            'text-white text-opacity-60 ': globalState.botIsRunning,
            'animate-pulse': globalState.botStateLocked,
          }"
        >
          <hi-power
            class=" text-4xl hover:text-cyan-600" :class="{ 'hover:text-gray-800': globalState.botIsRunning }"
          />
          <span class=" text-xl flex self-center justify-center w-full" :class="{ 'text-glow': textGlow }">{{ globalState.botStateText }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.selected-route {
  @apply border-r-2 border-white
}
.botstate-enter-active, .botstate-leave-active {
  transition: all .4s;
}
.botstatelock-enter-active {
  transition: width 4s, opacity 1s;
}
.botstatelock-leave-active {
  transition: width 0s, opacity .4s;
}
.botstate-enter, .botstate-leave-to, .botstatelock-leave-to {
  opacity: 0;
}
.botstate-enter-to, .botstate-enter-to {
  opacity: 1;
}
.botstatelock-enter {
  opacity: 0;
  width: 0;
}
.botstatelock-enter-to, .botstatelock-enter-to {
  opacity: 1;
  width: 100%;
}

.text-glow {
  background: url(https://media.tenor.com/8ZBML9qVD60AAAAC/smoke-mk.gif) #3c7e66;
  background-size: 38%;
  background-clip: text;
  color: transparent;
  background-blend-mode: color-dodge;
  background-position-y: 50px;
}
</style>

<style>
 @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300&family=Trade+Winds&display=swap');
.logo {
  font-family: 'Trade Winds', cursive;
}
div {
  font-family: 'Poppins', sans-serif;
}
</style>
