<script setup lang="ts">
import { watch, ref, computed } from 'vue'

import { useFilesStore } from '@/stores/files'

import Child from '@/components/NodeFileDropdownChild.vue'

const props = defineProps<{
  id: string
  name: string
  value: string[]
  component: {
    default: string[]
    directory: string[]
  }
}>()

const emits = defineEmits(['updateVal'])

const store = useFilesStore()

const struct = computed(() => store.getSubStructure(props.component.directory))

const value = ref(props.value)

watch(value, (val, prevVal) => {
  if (JSON.stringify(val) !== JSON.stringify(prevVal)) emits('updateVal', val)
})

const expanded = ref(false)
</script>

<template>
  <div class="wrapper">
    <div class="inline-flex max-w-full items-center p-2">
      <h1 class="pr-2 text-xs font-normal text-gray-300">{{ props.name }}</h1>

      <button
        @click="() => (expanded = !expanded)"
        class="inline-flex min-w-0 items-center rounded-lg bg-blue-600 px-2 py-0.5 hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-800"
        type="button"
      >
        <p
          class="start-0 w-full truncate whitespace-nowrap text-left text-xs font-normal text-white"
        >
          {{ value.at(-1) }}
        </p>

        <svg
          class="ml-2 h-4 w-4"
          aria-hidden="true"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          ></path>
        </svg>
      </button>
    </div>
    <div :class="{ hidden: !expanded }" class="absolute w-44 rounded-lg bg-gray-700">
      <ul class="flex flex-col items-stretch py-2 text-sm text-gray-200">
        <li v-for="key in Object.keys(struct)">
          <button
            v-if="!struct[key]"
            @click="() => (value = [...props.component.directory, key])"
            class="block w-full truncate whitespace-nowrap px-3 py-2 hover:bg-gray-600 hover:text-white"
          >
            <p class="start-0 w-full truncate whitespace-nowrap text-left text-xs">{{ key }}</p>
          </button>
          <Child
            v-else
            @on-change="(acc) => (value = [...props.component.directory, key, ...acc])"
            :dir="key"
            :struct="struct[key]!"
            :parent-expanded="expanded"
          />
        </li>
      </ul>
    </div>
  </div>
</template>
