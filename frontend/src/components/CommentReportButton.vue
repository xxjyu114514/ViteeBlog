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

const handleReportClick = () => {
  if (!userStore.isAuthenticated) {
    // 显示友好的未登录提示
    alert('请先登录后再进行举报操作');
    return
  }
  
  // 触发自定义事件，由父组件处理举报逻辑
  emit('report-click', props.commentId)
}

const emit = defineEmits(['report-click'])
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.report-btn {
  color: $color-danger;
  
  &:hover:not(:disabled) {
    color: darken($color-danger, 10%);
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