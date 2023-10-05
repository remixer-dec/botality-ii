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

const standardQuants = ['2_K', '3_K_L', '3_K_M', '3_K_S', '4_0', '4_K_M', '4_K_S', '5_0', '5_K_M', '5_K_S', '6_K', '8_0']
const theBloke = [
  ['TheBloke/llama2_7b_chat_uncensored-GGUF', 'llama2_7b_chat_uncensored.Q$.gguf', standardQuants],
  ['TheBloke/Luna-AI-Llama2-Uncensored-GGUF', 'luna-ai-llama2-uncensored.Q$.gguf', standardQuants],
  ['TheBloke/Mistral-7B-Instruct-v0.1-GGUF', 'mistral-7b-instruct-v0.1.Q$.gguf', standardQuants],
  ['TheBloke/WizardLM-1.0-Uncensored-Llama2-13B-GGUF',
    'wizardlm-1.0-uncensored-llama2-13b.Q$.gguf',
    standardQuants
  ],
  ['TheBloke/Speechless-Llama2-Hermes-Orca-Platypus-WizardLM-13B-GGUF',
    'speechless-llama2-hermes-orca-platypus-wizardlm-13b.Q$.gguf',
    standardQuants
  ],
  ['TheBloke/OpenBuddy-Llama2-13B-v11.1-GGUF',
    'openbuddy-llama2-13b-v11.1.Q$.gguf',
    standardQuants
  ],
  ['TheBloke/TinyLlama-1.1B-Chat-v0.3-GGUF', 'tinyllama-1.1b-chat-v0.3.Q$.gguf', standardQuants]
].map((x) => {
  return {
    name: x[1].split('.')[0],
    repo: x[0],
    model: x[1],
    quants: x[2],
    author: 'TheBloke',
    path: '',
    size: '2-14'
  }
})

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
  },
  LLM: {
    GGUF: [
      ...theBloke
    ]
  }
}
