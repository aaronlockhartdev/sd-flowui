<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <ul
        class="flex flex-wrap border-b border-gray-700 bg-gray-900 px-3 pt-3 text-center text-sm font-medium text-gray-400"
      >
        <li class="mr-2">
          <RouterLink
            to="/"
            active-class="text-blue-500 bg-gray-800"
            class="inline-block rounded-t-lg px-3 py-2"
            >Graph</RouterLink
          >
        </li>
        <li class="mr-2">
          <RouterLink
            to="/browser"
            active-class="text-blue-500 bg-gray-800"
            class="inline-block rounded-t-lg px-3 py-2"
            >Browser</RouterLink
          >
        </li>
      </ul>
    </div>
  </header>

  <RouterView />
</template>
