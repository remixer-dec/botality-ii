import { reactive } from 'vue'

export const globalState = reactive({
  botIsRunning: false,
  botStateText: 'stopped',
  botStateLocked: false
})
