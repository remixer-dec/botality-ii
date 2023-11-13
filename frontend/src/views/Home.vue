<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { api } from '../tools'
import { globalState } from '../state'
import locale from '../locale'

const stats = ref({ timings: { start: 0 } })
const uptime = computed(() => ~~(((new Date()).getTime() - new Date(stats.value.timings.start * 1000).getTime()) / 1000) - parseInt(trigger.value))
const trigger = ref(0.1)
let updateDataInterval = 0

setInterval(() => {
  if (!globalState.botIsRunning) return
  trigger.value = Math.random()
}, 1000)

watch(() => globalState.botIsRunning, (running) => {
  if (running)
    updateStats()
})

function updateStats() {
  if (!globalState.botIsRunning) return
  api('GET', 'status').then((r) => {
    if (r.response)
      stats.value = r.response
  })
}

onMounted(() => {
  updateStats()
  updateDataInterval = setInterval(updateStats, 5000)
})
onUnmounted(() => {
  clearInterval(updateDataInterval)
})
</script>

<template>
  <div class="w-full flex box-border flex-wrap justify-evenly flex-col min-h-screen">
    <div class="bg-white w-full p-2 grid grid-cols-2 mx-auto mb-4 rounded-md lg:w-1/2">
      <div>{{ locale.bot }}: </div>
      <div v-if="stats.bot">
        <a :href="`tg://resolve?domain=${stats.bot.username}`">{{ stats.bot.name }} (@{{ stats.bot.username }})</a>
      </div>
      <div v-else>
        -
      </div>
      <div>{{ locale.status }}:</div>
      <div>{{ locale.get(globalState.botIsRunning ? 'started' : 'stopped') }}</div>
      <div>{{ locale.flags }}: </div>
      <div v-if="stats.bot">
        <span v-if="stats.bot.can_join_groups" :title="locale.get('can_join_groups')">[G]</span>
        <span v-else :title="locale.get('cannot_join_groups')" class="text-orange">[G]</span>
        <span v-if="stats.bot.can_read_all_group_messages" :title="locale.get('can_read_all')" class="text-orange-400">[A]</span>
        <span v-else :title="locale.get('cannot_read_all')" />
      </div>
      <div v-else>
        -
      </div>
      <div>{{ locale.access_mode }}:</div>
      <div v-if="stats.access_mode">
        <span v-if="stats.access_mode !== 'whitelist'">blacklist</span>
        <span v-if="stats.access_mode === 'both'">+</span>
        <span v-if="stats.access_mode !== 'blacklist'">whitelist</span>
      </div>
      <div v-else>
        -
      </div>
      <div>{{ locale.main_active_modules }}:</div>
      <div>
        <div v-for="module, index in stats.modules" :key="index" class="pr-4">
          {{ module }} ({{ stats.timings[module] }}s)
        </div>
      </div>
      <div>{{ locale.uptime }}:</div>
      <div>
        <span v-show="stats.timings.start">
          {{ uptime }} {{ locale.seconds }}
        </span>
      </div>
      <div>{{ locale.total_messages }}:</div><div>{{ stats?.counters?.msg }}</div>
    </div>
    <div v-if="stats.memory_manager && globalState.botIsRunning" class="bg-white table p-2 mx-auto rounded-md w-full lg:w-1/2">
      <div v-for="item, name in stats.memory_manager" v-show="item" :key="name">
        <div class="w-full text-center p-1">
          {{ name }}
        </div>
        <div class=" bg-gray-500 w-full h-10">
          <div
            v-if="item" class=" bg-main h-10 text-white flex justify-center items-center relative"
            :style="{ width: `${100 - 100 * (item.current_memory / item.total_memory)}%` }"
          >
            <div
              v-if="item.process" class=" absolute left-0 top-0 w-1/2 flex h-10 bg-cyan-600"
              :style="{ width: `${100 * (item.process / item.total_memory)}%` }"
            />
            <span class="z-10">
              {{ Math.round((item.total_memory - item.current_memory) * 100) / 100 }}
              GB /
              {{ item.total_memory }}
              GB
            </span>
          </div>
        </div>
        <div v-if="item && item.process" class="grid grid-cols-3 w-full my-2 legend">
          <div class=" border-l-20 border-gray-500 pl-2">
            {{ locale.total }}
          </div>
          <div class=" border-l-20 border-main pl-2">
            {{ locale.consumed }}
          </div>
          <div v-if="item.process" class=" border-l-20 border-cyan-600 pl-2">
            {{ locale.process }} ({{ item.process }} GB)
          </div>
        </div>
        <div v-if="item && item.cache && item.cache.length > 0" class="mt-4 ">
          <span class="p-2 mr-4">
            {{ locale.cache }}:
          </span>
          <span v-for="cached, idx in item.cache" :key="idx" class=" bg-main p-2 m-1 ml-0 text-white inline-block cursor-default">
            <span v-for="v, k in cached" :key="k" :title="`${locale.cache_size}: ${v}GB`">{{ k }}</span>
          </span>
        </div>
      </div>
    </div>
    <small class=" block absolute bottom-0  text-center w-full text-gray-500 p-4">
      Botality &copy; 2023 Remixer Dec |  <b><a href="http://github.com/remixer-dec/botality-ii" target="_blank">Github</a></b>
    </small>
  </div>
</template>

<style scoped>
.legend > div {
  @apply break-words text-xs sm:text-base
}
</style>
