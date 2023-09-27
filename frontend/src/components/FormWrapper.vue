<template>
  <div class=" bg-white w-full min-h-[40px] border-b m-10 rounded-lg p-4">
    <div class="font-bold text-lg mb-2 text-center">
      <slot name="header" />
    </div>
    <hr class="my-4">
    <slot name="content" />
  </div>
</template>
