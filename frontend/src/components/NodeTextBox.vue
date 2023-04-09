<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  name: string
  value: string
  component: {
    default: string
    placeholder: string
    maxlen: string
  }
}>()

const emits = defineEmits(['updateVal'])

const text = ref(props.value)

watch(text, (val) => emits('updateVal', val))
</script>

<template>
  <div class="wrapper">
    <div class="mx-2 my-1 w-[20rem]">
      <label for="message" class="mb-1 block text-xs text-gray-300">{{ props.name }}</label>
      <textarea
        rows="5"
        class="block w-full rounded-lg border border-gray-600 bg-gray-700 p-1.5 text-xs text-white placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500 dark:focus:ring-blue-500"
        :placeholder="props.component.placeholder"
        v-model="text"
      ></textarea>
    </div>
  </div>
</template>
