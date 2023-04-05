<script setup lang="ts">
import { useFilesStore } from '@/stores/files'

const store = useFilesStore()
console.log(store.fileStructure)
</script>
