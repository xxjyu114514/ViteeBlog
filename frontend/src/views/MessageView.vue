<template>
  <div class="page-container">
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <div class="message-header">
      <h1>留言板</h1>
      <p>在这里留下你的想法、问题或建议，我会尽快回复！</p>
    </div>
    
    <!-- 留言表单 -->
    <div class="message-form-section">
      <form @submit.prevent="handleSubmit" class="message-form">
        <div class="form-group">
          <label for="name">昵称 *</label>
          <input 
            id="name" 
            v-model="formData.name" 
            type="text" 
            required 
            placeholder="请输入您的昵称"
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱 *</label>
          <input 
            id="email" 
            v-model="formData.email" 
            type="email" 
            required 
            placeholder="请输入您的邮箱（不会公开）"
          />
        </div>
        
        <div class="form-group">
          <label for="content">留言内容 *</label>
          <textarea 
            id="content" 
            v-model="formData.content" 
            rows="6" 
            required 
            placeholder="写下您想说的话..."
          ></textarea>
        </div>
        
        <button 
          type="submit" 
          :disabled="isSubmitting"
          class="submit-btn"
        >
          {{ isSubmitting ? '提交中...' : '发表留言' }}
        </button>
      </form>
    </div>
    
    <!-- 留言列表 -->
    <div class="message-list-section">
      <h2>最新留言 ({{ messages.length }})</h2>
      
      <div v-if="messages.length === 0" class="no-messages">
        还没有留言，快来抢沙发吧！
      </div>
      
      <div v-else class="messages-container">
        <div 
          v-for="message in messages" 
          :key="message.id" 
          class="message-item"
        >
          <div class="message-header">
            <span class="message-author">{{ message.name }}</span>
            <span class="message-time">{{ formatTime(message.created_at) }}</span>
          </div>
          <div class="message-content">
            {{ message.content }}
          </div>
          
          <!-- 回复显示（如果有） -->
          <div v-if="message.reply" class="message-reply">
            <div class="reply-header">
              <span class="reply-author">博主回复：</span>
              <span class="reply-time">{{ formatTime(message.reply.created_at) }}</span>
            </div>
            <div class="reply-content">
              {{ message.reply.content }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePageTransition } from '@/composables/usePageTransition'

const router = useRouter()
const { isAnimating } = usePageTransition()

// 表单数据
const formData = ref({
  name: '',
  email: '',
  content: ''
})

const isSubmitting = ref(false)

// 模拟留言数据
const messages = ref([
  {
    id: 1,
    name: '技术爱好者',
    content: '博客内容很实用，期待更多分享！',
    created_at: '2026-04-15T10:30:00Z',
    reply: {
      content: '谢谢支持！我会继续努力分享优质内容。',
      created_at: '2026-04-15T14:20:00Z'
    }
  },
  {
    id: 2,
    name: '前端小白',
    content: '请问Vue 3的学习路线有什么建议吗？',
    created_at: '2026-04-10T09:15:00Z',
    reply: null
  },
  {
    id: 3,
    name: '后端工程师',
    content: 'FastAPI确实很强大，和Vue 3搭配使用体验很棒！',
    created_at: '2026-04-05T16:45:00Z',
    reply: {
      content: '完全同意！前后端分离架构让开发效率大大提升。',
      created_at: '2026-04-05T18:30:00Z'
    }
  }
])

const handleBack = () => {
  if (isAnimating.value) return
  router.push('/message-immersive')
}

const handleSubmit = async () => {
  if (isSubmitting.value) return
  
  isSubmitting.value = true
  
  try {
    // 这里应该调用API提交留言
    console.log('提交留言:', formData.value)
    
    // 模拟成功提交
    setTimeout(() => {
      alert('留言提交成功！')
      formData.value = { name: '', email: '', content: '' }
      isSubmitting.value = false
    }, 1000)
  } catch (error) {
    console.error('提交失败:', error)
    alert('提交失败，请稍后重试')
    isSubmitting.value = false
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>

</style>