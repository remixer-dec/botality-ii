import { globalState as G } from './state'
import { api } from './tools'

export async function isBotAlive() {
  try {
    await api('GET', 'ping').then((r) => {
      if (r?.response === 'ok') {
        G.botIsRunning = true
        G.botStateText = 'running'
      }
      else { throw new Error('Incorrect response') }
    })
  }
  catch (e) {
    G.botIsRunning = false
    G.botStateText = 'stopped'
  }
  finally {
    G.botStateUnknown = false
  }
}

export function toggleBot() {
  if (G.botStateLocked) return
  G.botStateLocked = true
  if (!G.botIsRunning) {
    api('POST', 'bot/start', { mock: { response: 'ok' } }).then((data) => {
      G.botStateText = 'starting'
      if (data?.response === 'ok') {
        G.botStateText = 'initializing'
        return new Promise((resolve, reject) => {
          let isResolved = false
          const interval = setInterval(() => {
            api('GET', 'ping', { mock: { _delay: 3000, response: 'ok' } }).then((body) => {
              if (!(body?.response === 'ok')) return
              clearInterval(interval)
              clearTimeout(giveUp)
              if (isResolved) return
              resolve()
              isResolved = true
              G.botIsRunning = true
              G.botStateText = 'running'
              G.botStateLocked = false
            }).catch(() => {})
          }, 1000)
          const giveUp = setTimeout(() => {
            clearInterval(interval)
            reject(new Error('connection timeout'))
          }, 30000)
        })
      }
    }).catch(() => {
      G.botStateText = 'connection error'
      G.botStateLocked = false
    })
  }
  else {
    G.botStateText = 'stopping'
    api('POST', 'bot/stop', { mock: { response: 'ok' } }).then((data) => {
      if (data?.response === 'ok') {
        setTimeout(() => {
          G.botIsRunning = false
          G.botStateText = 'stopped'
          G.botStateLocked = false
        }, 1000)
      }
      else {
        isBotAlive()
        G.botStateLocked = false
      }
    }).catch(() => {
      G.botStateText = 'connection error'
      G.botStateLocked = false
    })
  }
}
