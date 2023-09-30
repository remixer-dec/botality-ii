<template>
  <div class=" bg-white my-2 md:w-full lg:w-[43%] min-h-[40px] border-b lg:m-4 xl:mx-8 xl:my-4 2xl:mx-10 rounded-lg p-4 h-max overflow-x-hidden">
    <div class="font-bold text-lg mb-2 text-center">
      <slot name="header" />
    </div>
    <hr class="my-4">
    <slot name="content" />
  </div>
</template>
