<template>
  <div class="comment-form">
    <div class="form-header">
      <h3 class="title">发表评论</h3>
      <p class="subtitle">分享您的想法和观点</p>
    </div>
    
    <textarea
      v-model="commentContent"
      class="form-input"
      placeholder="写下您的评论..."
      :disabled="loading || !userStore.isAuthenticated"
      @input="clearError"
    ></textarea>
    
    <div class="form-actions">
      <button 
        class="btn-submit"
        @click="handleSubmit"
        :disabled="!canSubmit || loading"
      >
        {{ loading ? '提交中...' : '发表评论' }}
      </button>
    </div>
    
    <div v-if="error" class="form-error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { createComment as createCommentApi } from '@/services/commentService'

const props = defineProps({
  articleId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['comment-submitted'])

const userStore = useUserStore()
const commentContent = ref('')
const loading = ref(false)
const error = ref(null)

const canSubmit = computed(() => {
  return commentContent.value.trim().length > 0 && 
         commentContent.value.trim().length <= 1000
})

const clearError = () => {
  error.value = null
}

const handleSubmit = async () => {
  if (!canSubmit.value || loading.value) return
  
  // 验证用户登录状态
  if (!userStore.isAuthenticated) {
    error.value = '请先登录后再发表评论'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    const result = await createCommentApi(
      props.articleId,
      { content: commentContent.value.trim() }
    )
    
    if (result.success) {
      // 清空表单并触发事件
      commentContent.value = ''
      emit('comment-submitted', result.data)
    } else {
      error.value = result.message || '发表评论失败，请稍后重试'
    }
  } catch (err) {
    console.error('Comment form submit error:', err)
    error.value = '网络错误，请检查网络连接后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
@use '@/assets/styles/components/comment';

.form-error {
  margin-top: 12px;
  color: #ef4444;
  font-size: 0.9rem;
}
</style>