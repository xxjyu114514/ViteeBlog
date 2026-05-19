<template>
  <div class="comment-item">
    <!-- 作者信息 -->
    <div class="author-info">
      <div class="avatar">
        {{ getInitials(authorInfo.username) }}
      </div>
      <span class="username">{{ authorInfo.username }}</span>
      <span class="time">{{ formatDate(comment.created_at) }}</span>
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
    </div>
    
    <!-- 举报弹窗 -->
    <Teleport to="body">
      <CommentReportModal
        :comment-id="props.comment.id"
        v-model:show="showReportModal"
        @report-success="handleReportSuccess"
      />
    </Teleport>
    
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
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'
import { useCommentAPI } from '@/composables/useCommentAPI'

// 导入举报组件
import CommentReportButton from './CommentReportButton.vue'
import CommentReportModal from './CommentReportModal.vue'

// 初始化Markdown解析器（简化版，仅用于评论内容）
const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true
})

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

const emit = defineEmits(['comment-liked', 'comment-replied', 'comment-reported'])

const userStore = useUserStore()
const router = useRouter()
const { createComment, toggleCommentLike } = useCommentAPI()

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
const localIsLiked = ref(props.comment.is_liked)
const localLikeCount = ref(props.comment.like_count)

// 监听props变化，同步到本地状态
watch(() => props.comment.is_liked, (newVal) => {
  localIsLiked.value = newVal
})

watch(() => props.comment.like_count, (newVal) => {
  localLikeCount.value = newVal
})

const likeLoading = ref(false)

const handleLike = async () => {
  if (!userStore.isAuthenticated) {
    // 未登录用户点击点赞时跳转到登录页
    router.push('/login')
    return
  }
  
  if (likeLoading.value) return
  
  likeLoading.value = true
  
  try {
    const result = await toggleCommentLike(props.comment.id)
    
    if (result.success) {
      // 更新本地状态
      localIsLiked.value = result.data.is_liked
      localLikeCount.value = result.data.like_count
      // 触发事件通知父组件
      emit('comment-liked', {
        ...props.comment,
        is_liked: result.data.is_liked,
        like_count: result.data.like_count
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
  return md.renderInline(props.comment.content)
})

// 获取用户名首字母
const getInitials = (username) => {
  if (!username) return 'U'
  return username.charAt(0).toUpperCase()
}

// 格式化日期
const formatDate = (dateString) => {
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
    const result = await createComment(
      { 
        content: replyContent.value.trim(),
        parent_id: props.comment.id
      },
      props.articleId
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
</style>