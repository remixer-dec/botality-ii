<script setup>
import { onMounted } from 'vue'
import { api } from '../tools'

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

const installed_models = ref([])
const recommended_models = ref([])

onMounted(async () => {
  const recommended = (await import('../recommendedModels')).models
  recommended_models.value = recommended
  try {
    const installed = await api('GET', 'models')
    installed_models.value = installed.response || []
  }
  catch (e) {

  }
})
</script>

<template>
  <div class="w-full flex box-border flex-wrap justify-evenly flex-col">
    <div class=" w-full flex flex-col">
      <div class=" m-2 flex w-auto bg-white p-2 rounded-md">
        <div>
          <div class="mb-2">
            Pretrained Models
          </div>
          <Tabs ref="categoryTabs" :items="tabs" class="my-1" />
          <div v-if="categoryTabs">
            <Tabs v-if="categoryTabs.selectedItem === 'TTS'" ref="ttsTabsComponent" :items="ttsTabs" />
            <Tabs v-if="categoryTabs.selectedItem === 'LLM'" ref="llmTabsComponent" :items="llmTabs" />
          </div>
        </div>
      </div>

      <div class=" m-2 flex flex-col bg-white w-auto p-2 rounded-md">
        <div class="mb-2">
          Installed Models
        </div>
        <ModelTable
          v-if="categoryTabs && categoryTabs.selectedItem === 'TTS' && subMenuSelectedItem
            && installed_models && installed_models[categoryTabs.selectedItem]"
          :headers="['Voice', 'Path', 'Size (GB)']"
          :data="installed_models[categoryTabs.selectedItem][subMenuSelectedItem]"
          :keys="['voice', 'path', 'size']"
          :can-be-installed="false"
        />
        <div class="mt-8 mb-2">
          Recommended Models
        </div>
        <ModelTable
          v-if="categoryTabs && categoryTabs.selectedItem === 'TTS' && subMenuSelectedItem
            && recommended_models && recommended_models[categoryTabs.selectedItem]"
          :headers="['Voice', 'Repo', 'Size (GB)', 'Install']"
          :data="recommended_models[categoryTabs.selectedItem][subMenuSelectedItem]"
          :keys="['voice', 'repo', 'size']"
          :can-be-installed="true"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>