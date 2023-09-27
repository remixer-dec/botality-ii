<template>
  <div id="app" class="bg-gray-300 min-h-full h-max">
    <Sidebar />
    <main class="transform translate-x-64 mr-64">
      <RouterView />
    </main>
  </div>
</template>

<style>
@import '../node_modules/formvuelar/dist/formvuelar.css';
svg {
  display: inline-block !important;
}
</style>
