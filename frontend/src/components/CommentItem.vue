<template>
  <div class="comment-item">
    <!-- 作者信息 -->
    <div class="author-info">
      <div class="avatar">
        {{ getInitials(authorInfo.username) }}
      </div>
      <span class="username">{{ authorInfo.username }}</span>
      <span class="time">{{ formatRelativeTime(comment.createdAt) }}</span>
    </div>
    
    <!-- 评论内容 -->
    <div class="comment-content" v-html="renderedContent"></div>
    
    <!-- 操作区域 -->
    <div class="comment-actions">
      <button 
        class="action-btn" 
        :class="{ 'liked': localIsLiked }"
        @click="handleLike"
        :disabled="likeLoading"
      >
        <i class="icon-like"></i>
        {{ localLikeCount }}
      </button>
      <CommentReportButton 
        :comment-id="props.comment.id" 
        @report-click="handleReportClick"
      />
      <button 
        class="action-btn"
        @click="handleReply"
        :disabled="!userStore.isAuthenticated"
      >
        回复
      </button>
      <button v-if="canDelete" class="action-btn btn-del" @click="handleDelete" :disabled="deleteLoading">
        {{ deleteLoading ? '删除中...' : '删除' }}
      </button>
    </div>
    
    <!-- 举报弹窗 -->
    <Teleport to="body">
      <CommentReportModal
        :comment-id="props.comment.id"
        v-model:show="showReportModal"
        @report-success="handleReportSuccess"
      />
    </Teleport>
    
    <!-- 删除确认弹窗 -->
    <ConfirmModal
      :show="showDeleteConfirm"
      title="删除评论"
      message="确定要删除此评论吗？删除后不可恢复。"
      confirm-text="删除"
      :danger="true"
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
    />
    
    <!-- 回复表单（如果正在回复此评论） -->
    <div v-if="showReplyForm" class="reply-form-container">
      <textarea
        v-model="replyContent"
        class="form-input"
        placeholder="回复此评论..."
        :disabled="replyLoading"
        @input="clearReplyError"
        @keydown.enter.exact.prevent="submitReply"
      ></textarea>
      <div class="reply-actions">
        <button 
          class="btn-cancel"
          @click="cancelReply"
        >
          取消
        </button>
        <button 
          class="btn-submit"
          @click="submitReply"
          :disabled="!canSubmitReply || replyLoading"
        >
          {{ replyLoading ? '发送中...' : '发送' }}
        </button>
      </div>
      <div v-if="replyError" class="reply-error">
        {{ replyError }}
      </div>
    </div>
    
    <!-- 嵌套回复列表 -->
    <div v-if="comment.replies && comment.replies.length > 0" class="replies">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :article-id="articleId"
        @comment-liked="handleChildCommentLiked"
        @comment-replied="handleChildCommentReplied"
        @comment-deleted="(id) => emit('comment-deleted', id)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { createComment as createCommentApi, likeComment, deleteComment as deleteCommentApi } from '@/services/commentService'
import { renderInline } from '@/utils'

import CommentReportButton from './CommentReportButton.vue'
import CommentReportModal from './CommentReportModal.vue'
import ConfirmModal from './ConfirmModal.vue'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  articleId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['comment-liked', 'comment-replied', 'comment-reported', 'comment-deleted'])

const userStore = useUserStore()
const router = useRouter()

// 安全获取作者信息，处理 author 字段缺失的情况
const authorInfo = computed(() => {
  const author = props.comment.author
  return {
    username: author?.username || '匿名用户',
    avatar: author?.avatar || null
  }
})

const showReplyForm = ref(false)
const replyContent = ref('')
const replyLoading = ref(false)
const replyError = ref(null)

// 使用本地响应式状态管理点赞状态，避免直接修改props
const localIsLiked = ref(props.comment.isLiked)
const localLikeCount = ref(props.comment.likeCount)

// 监听props变化，同步到本地状态
watch(() => props.comment.isLiked, (newVal) => {
  localIsLiked.value = newVal
})

watch(() => props.comment.likeCount, (newVal) => {
  localLikeCount.value = newVal
})

const likeLoading = ref(false)
const deleteLoading = ref(false)
const showDeleteConfirm = ref(false)

const canDelete = computed(() => {
  return userStore.isAuthenticated && (userStore.isAdmin || userStore.userInfo?.id === props.comment.userId)
})

const handleDelete = async () => {
  showDeleteConfirm.value = false
  deleteLoading.value = true
  const result = await deleteCommentApi(props.comment.id)
  if (result.success) {
    emit('comment-deleted', props.comment.id)
  } else {
    alert(result.message || '删除失败')
  }
  deleteLoading.value = false
}

const handleLike = async () => {
  if (!userStore.isAuthenticated) {
    // 未登录用户点击点赞时跳转到登录页
    router.push('/login')
    return
  }
  
  if (likeLoading.value) return
  
  likeLoading.value = true
  
  try {
    const result = await likeComment(props.comment.id)
    
    if (result.success) {
      // 更新本地状态
      localIsLiked.value = result.data.isLiked
      localLikeCount.value = result.data.likeCount
      // 触发事件通知父组件
      emit('comment-liked', {
        ...props.comment,
        isLiked: result.data.isLiked,
        likeCount: result.data.likeCount,
      })
    }
  } catch (err) {
    console.error('Like toggle error:', err)
  } finally {
    likeLoading.value = false
  }
}

// 渲染Markdown内容
const renderedContent = computed(() => {
  if (!props.comment.content) return ''
  return renderInline(props.comment.content)
})

// 获取用户名首字母
const getInitials = (username) => {
  if (!username) return 'U'
  return username.charAt(0).toUpperCase()
}

// 格式化日期（相对时间）
const formatRelativeTime = (dateString) => {
  if (!dateString) return '刚刚'
  const date = new Date(dateString)
  const now = new Date()
  const diffInMs = now - date
  const diffInMinutes = Math.floor(diffInMs / 60000)
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)
  
  if (diffInMinutes < 1) return '刚刚'
  if (diffInMinutes < 60) return `${diffInMinutes}分钟前`
  if (diffInHours < 24) return `${diffInHours}小时前`
  if (diffInDays < 7) return `${diffInDays}天前`
  
  return date.toLocaleDateString('zh-CN', {
    month: 'numeric',
    day: 'numeric'
  })
}

const canSubmitReply = computed(() => {
  return replyContent.value.trim().length > 0 && 
         replyContent.value.trim().length <= 500
})

const clearReplyError = () => {
  replyError.value = null
}

const handleReply = () => {
  if (!userStore.isAuthenticated) {
    // 可以在这里触发登录提示，但暂时先禁用按钮
    return
  }
  showReplyForm.value = true
  replyContent.value = ''
  replyError.value = null
}

const cancelReply = () => {
  showReplyForm.value = false
  replyContent.value = ''
  replyError.value = null
}

const submitReply = async () => {
  if (!canSubmitReply.value || replyLoading.value) return
  
  replyLoading.value = true
  replyError.value = null
  
  try {
    const result = await createCommentApi(
      props.articleId,
      { 
        content: replyContent.value.trim(),
        parent_id: props.comment.id
      }
    )
    
    if (result.success) {
      // 触发事件通知父组件
      emit('comment-replied', result.data)
      cancelReply()
    } else {
      replyError.value = result.message || '回复失败，请稍后重试'
    }
  } catch (err) {
    console.error('Reply submit error:', err)
    replyError.value = '网络错误，请检查网络连接后重试'
  } finally {
    replyLoading.value = false
  }
}

const handleChildCommentLiked = (updatedComment) => {
  emit('comment-liked', updatedComment)
}

const handleChildCommentReplied = (newComment) => {
  emit('comment-replied', newComment)
}

// 举报弹窗显示状态
const showReportModal = ref(false)

// 举报按钮点击处理
const handleReportClick = (commentId) => {
  showReportModal.value = true;
}

// 举报成功处理
const handleReportSuccess = () => {
  // 显示成功提示（可以使用全局通知组件，这里简单用alert）
  alert('举报成功！感谢您的监督，我们会尽快处理。')
  // 触发事件通知父组件（可选）
  emit('comment-reported', props.comment.id)
}

</script>

<style scoped lang="scss">
@use '@/assets/styles/components/comment';

.reply-form-container {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.form-input {
  width: 100%;
  min-height: 80px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  line-height: 1.5;
  resize: vertical;
  margin-bottom: 12px;
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  
  .btn-cancel {
    background: none;
    border: 1px solid #d1d5db;
    color: #6b7280;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      background: #f9fafb;
    }
  }
  
  .btn-submit {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    
    &:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
  }
}

.reply-error {
  margin-top: 8px;
  color: #ef4444;
  font-size: 0.85rem;
}

.btn-del { color: #ef4444; &:hover { text-decoration: underline; } }
</style>