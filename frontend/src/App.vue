<script setup>
const notification = ref(null)
</script>

<template>
  <div id="app" class="bg-gray-300 min-h-full h-max">
    <Sidebar />
    <Notification ref="notification" class="right-4 top-4" />
    <main class="transform sm:translate-x-64 sm:mr-64">
      <RouterView />
    </main>
    <Modal />
  </div>
</template>

<style>
@import '%/formvuelar/dist/formvuelar.css';
html {
  touch-action: manipulation;
}
svg {
  display: inline-block !important;
}
</style>
