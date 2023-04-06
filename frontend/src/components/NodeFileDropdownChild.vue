<script setup lang="ts">
import { ref, watch } from 'vue'

import type { Directory } from '@/stores/files'

const props = defineProps<{
  struct: Directory
  parentExpanded: boolean
  dir: string
}>()

const emits = defineEmits(['onChange'])

const expanded = ref(false)

watch(
  () => props.parentExpanded,
  (val) => {
    if (!val) expanded.value = false
  }
)
</script>

<template>
  <button
    @click="
      () => {
        if (Object.keys(props.struct).length > 0) expanded = !expanded
      }
    "
    class="flex w-full items-center justify-between px-3 py-2 hover:bg-gray-600 hover:text-white"
  >
    <p class="start-0 w-full truncate whitespace-nowrap text-left text-xs">{{ props.dir }}</p>
    <svg
      aria-hidden="true"
      class="h-4 w-4"
      fill="currentColor"
      viewBox="0 0 20 20"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fill-rule="evenodd"
        d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
        clip-rule="evenodd"
      ></path>
    </svg>
  </button>
  <ul
    :class="{ hidden: !expanded, 'shadow-inner': expanded }"
    class="flex w-44 flex-col items-stretch text-sm text-gray-200"
    b
  >
    <li v-for="key in Object.keys(props.struct)">
      <button
        v-if="!props.struct[key]"
        @click="() => emits('onChange', [key])"
        class="block w-full truncate whitespace-nowrap px-3 py-2 hover:bg-gray-600 hover:text-white"
      >
        <p class="start-0 w-full truncate whitespace-nowrap text-left text-xs">{{ key }}</p>
      </button>
      <NodeFileDropdownChild
        v-else
        @on-change="(acc) => emits('onChange', [key, ...acc])"
        :dir="key"
        :struct="props.struct[key]!"
        :parent-expanded="expanded"
      />
    </li>
  </ul>
</template>
