<script setup lang="ts">
import { computed } from 'vue'

console.log('FUCK YEAH')

const props = defineProps<{
  id: string
  name: string
  component: {
    default: boolean
  }
}>()

const emits = defineEmits(['onChange'])

let value = props.component.default

const iconClass = computed(() => {
  return {
    'checkbox-icon': true,
    ':checked': value
  }
})

function toggle() {
  value = !value
  emits('onChange', value)
}
</script>

<template>
  <div class="wrapper">
    <div :class="iconClass" @click="toggle" />
  </div>
</template>

<style scoped lang="sass"></style>
