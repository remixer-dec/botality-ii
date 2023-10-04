<script setup>
import { globalState } from '../state'

const props = defineProps(['message'])
</script>

<template>
  <div
    v-if="!globalState.botIsRunning && !globalState.botStateUnknown"
    class="flex flex-col w-full align-center justify-center h-screen items-center"
  >
    <div v-if="!globalState.botStateLocked" class="text-xl">
      <hi-wifi-off />
    </div>
    <div v-else class="animate-ping">
      <hi-wifi />
    </div>
    {{ props.message || '' }}
  </div>
</template>
