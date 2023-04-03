<script setup lang="ts">
import CheckboxComponent from '@/components/CheckboxComponent.vue'

interface Connection {
  id: string
  name: string
  type: string
}

const props = defineProps<{
  data: {
    template: {
      inputs: Connection[]
      outputs: Connection[]
      params: {
        id: string
        name: string
        component: {
          name: string
        }
      }[]
    }
    values: object
  }
}>()

console.log(props.data.template.params)

const emits = defineEmits(['change'])
</script>

<template>
  <div class="wrapper">
    <ul v-for="param in props.data.template.params">
      <li v-if="param.component.name === 'Checkbox'">
        <CheckboxComponent :id="param.id" :name="param.name" :component="param.component as any" />
      </li>
    </ul>
  </div>
</template>
