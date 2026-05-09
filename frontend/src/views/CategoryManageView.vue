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
import { useMetaAPI } from '@/composables/useMetaAPI'

const router = useRouter()
const userStore = useUserStore()
const {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory
} = useMetaAPI()

const categories = ref([])
const loading = ref(false)
const editingCategory = ref(null)
const categoryName = ref('')
const creating = ref(false)
const updatingId = ref(null)
const deletingId = ref(null)
const showModal = ref(false)

// 获取分类列表
const fetchCategories = async () => {
  loading.value = true
  try {
    const result = await getCategories()
    if (result.success) {
      categories.value = result.data || []
    } else {
      alert(result.message || '获取分类列表失败')
    }
  } catch (error) {
    console.error('获取分类列表异常:', error)
    alert('获取分类列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 显示创建模态框
const showCreateModal = () => {
  editingCategory.value = null
  categoryName.value = ''
  showModal.value = true
}

// 显示编辑模态框
const showEditModal = (category) => {
  editingCategory.value = { ...category }
  categoryName.value = category.name
  showModal.value = true
}

// 关闭模态框
const closeModal = () => {
  showModal.value = false
  editingCategory.value = null
  categoryName.value = ''
}

// 返回上一页
const handleBack = () => {
  router.go(-1)
}

// 创建分类
const createCategoryHandler = async () => {
  if (!categoryName.value.trim()) {
    alert('分类名称不能为空')
    return
  }
  
  creating.value = true
  try {
    const result = await createCategory(categoryName.value.trim())
    if (result.success) {
      await fetchCategories()
      closeModal()
    } else {
      alert(result.message || '创建分类失败')
    }
  } catch (error) {
    console.error('创建分类异常:', error)
    alert('创建分类失败，请稍后重试')
  } finally {
    creating.value = false
  }
}

// 更新分类
const updateCategoryHandler = async () => {
  if (!editingCategory.value || !categoryName.value.trim()) {
    alert('分类信息不完整')
    return
  }
  
  updatingId.value = editingCategory.value.id
  try {
    const result = await updateCategory(editingCategory.value.id, categoryName.value.trim())
    if (result.success) {
      await fetchCategories()
      closeModal()
    } else {
      alert(result.message || '更新分类失败')
    }
  } catch (error) {
    console.error('更新分类异常:', error)
    alert('更新分类失败，请稍后重试')
  } finally {
    updatingId.value = null
  }
}

// 删除分类
const deleteCategoryHandler = async (categoryId) => {
  if (!confirm('确定要删除这个分类吗？这将影响使用该分类的所有文章。')) {
    return
  }
  
  deletingId.value = categoryId
  try {
    const result = await deleteCategory(categoryId)
    if (result.success) {
      await fetchCategories()
    } else {
      alert(result.message || '删除分类失败')
    }
  } catch (error) {
    console.error('删除分类异常:', error)
    alert('删除分类失败，请稍后重试')
  } finally {
    deletingId.value = null
  }
}

// 处理表单提交
const handleSubmit = () => {
  if (editingCategory.value) {
    updateCategoryHandler()
  } else {
    createCategoryHandler()
  }
}

// 处理删除按钮点击
const handleDelete = (categoryId) => {
  deleteCategoryHandler(categoryId)
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>

</style>