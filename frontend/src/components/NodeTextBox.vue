<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = defineProps<{
  id: string
  name: string
  value: string
  component: {
    default: string
    placeholder: string
    regex: string
    maxlen: number
  }
}>()

const re = new RegExp(props.component.regex, 'g')

const emits = defineEmits(['updateVal'])

const text = ref(props.value)

watch(text, (val) => emits('updateVal', val))

const numWords = computed(() => Array.from(text.value.matchAll(re)).length)
</script>

<template>
  <div class="wrapper">
    <div class="mx-2 my-1 w-[18rem]">
      <div class="my-1 flex justify-between">
        <label :for="`textarea_${name}_${props.id}`" class="text-xs font-normal text-gray-300">{{
          props.name
        }}</label>
        <p v-if="props.component.regex" class="text-xs font-normal text-gray-300">
          {{ numWords }}/{{ props.component.maxlen ? props.component.maxlen : '&infin;' }}
        </p>
      </div>

      <textarea
        :id="`textarea_${name}_${props.id}}`"
        rows="6"
        :class="
          props.component.maxlen &&
          numWords > props.component.maxlen && [
            'ring-red-500',
            'focus:ring-red-500',
            'border-red-500',
            'focus:border-red-500'
          ]
        "
        class="nodrag nowheel block w-full resize-none rounded-lg border border-gray-600 bg-gray-700 p-1.5 text-xs text-white placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500"
        :placeholder="props.component.placeholder"
        v-model="text"
      ></textarea>
    </div>
  </div>
</template>
