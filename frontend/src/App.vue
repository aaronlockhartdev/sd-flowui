<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <nav class="h-12">
        <ul
          class="bottom-0 flex h-full items-end border-b border-gray-700 bg-gray-900 px-3 pb-0 pt-3 text-center text-sm font-medium text-gray-400"
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
      </nav>
    </div>
  </header>

  <RouterView />
</template>
