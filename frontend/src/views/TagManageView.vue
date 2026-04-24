<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div class="container-narrow">
      <div class="flex-between mb-30">
        <h1 class="title-large">标签管理</h1>
        <button 
          class="btn-primary" 
          @click="showCreateModal"
          :disabled="creating"
        >
          {{ creating ? '创建中...' : '新建标签' }}
        </button>
      </div>

      <!-- 标签列表 -->
      <div v-if="tags.length > 0" class="tag-list">
        <div 
          v-for="tag in tags" 
          :key="tag.id" 
          class="tag-item card card-hover"
        >
          <div class="flex-between">
            <div class="tag-info">
              <h3 class="tag-name">{{ tag.name }}</h3>
              <div class="meta-text">
                <span>ID: {{ tag.id }}</span>
              </div>
            </div>
            <div class="tag-actions">
              <button 
                class="btn-action btn-edit"
                @click="showEditModal(tag)"
                :disabled="updatingId === tag.id"
              >
                {{ updatingId === tag.id ? '保存中...' : '编辑' }}
              </button>
              <button 
                class="btn-action btn-delete"
                @click="handleDelete(tag.id)"
                :disabled="deletingId === tag.id"
              >
                {{ deletingId === tag.id ? '删除中...' : '删除' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载标签列表中...</p>
      </div>

      <div v-else class="empty-state">
        <p>暂无标签</p>
        <button class="btn-primary mt-20" @click="showCreateModal">立即创建第一个标签</button>
      </div>
    </div>

    <!-- 创建/编辑模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">{{ editingTag ? '编辑标签' : '新建标签' }}</h3>
        <div class="form-group">
          <label>标签名称</label>
          <input 
            v-model="tagName" 
            type="text" 
            class="input-field" 
            placeholder="请输入标签名称"
            maxlength="50"
            :disabled="creating || updatingId"
          >
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeModal">取消</button>
          <button 
            class="btn-primary" 
            @click="handleSubmit"
            :disabled="!tagName.trim() || creating || updatingId"
          >
            {{ creating || updatingId ? '处理中...' : (editingTag ? '保存' : '创建') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 状态管理
const loading = ref(true)
const tags = ref([])
const showModal = ref(false)
const tagName = ref('')
const editingTag = ref(null)
const creating = ref(false)
const updatingId = ref(null)
const deletingId = ref(null)

// 获取标签列表
const fetchTags = async () => {
  loading.value = true
  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/article/tags', {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      tags.value = data.items || []
    } else {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || '获取标签列表失败'
      alert(errorMessage)
    }
  } catch (error) {
    console.error('获取标签列表异常:', error)
    alert('网络错误，请稍后重试')
  }
  loading.value = false
}

// 显示创建模态框
const showCreateModal = () => {
  editingTag.value = null
  tagName.value = ''
  showModal.value = true
}

// 显示编辑模态框
const showEditModal = (tag) => {
  editingTag.value = tag
  tagName.value = tag.name
  showModal.value = true
}

// 关闭模态框
const closeModal = () => {
  showModal.value = false
  editingTag.value = null
  tagName.value = ''
}

// 处理提交（创建或更新）
const handleSubmit = async () => {
  if (!tagName.value.trim()) return
  
  if (editingTag.value) {
    // 更新标签
    updatingId.value = editingTag.value.id
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/article/tags/${editingTag.value.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${userStore.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: tagName.value.trim() })
      })
      
      if (response.ok) {
        await fetchTags()
        closeModal()
      } else {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || '更新标签失败'
        alert(errorMessage)
      }
    } catch (error) {
      console.error('更新标签异常:', error)
      alert('网络错误，请稍后重试')
    }
    updatingId.value = null
  } else {
    // 创建标签
    creating.value = true
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/article/tags', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userStore.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: tagName.value.trim() })
      })
      
      if (response.ok) {
        await fetchTags()
        closeModal()
      } else {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || '创建标签失败'
        alert(errorMessage)
      }
    } catch (error) {
      console.error('创建标签异常:', error)
      alert('网络错误，请稍后重试')
    }
    creating.value = false
  }
}

// 处理删除
const handleDelete = async (tagId) => {
  if (!confirm('确定要删除此标签吗？删除后关联的文章将不再有此标签！')) return
  
  deletingId.value = tagId
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/v1/article/tags/${tagId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    if (response.ok) {
      await fetchTags()
    } else {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || '删除标签失败'
      alert(errorMessage)
    }
  } catch (error) {
    console.error('删除标签异常:', error)
    alert('网络错误，请稍后重试')
  }
  deletingId.value = null
}

// 初始化
onMounted(async () => {
  // 检查是否为管理员
  if (!userStore.isAdmin) {
    alert('权限不足：此功能仅限管理员使用')
    window.history.back()
    return
  }
  
  await fetchTags()
})
</script>

<style scoped>
.tag-list {
  margin-top: 20px;
}

.tag-item {
  padding: 20px;
  margin-bottom: 15px;
  border-radius: 8px;
}

.tag-info {
  flex: 1;
}

.tag-name {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.meta-text {
  color: #666;
  font-size: 14px;
}

.tag-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-action {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  border: none;
  cursor: pointer;
}

.btn-edit {
  background-color: #8b5cf6;
  color: white;
}

.btn-edit:hover:not(:disabled) {
  background-color: #7c3aed;
}

.btn-edit:disabled {
  background-color: #c4a7ff;
  cursor: not-allowed;
}

.btn-delete {
  background-color: #ef4444;
  color: white;
}

.btn-delete:hover:not(:disabled) {
  background-color: #dc2626;
}

.btn-delete:disabled {
  background-color: #fca5a5;
  cursor: not-allowed;
}

.loading-state {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.mt-20 {
  margin-top: 20px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #333;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.input-field {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.input-field:focus {
  outline: none;
  border-color: #3b82f6;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn-secondary {
  padding: 10px 20px;
  border: 1px solid #ddd;
  background: white;
  color: #333;
  border-radius: 6px;
  cursor: pointer;
  font-SIZE: 14px;
}

.btn-secondary:hover {
  background: #f5f5f5;
}

.btn-primary {
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}
</style>