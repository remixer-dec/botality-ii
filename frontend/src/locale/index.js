const locales = ['ru', 'en']

let useLocale = 'en'
for (let i = 0; i < locales.length; i++) {
  useLocale = navigator.languages.includes(locales[i]) ? locales[i] : useLocale
  if (useLocale !== 'en') break
}
const urlParamsLocale = (new URLSearchParams(location.search)).get('lang')
useLocale = (locales.indexOf(urlParamsLocale) !== -1) ? urlParamsLocale : useLocale

const locale = (await import(`./lang/${useLocale}.js`)).default
locale.get = key => locale[key] || key

export default locale
