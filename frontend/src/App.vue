<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <nav class="h-12">
        <ul
          class="bottom-0 flex h-full items-end border-b-[2px] border-gray-800 bg-gray-900 px-3 pb-0 text-center text-sm font-medium text-gray-400"
        >
          <li class="mr-4 flex h-full items-center self-center p-3">
            <img src="/favicon.svg" class="mr-2 h-full" />
            <h5 class="text-lg font-bold text-white">FlowUI</h5>
          </li>

          <li class="mx-1 mt-2">
            <RouterLink
              to="/"
              active-class="text-blue-500 bg-gray-800"
              class="inline-block rounded-t-lg px-3 py-2 hover:text-white"
              >Graph</RouterLink
            >
          </li>
          <li class="mx-1 mt-2">
            <RouterLink
              to="/browser"
              active-class="text-blue-500 bg-gray-800"
              class="inline-block rounded-t-lg px-3 py-2 hover:text-gray-200"
              >Browser</RouterLink
            >
          </li>
        </ul>
      </nav>
    </div>
  </header>

  <RouterView />
</template>
