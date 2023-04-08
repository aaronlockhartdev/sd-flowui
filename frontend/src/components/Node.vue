<script setup lang="ts">
import { watch, ref } from 'vue'
import { Handle, Position } from '@vue-flow/core'

import Checkbox from '@/components/NodeCheckbox.vue'
import FileDropdown from '@/components/NodeFileDropdown.vue'
import { useGraphStore } from '@/stores/graph'

const props = defineProps<{
  selected: boolean
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
      :class="{
        'ring-blue-600': props.selected,
        'ring-2': props.selected
      }"
      class="block min-w-[12rem] max-w-sm rounded-lg border border-gray-700 bg-gray-800 p-1 shadow"
    >
      <h5 class="px-2 text-sm font-medium text-white">
        {{ props.data.type }}
      </h5>
      <hr class="my-1 h-px border-0 bg-gray-700" />
      <div class="flex items-stretch">
        <ul class="flex min-w-0 flex-col">
          <li v-for="[k, v] in Object.entries(store.templates[props.data.type].values)">
            <Checkbox
              v-if="v.component.type === 'Checkbox'"
              :name="v.name"
              :value="values[k]"
              :component="v.component as any"
              @update-val="(val) => (values[k] = val)"
            />
            <FileDropdown
              v-else-if="v.component.type === 'FileDropdown'"
              :name="v.name"
              :value="values[k]"
              :component="v.component as any"
              @update-val="(val) => (values[k] = val)"
            />
          </li>
        </ul>
        <ul class="right-0 ml-1 flex flex-col">
          <li
            v-for="[k, v] in Object.entries(store.templates[props.data.type].outputs)"
            class="my-1 flex items-center justify-end"
          >
            <p class="mr-2 text-right text-xs font-normal text-gray-300">{{ v.name }}</p>
            <Handle :id="k" type="source" class="static h-1 w-1 rounded-full bg-gray-500" />
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
