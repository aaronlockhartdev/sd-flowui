<script setup lang="ts">
import CheckboxComponent from '@/components/CheckboxComponent.vue'
import { watch } from 'vue'
import type { Component } from 'vue'

const components: { [key: string]: Component } = {
  Checkbox: CheckboxComponent
}

interface Connection {
  id: string
  name: string
  type: string
}

const props = defineProps<{
  data: {
    label: string
    template: {
      inputs: Connection[]
      outputs: Connection[]
      params: {
        id: string
        name: string
        component: {
          type: string
        }
      }[]
    }
    values: { [key: string]: any }
  }
}>()

const emits = defineEmits(['updateNode'])

watch(props.data.values, (val) => {
  emits('updateNode', val)
})
</script>

<template>
  <div class="wrapper">
    <div class="block max-w-md rounded-lg border border-gray-700 bg-gray-800 p-1 shadow">
      <h5 class="px-2 text-sm font-medium tracking-tight text-white">
        {{ props.data.label }}
      </h5>
      <hr class="my-1 h-px border-0 bg-gray-700" />
      <ul v-for="param in props.data.template.params">
        <li v-if="param.component.type === 'Checkbox'">
          <CheckboxComponent
            :id="param.id"
            :name="param.name"
            :value="props.data.values[param.id]"
            :component="param.component as any"
            @update-val="
              (val) => {
                props.data.values[param.id] = val
              }
            "
          />
        </li>
      </ul>
    </div>
  </div>
</template>
