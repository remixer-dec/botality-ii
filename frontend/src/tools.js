export async function fetchJSON(filename, ...args) {
  const f = await fetch(filename, ...args)
  return await f.json()
}

export async function api(method, endpoint, options) {
  if (import.meta.env.DEV) {
    if (options.mock && options.mock._delay)
      return await (new Promise((resolve) => { setTimeout(() => resolve(options.mock), options.mock._delay) }))
    return options.mock
  }

  return fetchJSON(`${location.origin}/api/${endpoint}`, { method, ...options })
}
