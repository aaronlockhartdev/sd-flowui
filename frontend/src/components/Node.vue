<script setup lang="ts">
import { watch, ref, defineAsyncComponent, onMounted, nextTick } from 'vue'
import type { Component, Ref } from 'vue'

import { Handle, Position } from '@vue-flow/core'

import { useGraphStore } from '@/stores/graph'
import type { Template } from '@/stores/graph'

const props = defineProps<{
  id: string
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

const components: [
  Component,
  {
    id: string
    name: string
    value: any
    component: Template['values'][0]['component']
  }
][] = []
for (const [k, v] of Object.entries(store.templates[props.data.type].values)) {
  components.push([
    defineAsyncComponent(() => import(`@/components/Node${v.component.type}.vue`)),
    {
      id: props.id,
      name: v.name,
      value: values.value[k],
      component: v.component
    }
  ])
}
</script>

<template>
  <div class="wrapper">
    <div
      :class="{
        'ring-blue-600': props.selected,
        'ring-2': props.selected
      }"
      class="block min-w-[12rem] max-w-lg rounded-lg border border-gray-700 bg-gray-800 p-1 shadow"
    >
      <h5 class="px-2 text-sm font-medium text-white">
        {{ props.data.type }}
      </h5>
      <hr class="my-1 h-px border-0 bg-gray-700" />
      <div class="flex items-stretch">
        <ul class="left-0 mr-2 flex flex-col">
          <li
            v-for="[k, v] in Object.entries(store.templates[props.data.type].inputs)"
            class="my-1 flex items-center"
          >
            <Handle
              :id="k"
              type="target"
              :position="Position.Left"
              class="static h-1 w-1 rounded-full bg-gray-500"
            />
            <p class="ml-1.5 text-xs text-gray-300">{{ v.name }}</p>
          </li>
        </ul>
        <ul class="flex min-w-0 flex-col">
          <li v-for="[c, props] in components">
            <component :is="c" v-bind="props" />
          </li>
        </ul>
        <ul class="right-0 ml-1 flex flex-col">
          <li
            v-for="[k, v] in Object.entries(store.templates[props.data.type].outputs)"
            class="my-1 flex items-center justify-end"
          >
            <p class="mr-1.5 text-right text-xs text-gray-300">{{ v.name }}</p>
            <Handle
              :id="k"
              type="source"
              :position="Position.Right"
              class="static h-1 w-1 rounded-full bg-gray-500"
            />
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
