<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { graphHandler } from '@/services/graph'

const elements = ref(graphHandler.elements)

onMounted(() => {
  graphHandler.addRef(elements)
})

onUnmounted(() => {
  graphHandler.removeRef(elements)
})

function logElements() {
  console.log(graphHandler.elements)
}
</script>

<template>
  <VueFlow v-model="elements" />
  <button @click="logElements">logElements</button>
</template>
