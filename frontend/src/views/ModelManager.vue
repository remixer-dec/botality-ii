<script setup>
import { onMounted, getCurrentInstance, watch, defineProps } from 'vue'
import { api } from '../tools'
import { globalState } from '../state'
import SetupWindow from '../components/ModelSetupWindow.vue'

const props = defineProps(['catType', 'subType'])
const { proxy } = getCurrentInstance()

const tabs = ref([
  { name: 'TTS' },
  { name: 'LLM' }
])

const ttsTabs = ref([
  { name: 'SO_VITS_SVC' },
  { name: 'VITS' }
])

const llmTabs = ref([
  { name: 'GGUF' }
])

const categoryTabs = ref(null)
const ttsTabsComponent = ref(null)
const llmTabsComponent = ref(null)
const subMenuSelectedItem = computed(() => subitem_map[categoryTabs?.value?.selectedItem]?.selectedItem)

const subitem_map = reactive({
  TTS: ttsTabsComponent,
  LLM: llmTabsComponent
})

function getCategoryHeaders(category, install) {
  const hmap = {
    TTS: ['Voice', 'Path', 'Size (GB)'],
    LLM: ['Name', 'Path', 'Size (GB)']
  }
  return [...hmap[category], install ? 'Install' : 'Uninstall']
}
function getCategoryKeys(category) {
  const kmap = {
    TTS: ['voice', 'path', 'size'],
    LLM: ['name', 'path', 'size']
  }
  return kmap[category]
}

const installed_models = ref([])
const recommended_models = ref([])

const refreshModels = async () => {
  const recommended = (await import('../recommendedModels')).models
  recommended_models.value = recommended
  try {
    const installed = await api('GET', 'models')
    if (installed.error) throw new Error(installed.error)
    installed_models.value = installed.response || []

    // hide installed models from recommended
    for (const modelType in recommended_models.value) {
      for (const modelSubtype in recommended_models.value[modelType]) {
        const targetSet = new Set()
        installed_models.value[modelType][modelSubtype].forEach((x) => {
          targetSet.add(x.repo + (x.voice || x.model))
        })
        for (const recModel of recommended_models.value[modelType][modelSubtype]) {
          if (targetSet.has(recModel.repo + (recModel.voice || recModel.model)))
            recModel.hide = true
        }
      }
    }
  }
  catch (e) {
    proxy.$root.$emit('showNotification', { message: String(e), type: 'error' })
  }
}

proxy.$root.$on('refreshModels', refreshModels)
watch(() => globalState.botIsRunning, () => globalState.botIsRunning ? refreshModels() : null)
onMounted(refreshModels)

function showInstallWindow() {
  proxy.$root.$emit('showModal', { component: SetupWindow, data: {} })
}
</script>

<template>
  <div class="w-full flex box-border flex-wrap justify-evenly flex-col">
    <div v-if="globalState.botIsRunning" class=" w-full flex flex-col">
      <div class=" m-2 flex w-auto bg-white p-2 rounded-md relative">
        <div>
          <div class="mb-2">
            Pretrained Models
            <div class="bg-main p-2 text-white rounded-md absolute right-2 top-2 cursor-pointer" @click="showInstallWindow">
              Install custom model
            </div>
          </div>
          <Tabs ref="categoryTabs" :items="tabs" class="my-1" :default="props.catType" />
          <div v-if="categoryTabs">
            <Tabs v-if="categoryTabs.selectedItem === 'TTS'" ref="ttsTabsComponent" :items="ttsTabs" :default="props.subType" />
            <Tabs v-if="categoryTabs.selectedItem === 'LLM'" ref="llmTabsComponent" :items="llmTabs" :default="props.subType" />
          </div>
        </div>
      </div>

      <div class=" m-2 flex flex-col bg-white w-auto p-2 rounded-md">
        <div class="mb-2">
          Installed Models
        </div>
        <ModelTable
          v-if="categoryTabs && categoryTabs.selectedItem && subMenuSelectedItem
            && installed_models && installed_models[categoryTabs.selectedItem]"
          :headers="getCategoryHeaders(categoryTabs.selectedItem, false)"
          :data="installed_models[categoryTabs.selectedItem][subMenuSelectedItem]"
          :keys="getCategoryKeys(categoryTabs.selectedItem)"
          :can-be-installed="false"
          :model-type="subMenuSelectedItem"
        />
        <div class="mt-8 mb-2">
          Recommended Models
        </div>
        <ModelTable
          v-if="categoryTabs && categoryTabs.selectedItem && subMenuSelectedItem
            && recommended_models && recommended_models[categoryTabs.selectedItem]"
          :headers="getCategoryHeaders(categoryTabs.selectedItem, true)"
          :data="recommended_models[categoryTabs.selectedItem][subMenuSelectedItem]"
          :keys="getCategoryKeys(categoryTabs.selectedItem)"
          :can-be-installed="true"
          :model-type="subMenuSelectedItem"
        />
      </div>
    </div>
    <Offline message="Please start the bot to manage models." />
  </div>
</template>

<style scoped>
</style>
