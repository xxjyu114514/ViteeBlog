<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <div class="container-narrow">
      <div class="flex-between mb-30">
        <h1 class="title-large">分类管理</h1>
        <button 
          class="btn-primary" 
          @click="showCreateModal"
          :disabled="creating"
        >
          {{ creating ? '创建中...' : '新建分类' }}
        </button>
      </div>

      <!-- 分类列表 -->
      <div v-if="categories.length > 0" class="category-list">
        <div 
          v-for="category in categories" 
          :key="category.id" 
          class="category-item card card-hover"
        >
          <div class="flex-between">
            <div class="category-info">
              <h3 class="category-name">{{ category.name }}</h3>
              <div class="meta-text">
                <span>ID: {{ category.id }}</span>
              </div>
            </div>
            <div class="category-actions">
              <button 
                class="btn-action btn-edit"
                @click="showEditModal(category)"
                :disabled="updatingId === category.id"
              >
                {{ updatingId === category.id ? '保存中...' : '编辑' }}
              </button>
              <button 
                class="btn-action btn-delete"
                @click="handleDelete(category.id)"
                :disabled="deletingId === category.id"
              >
                {{ deletingId === category.id ? '删除中...' : '删除' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载分类列表中...</p>
      </div>

      <div v-else class="empty-state">
        <p>暂无分类</p>
        <button class="btn-primary mt-20" @click="showCreateModal">立即创建第一个分类</button>
      </div>
    </div>

    <!-- 创建/编辑模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">{{ editingCategory ? '编辑分类' : '新建分类' }}</h3>
        <div class="form-group">
          <label>分类名称</label>
          <input 
            v-model="categoryName" 
            type="text" 
            class="input-field" 
            placeholder="请输入分类名称"
            maxlength="50"
            :disabled="creating || updatingId"
          >
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeModal">取消</button>
          <button 
            class="btn-primary" 
            @click="handleSubmit"
            :disabled="!categoryName.trim() || creating || updatingId"
          >
            {{ creating || updatingId ? '处理中...' : (editingCategory ? '保存' : '创建') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 状态管理
const loading = ref(true)
const categories = ref([])
const showModal = ref(false)
const categoryName = ref('')
const editingCategory = ref(null)
const creating = ref(false)
const updatingId = ref(null)
const deletingId = ref(null)

// 获取分类列表
const fetchCategories = async () => {
  loading.value = true
  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/article/categories', {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      categories.value = data.items || []
    } else {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || '获取分类列表失败'
      alert(errorMessage)
    }
  } catch (error) {
    console.error('获取分类列表异常:', error)
    alert('网络错误，请稍后重试')
  }
  loading.value = false
}

// 显示创建模态框
const showCreateModal = () => {
  editingCategory.value = null
  categoryName.value = ''
  showModal.value = true
}

// 显示编辑模态框
const showEditModal = (category) => {
  editingCategory.value = category
  categoryName.value = category.name
  showModal.value = true
}

// 关闭模态框
const closeModal = () => {
  showModal.value = false
  editingCategory.value = null
  categoryName.value = ''
}

// 处理提交（创建或更新）
const handleSubmit = async () => {
  if (!categoryName.value.trim()) return
  
  if (editingCategory.value) {
    // 更新分类
    updatingId.value = editingCategory.value.id
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/article/categories/${editingCategory.value.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${userStore.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: categoryName.value.trim() })
      })
      
      if (response.ok) {
        await fetchCategories()
        closeModal()
      } else {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || '更新分类失败'
        alert(errorMessage)
      }
    } catch (error) {
      console.error('更新分类异常:', error)
      alert('网络错误，请稍后重试')
    }
    updatingId.value = null
  } else {
    // 创建分类
    creating.value = true
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/article/categories', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userStore.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: categoryName.value.trim() })
      })
      
      if (response.ok) {
        await fetchCategories()
        closeModal()
      } else {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || '创建分类失败'
        alert(errorMessage)
      }
    } catch (error) {
      console.error('创建分类异常:', error)
      alert('网络错误，请稍后重试')
    }
    creating.value = false
  }
}

// 处理删除
const handleDelete = async (categoryId) => {
  if (!confirm('确定要删除此分类吗？删除后关联的文章将不再有分类！')) return
  
  deletingId.value = categoryId
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/v1/article/categories/${categoryId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    if (response.ok) {
      await fetchCategories()
    } else {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || '删除分类失败'
      alert(errorMessage)
    }
  } catch (error) {
    console.error('删除分类异常:', error)
    alert('网络错误，请稍后重试')
  }
  deletingId.value = null
}

// 返回上一页
const handleBack = () => {
  router.go(-1)
}

// 初始化
onMounted(async () => {
  // 检查是否为管理员
  if (!userStore.isAdmin) {
    alert('权限不足：此功能仅限管理员使用')
    router.go(-1)
    return
  }
  
  await fetchCategories()
})
</script>

<style scoped>

</style>