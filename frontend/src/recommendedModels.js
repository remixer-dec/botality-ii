const bajTTS = ['david', 'forsen', 'juice-wrld', 'obiwan', 'trump', 'xqc'].map((x) => {
  return {
    voice: x,
    model: `${x}.pth`,
    author: 'enlyth',
    repo: 'enlyth/baj-tts',
    path: 'models/',
    size: 0.9,
    rename: false,
    language: 'en'
  }
})

const ymbbTTS = [
  'adam_carolla_checkpoint_1360000',
  'alex_jones_checkpoint_2490000',
  'david_attenborough_checkpoint_2020000',
  'james_earl_jones_checkpoint_1600000',
  'joel_osteen_checkpoint_2550000',
  'neil_degrasse_tyson_checkpoint_1910000',
  'tim_dillon_checkpoint_1970000',
  'vincent_price_checkpoint_2080000'
].map((x) => {
  return {
    voice: x.split('_checkpoint')[0],
    model: `${x}.pth`,
    author: 'youmebangbang',
    repo: 'youmebangbang/vits_tts_models',
    path: '',
    size: 0.9,
    rename: true,
    language: 'en'
  }
})
const prTTSModels = ['G_20000', 'G_157', 'G_480', 'G_449', 'G_50000', 'G_18500.pth']
const prTTS = ['Biden20k', 'BillClinton', 'BorisJohnson', 'GeorgeBush', 'Obama50k', 'Trump18.5k'].map((x, i) => {
  return {
    voice: x.replace(/[0-9.]+k/, ''),
    model: `${prTTSModels[i]}.pth`,
    author: 'Nardicality',
    repo: 'Nardicality/so-vits-svc-4.0-models',
    path: `${x}/`,
    size: 0.5
  }
})

const amoTTSModels = ['G_50000', 'G_100000', 'G_85000']
const amoTTS = ['Glados_50k', 'Star-Trek-Computer', 'Boss_MGS_80k'].map((x, i) => {
  return {
    voice: x.replace(/_[0-9]+k|-/g, ''),
    model: `${amoTTSModels[i]}.pth`,
    author: 'Amo',
    repo: 'Amo/so-vits-svc-4.0_GA',
    path: `ModelsFolder/${x}/`,
    size: 0.5
  }
})

const tim = [{
  voice: 'Tim_Cook',
  model: 'Tim_Cook.pth',
  author: 'Sucial',
  repo: 'Sucial/so-vits-svc4.1-Tim_Cook',
  path: '',
  size: 0.2
}]

export const models = {
  TTS: {
    VITS: [
      ...bajTTS,
      ...ymbbTTS
    ],
    SO_VITS_SVC: [
      ...prTTS,
      ...amoTTS,
      ...tim
    ]
  }
}
