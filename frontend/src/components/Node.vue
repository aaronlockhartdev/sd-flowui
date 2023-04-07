<script setup lang="ts">
import { watch, ref } from 'vue'
import { Handle, Position } from '@vue-flow/core'

import Checkbox from '@/components/NodeCheckbox.vue'
import FileDropdown from '@/components/NodeFileDropdown.vue'
import { useGraphStore } from '@/stores/graph'

interface Connection {
  id: string
  name: string
  type: string
}

const props = defineProps<{
  data: {
    type: string
    values: { [key: string]: any }
  }
}>()

const store = useGraphStore()

const emits = defineEmits(['updateNode'])

const values = ref(props.data.values)

watch(values, (val) => emits('updateNode', val))
</script>

<template>
  <div class="wrapper">
    <div
      class="block min-w-[12rem] max-w-sm rounded-lg border border-gray-700 bg-gray-800 p-1 shadow"
    >
      <h5 class="px-2 text-sm font-medium text-white">
        {{ props.data.type }}
      </h5>
      <hr class="my-1 h-px border-0 bg-gray-700" />
      <div class="flex items-stretch">
        <ul class="flex min-w-0 flex-col">
          <li v-for="param in store.templates[props.data.type].params">
            <Checkbox
              v-if="param.component.type === 'Checkbox'"
              :name="param.name"
              :value="values[param.id]"
              :component="param.component as any"
              @update-val="(val) => (values[param.id] = val)"
            />
            <FileDropdown
              v-else-if="param.component.type === 'FileDropdown'"
              :name="param.name"
              :value="values[param.id]"
              :component="param.component as any"
              @update-val="(val) => (values[param.id] = val)"
            />
          </li>
        </ul>
        <ul class="right-0 ml-1 flex flex-col">
          <li
            v-for="output in store.templates[props.data.type].outputs"
            class="my-1 flex items-center justify-end"
          >
            <p class="mr-2 text-right text-xs font-normal text-gray-300">{{ output.name }}</p>
            <Handle :id="output.id" type="source" class="static h-1 w-1 rounded-full bg-gray-500" />
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
