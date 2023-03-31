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

function hi() {
  console.log('fu')
  console.log(graphHandler.elements)
}
</script>

<template>
  <VueFlow v-model="elements" />
  <button click="hi()">hi</button>
</template>
