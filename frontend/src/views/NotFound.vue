<script setup>
import locale from '../locale'
</script>

<template>
  <section class="text-gray-600 body-font">
    <div
      class="container flex flex-col items-center justify-center px-5 py-24 mx-auto"
    >
      <img
        class="object-cover object-center w-5/6 mb-10 rounded lg:w-2/6 md:w-3/6"
        alt="hero"
        src="@/assets/not-found.svg"
      >
      <div v-once class="w-full text-center lg:w-2/3">
        <h2>404</h2>
        <p class="mb-8 leading-relaxed dark:text-gray-300">
          {{ locale.page404 }}
        </p>
        <div class="flex justify-center">
          <RouterLink to="/">
            <span class="fvl-submit-button m-2 inline-block cursor-pointer bg-opacity-70">
              {{ locale.goBack }}
            </span>
          </RouterLink>
        </div>
      </div>
    </div>
  </section>
</template>
