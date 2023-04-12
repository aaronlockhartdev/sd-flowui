<script setup lang="ts">
import { BaseEdge, Position, getBezierPath } from '@vue-flow/core'
import { computed } from 'vue'

const props = defineProps<{
  id: string
  sourceX: number
  sourceY: number
  targetX: number
  targetY: number
  markerEnd: string
  sourceHandleId: string
  targetHandleId: string
}>()

const path = computed(() =>
  getBezierPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    targetX: props.targetX,
    targetY: props.targetY,
    curvature: 0.3,
    sourcePosition: Position.Right,
    targetPosition: Position.Left
  })
)
</script>

<template>
  <BaseEdge
    :id="id"
    :path="path[0]"
    :marker-end="markerEnd"
    class="rounded-full fill-none stroke-gray-500 stroke-2"
  />
</template>

<style></style>
