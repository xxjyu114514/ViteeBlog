<template>
  <button 
    class="action-btn report-btn"
    @click="handleReportClick"
    :disabled="!userStore.isAuthenticated"
    title="举报不当内容"
  >
    <i class="icon-report"></i>
    举报
  </button>
</template>

<script setup>
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const props = defineProps({
  commentId: {
    type: Number,
    required: true
  }
})

const userStore = useUserStore()
const router = useRouter()

const emit = defineEmits(['report-click'])

const handleReportClick = () => {
  if (!userStore.isAuthenticated) {
    alert('请先登录后再进行举报操作');
    return
  }
  
  emit('report-click', props.commentId)
}

</script>

<style scoped lang="scss">
@use 'sass:color';
@use '@/assets/styles/variables' as *;

.report-btn {
  color: $color-danger;
  
  &:hover:not(:disabled) {
    color: color.adjust($color-danger, $lightness: -10%);
  }
  
  &:disabled {
    color: $text-muted;
  }
  
  .icon-report::before {
    content: "⚠️";
    font-size: 1.1em;
  }
}
</style>