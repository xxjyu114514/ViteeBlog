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
.back-button {
  position: fixed;
  top: 100px;
  left: 20px;
  z-index: 1000;
  padding: 8px 16px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: #374151;
  text-decoration: none;
  transition: all 0.2s;
}

.back-button:hover {
  background: #f3f4f6;
  transform: translateX(-2px);
}

.message-header {
  text-align: center;
  margin: 80px 0 40px 0;
}

.message-header h1 {
  font-size: 2.5rem;
  color: #1f2937;
  margin-bottom: 16px;
}

.message-header p {
  color: #6b7280;
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.message-form-section {
  max-width: 700px;
  margin: 0 auto 60px auto;
  padding: 0 20px;
}

.message-form {
  background: white;
  padding: 30px;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #1f2937;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #2563eb;
}

.submit-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.message-list-section {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px 80px;
}

.message-list-section h2 {
  font-size: 1.8rem;
  color: #1f2937;
  margin-bottom: 30px;
  text-align: center;
}

.no-messages {
  text-align: center;
  color: #6b7280;
  font-size: 1.1rem;
  padding: 40px;
  background: #f9fafb;
  border-radius: 16px;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-item {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #3b82f6;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.message-author {
  font-weight: 700;
  color: #1f2937;
  font-size: 1.1rem;
}

.message-time {
  color: #9ca3af;
  font-size: 0.9rem;
}

.message-content {
  color: #374151;
  line-height: 1.6;
  font-size: 1rem;
}

.message-reply {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f3f4f6;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.reply-author {
  font-weight: 600;
  color: #3b82f6;
  font-size: 1rem;
}

.reply-time {
  color: #9ca3af;
  font-size: 0.85rem;
}

.reply-content {
  color: #4b5563;
  line-height: 1.6;
  font-style: italic;
}
</style>