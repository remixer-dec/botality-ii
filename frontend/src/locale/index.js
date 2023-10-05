const locales = ['ru']

let useLocale = 'en'
for (let i = 0; i < locales.length; i++) {
  useLocale = navigator.languages.includes(locales[i]) ? locales[i] : useLocale
  if (useLocale !== 'en') break
}

const locale = (await import(`./lang/${useLocale}.js`)).default
locale.get = key => locale[key] || key

export default locale
