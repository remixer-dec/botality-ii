import { reactive } from 'vue'

export const globalState = reactive({
  botStateUnknown: true,
  botIsRunning: false,
  botStateText: 'stopped',
  botStateLocked: false
})
