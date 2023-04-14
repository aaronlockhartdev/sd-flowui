<script setup lang="ts">
import { watch, ref } from 'vue'

const props = defineProps<{
  node_id: string
  name: string
  value: boolean
  component: {
    default: boolean
  }
}>()

const emits = defineEmits(['updateVal'])

const checked = ref(props.value)
watch(checked, (val: boolean) => {
  emits('updateVal', val)
})
</script>

<template>
  <div class="wrapper">
    <div class="mx-2 my-1 flex items-center">
      <input
        :id="`checkbox_${name}_${props.node_id}`"
        type="checkbox"
        class="h-3.5 w-3.5 rounded border-gray-600 bg-gray-700 text-blue-600 focus:ring-2 focus:ring-blue-600 focus:ring-offset-gray-800"
        v-model="checked"
      />
      <label
        :for="`checkbox_${name}_${props.node_id}`"
        class="ml-2 p-0 text-xs font-normal text-gray-300"
        >{{ props.name }}</label
      >
    </div>
  </div>
</template>

<style scoped>
.container {
  padding: 100px;
}

.checkbox-icon {
  background: black;
  width: 1rem;
  height: 1rem;
}

.checkbox-icon-checked {
  background-color: white;
}
</style>
