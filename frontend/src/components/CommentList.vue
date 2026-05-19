<template>
  <div class="comment-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-comments">
      <div class="spinner"></div>
      <p class="text">加载评论中...</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-comments">
      <p class="message">{{ error }}</p>
      <button class="retry-btn" @click="loadComments">
        重新加载
      </button>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="!comments || comments.length === 0" class="empty-state">
      <div class="icon">💬</div>
      <p class="message">暂无评论，快来发表您的观点吧！</p>
    </div>
    
    <!-- 评论列表 -->
    <div v-else>
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :article-id="articleId"
        @comment-liked="handleCommentLiked"
        @comment-replied="handleCommentReplied"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CommentItem from './CommentItem.vue'
import { getCommentsByArticle as getCommentsApi } from '@/services/commentService'

const props = defineProps({
  articleId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['comments-loaded'])

const comments = ref([])
const loading = ref(false)
const error = ref(null)

const loadComments = async () => {
  loading.value = true
  error.value = null
  
  try {
    const result = await getCommentsApi(props.articleId)
    
    if (result.success) {
      // 调试：输出原始数据
      console.log('原始API响应:', result)
      console.log('扁平评论列表:', result.data.items)
      
      // 将扁平列表转换为嵌套树结构
      const flatComments = result.data.items || []
      const nestedComments = buildCommentTree(flatComments)
      
      // 调试：输出转换后的数据
      console.log('转换后的嵌套评论:', nestedComments)
      
      comments.value = nestedComments
      emit('comments-loaded', result.data.total)
    } else {
      error.value = result.message || '加载评论失败，请稍后重试'
      console.log('API调用失败:', result)
    }
  } catch (err) {
    console.error('Load comments error:', err)
    error.value = '网络错误，请检查网络连接后重试'
  } finally {
    loading.value = false
  }
}

// 将扁平评论列表转换为嵌套树结构
const buildCommentTree = (flatComments) => {
  if (!Array.isArray(flatComments) || flatComments.length === 0) {
    return []
  }
  
  // 创建ID到评论对象的映射
  const commentMap = new Map()
  flatComments.forEach(comment => {
    commentMap.set(comment.id, {
      ...comment,
      replies: [] // 初始化回复数组
    })
  })
  
  const rootComments = []
  
  // 遍历所有评论，构建父子关系
  flatComments.forEach(comment => {
    const commentWithReplies = commentMap.get(comment.id)
    
    if (comment.parentId) {
      // 这是一个回复评论
      const parent = commentMap.get(comment.parentId)
      if (parent) {
        parent.replies.push(commentWithReplies)
      } else {
        // 父评论不存在，作为顶级评论处理（异常情况）
        rootComments.push(commentWithReplies)
      }
    } else {
      // 这是一个顶级评论
      rootComments.push(commentWithReplies)
    }
  })
  
  // 安全的日期解析函数
  const parseDate = (dateValue) => {
    if (dateValue instanceof Date) {
      return dateValue.getTime()
    }
    if (typeof dateValue === 'string') {
      return new Date(dateValue).getTime()
    }
    return 0 // 默认值
  }
  
  // 按时间倒序排列顶级评论（最新的在前面）
  rootComments.sort((a, b) => parseDate(b.createdAt) - parseDate(a.createdAt))
  
  // 对每个顶级评论的回复也按时间倒序排列
  const sortReplies = (comments) => {
    comments.forEach(comment => {
      if (comment.replies && comment.replies.length > 0) {
        comment.replies.sort((a, b) => parseDate(b.createdAt) - parseDate(a.createdAt))
        sortReplies(comment.replies) // 递归排序嵌套回复
      }
    })
  }
  
  sortReplies(rootComments)
  
  return rootComments
}

const handleCommentLiked = (updatedComment) => {
  // 更新本地评论列表中的对应评论
  const updateCommentInList = (commentList, commentId, updatedData) => {
    for (let i = 0; i < commentList.length; i++) {
      if (commentList[i].id === commentId) {
        commentList[i].is_liked = updatedData.isLiked
        commentList[i].like_count = updatedData.likeCount
        return true
      }
      
      // 递归更新嵌套回复
      if (commentList[i].replies && commentList[i].replies.length > 0) {
        if (updateCommentInList(commentList[i].replies, commentId, updatedData)) {
          return true
        }
      }
    }
    return false
  }
  
  updateCommentInList(comments.value, updatedComment.id, updatedComment)
}

const handleCommentReplied = (newComment) => {
  // 将新回复添加到对应的父评论下
  const addReplyToParent = (commentList, parentId, reply) => {
    for (let i = 0; i < commentList.length; i++) {
      if (commentList[i].id === parentId) {
        if (!commentList[i].replies) {
          commentList[i].replies = []
        }
        commentList[i].replies.push(reply)
        return true
      }
      
      // 递归查找嵌套回复
      if (commentList[i].replies && commentList[i].replies.length > 0) {
        if (addReplyToParent(commentList[i].replies, parentId, reply)) {
          return true
        }
      }
    }
    return false
  }
  
  // 如果是顶级评论（没有parent_id），添加到列表顶部
  if (!newComment.parentId) {
    comments.value.unshift(newComment)
  } else {
    // 否则找到父评论并添加回复
    addReplyToParent(comments.value, newComment.parentId, newComment)
  }
  
  // 触发事件通知父组件评论数量变化
  emit('comments-loaded', comments.value.length)
}

onMounted(() => {
  loadComments()
})

// 提供刷新方法给父组件调用
defineExpose({
  refreshComments: loadComments
})
</script>

<style scoped lang="scss">
@use '@/assets/styles/components/comment';
</style>