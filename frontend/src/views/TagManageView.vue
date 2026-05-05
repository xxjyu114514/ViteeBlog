<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <div class="container-narrow">
      <div class="flex-between mb-30">
        <h1 class="title-large">标签管理</h1>
        <button 
          class="btn-primary" 
          @click="openModalForCreate"
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
                @click="openModalForEdit(tag)"
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
        <button class="btn-primary mt-20" @click="openModalForCreate">立即创建第一个标签</button>
      </div>
    </div>

    <!-- 创建/编辑模态框 -->
    <div v-if="isModalOpen" class="modal-overlay" @click="closeModal">
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
            @click="handleCreateOrUpdateTag"
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
import { useRouter } from 'vue-router'
import { useMetaAPI } from '@/composables/useMetaAPI'

const router = useRouter()
const {
  getTags,
  createTag,
  updateTag,
  deleteTag
} = useMetaAPI()

const loading = ref(false)
const tags = ref([])
const creating = ref(false)
const updatingId = ref(null)
const deletingId = ref(null)

// 获取标签列表
const fetchTags = async () => {
  loading.value = true
  try {
    const result = await getTags()
    if (result.success) {
      tags.value = result.data || []
    } else {
      alert(result.message || '获取标签列表失败')
    }
  } catch (error) {
    console.error('获取标签列表异常:', error)
    alert('获取标签列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 打开模态框（用于创建或更新）
const tagName = ref('')
const editingTag = ref(null)
const isModalOpen = ref(false)

const openModalForCreate = () => {
  tagName.value = ''
  editingTag.value = null
  isModalOpen.value = true
}

const openModalForEdit = (tag) => {
  tagName.value = tag.name
  editingTag.value = tag
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  tagName.value = ''
  editingTag.value = null
}

// 处理创建或更新
const handleCreateOrUpdateTag = async () => {
  if (!tagName.value.trim()) {
    alert('请输入标签名称')
    return
  }

  if (editingTag.value) {
    // 更新标签
    updatingId.value = editingTag.value.id
    try {
      const result = await updateTag(editingTag.value.id, tagName.value.trim())
      if (result.success) {
        await fetchTags()
        closeModal()
      } else {
        alert(result.message || '更新标签失败')
      }
    } catch (error) {
      console.error('更新标签异常:', error)
      alert('更新标签失败，请稍后重试')
    } finally {
      updatingId.value = null
    }
  } else {
    // 创建标签
    creating.value = true
    try {
      const result = await createTag(tagName.value.trim())
      if (result.success) {
        await fetchTags()
        closeModal()
      } else {
        alert(result.message || '创建标签失败')
      }
    } catch (error) {
      console.error('创建标签异常:', error)
      alert('创建标签失败，请稍后重试')
    } finally {
      creating.value = false
    }
  }
}

// 处理删除
const handleDelete = async (tagId) => {
  if (!confirm('确定要删除此标签吗？删除后关联的文章将不再有此标签！')) return
  
  deletingId.value = tagId
  try {
    const result = await deleteTag(tagId)
    if (result.success) {
      await fetchTags()
    } else {
      alert(result.message || '删除标签失败')
    }
  } catch (error) {
    console.error('删除标签异常:', error)
    alert('删除标签失败，请稍后重试')
  } finally {
    deletingId.value = null
  }
}

// 初始化
onMounted(() => {
  fetchTags()
})

// 返回上一页
const handleBack = () => {
  router.go(-1)
}
</script>

<style scoped>

</style>