<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div class="editor-container-wide">
      <div class="editor-header flex-between">
        <h1 class="title-large">{{ editingArticle ? '编辑文章' : '新建文章' }}</h1>
        <div class="editor-actions">
          <button class="btn-secondary" @click="goBack" :disabled="saving">返回</button>
          <button class="btn-primary" @click="handleSave" :disabled="saving || !canSave">
            {{ saving ? '保存中...' : '保存草稿' }}
          </button>
          <button 
            v-if="editingArticle && editingArticle.status === 'draft'"
            class="btn-publish" 
            @click="handlePublish"
            :disabled="saving || !canSave"
          >
            {{ publishing ? '发布中...' : '发布文章' }}
          </button>
        </div>
      </div>

      <div v-if="statusMessage" :class="['message-banner', isError ? 'error' : 'success']">
        {{ statusMessage }}
      </div>

      <div class="editor-form">
        <div class="form-group">
          <label>标题</label>
          <input 
            v-model="currentArticle.title" 
            type="text" 
            class="input-field"
            placeholder="请输入文章标题"
            :disabled="saving"
          >
        </div>
        
        <div class="form-row">
          <div class="form-group flex-1">
            <label>分类</label>
            <select 
              v-model="currentArticle.category_id" 
              class="input-field select-field"
              :disabled="saving || loadingCategories"
            >
              <option value="">请选择分类</option>
              <option 
                v-for="category in categories" 
                :key="category.id" 
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>
            <div v-if="loadingCategories" class="loading-text">加载分类中...</div>
          </div>
          <div class="form-group flex-2">
            <label>标签</label>
            <div class="tag-selector">
              <div 
                v-for="tag in selectedTags" 
                :key="tag.id" 
                class="selected-tag"
              >
                {{ tag.name }}
                <span class="remove-tag" @click.stop="removeTag(tag.id)">×</span>
              </div>
              <select 
                v-model="newTagId" 
                class="tag-select input-field"
                :disabled="saving || loadingTags"
                @change="addTag"
              >
                <option value="">+ 选择标签</option>
                <option 
                  v-for="tag in availableTags" 
                  :key="tag.id" 
                  :value="tag.id"
                  :disabled="selectedTags.some(t => t.id === tag.id)"
                >
                  {{ tag.name }}
                </option>
              </select>
            </div>
            <div v-if="loadingTags" class="loading-text">加载标签中...</div>
          </div>
        </div>

        <div class="form-group">
          <label>内容 (支持拖拽/粘贴图片上传)</label>
          <div v-show="!editorLoadError" id="vditor-editor"></div>
          
          <textarea 
            v-if="editorLoadError" 
            v-model="currentArticle.content" 
            class="fallback-textarea"
            placeholder="高级编辑器加载失败，您可以使用普通文本模式编写..."
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useArticleAPI } from '@/composables/useArticleAPI'
import Vditor from 'vditor'
import 'vditor/dist/index.css'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { autoSaveArticle, publishArticle, getArticleDetail } = useArticleAPI()

// 后端基础配置
const BACKEND_URL = 'http://localhost:8000'

// 分类和标签相关状态
const categories = ref([])
const tags = ref([])
const selectedTags = ref([])
const newTagId = ref('')
const loadingCategories = ref(false)
const loadingTags = ref(false)

// 响应式状态
const currentArticle = ref({ title: '', content: '', category_id: null, tag_ids: [] })
const saving = ref(false)
const publishing = ref(false)
const statusMessage = ref('')
const isError = ref(false)
const editingArticle = ref(null)
const editorLoadError = ref(false)
let vditorInstance = null

const canSave = computed(() => {
  return currentArticle.value.title.trim() !== '' && currentArticle.value.content.trim() !== ''
})

// 计算属性：可用的标签（未被选中的）
const availableTags = computed(() => {
  return tags.value.filter(tag => !selectedTags.value.some(selected => selected.id === tag.id))
})

// 获取分类列表
const fetchCategories = async () => {
  loadingCategories.value = true
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/article/categories`, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      categories.value = data.items || []
    } else {
      console.error('获取分类列表失败:', await response.json().catch(() => ({})))
    }
  } catch (error) {
    console.error('获取分类列表异常:', error)
  }
  loadingCategories.value = false
}

// 获取标签列表
const fetchTags = async () => {
  loadingTags.value = true
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/article/tags`, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      tags.value = data.items || []
    } else {
      console.error('获取标签列表失败:', await response.json().catch(() => ({})))
    }
  } catch (error) {
    console.error('获取标签列表异常:', error)
  }
  loadingTags.value = false
}

// 添加标签
const addTag = () => {
  if (!newTagId.value) return
  
  const tagToAdd = tags.value.find(tag => tag.id === parseInt(newTagId.value))
  if (tagToAdd && !selectedTags.value.some(tag => tag.id === tagToAdd.id)) {
    selectedTags.value.push(tagToAdd)
  }
  newTagId.value = ''
}

// 移除标签
const removeTag = (tagId) => {
  selectedTags.value = selectedTags.value.filter(tag => tag.id !== tagId)
}

// 监听 selectedTags 变化，更新 currentArticle.tag_ids
watch(selectedTags, (newTags) => {
  currentArticle.value.tag_ids = newTags.map(tag => tag.id)
}, { deep: true })

/**
 * 初始化编辑器
 */
const initVditor = (initialContent) => {
  if (vditorInstance) {
    vditorInstance.destroy()
  }

  vditorInstance = new Vditor('vditor-editor', {
    mode: 'ir', // 所见即所得模式
    height: 600,
    placeholder: '从这里开始创作...',
    value: initialContent || '',
    cache: { enable: false },
    toolbarConfig: { pin: true },
    // 注意：如果你的网络环境无法访问官方 CDN，可以重新开启并配置本地 cdn: '/vditor'
    
    upload: {
      url: `${BACKEND_URL}/api/v1/article/upload-image`,
      fieldName: 'file',
      max: 10 * 1024 * 1024,
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      },
      // 适配后端响应格式
      format: (files, responseText) => {
        try {
          const res = JSON.parse(responseText)
          const filename = res.filename || files[0].name
          return JSON.stringify({
            code: 0,
            msg: "",
            data: {
              errFiles: [],
              succMap: {
                [filename]: `${BACKEND_URL}${res.url}`
              }
            }
          })
        } catch (e) {
          return JSON.stringify({ code: 1, msg: "接口解析失败", data: { errFiles: [files[0].name] } })
        }
      },
      error: (msg) => {
        showStatus('图片上传失败: ' + msg, true)
      }
    },
    after: () => {
      editorLoadError.value = false
    },
    input: (val) => {
      currentArticle.value.content = val
    }
  })
}

/**
 * 消息提醒
 */
const showStatus = (msg, error = false) => {
  statusMessage.value = msg
  isError.value = error
  setTimeout(() => { statusMessage.value = '' }, 3000)
}

/**
 * 加载文章数据
 */
const loadArticleData = async () => {
  const articleId = route.params.id
  
  // 先加载分类和标签
  await Promise.all([
    fetchCategories(),
    fetchTags()
  ])

  if (!articleId) {
    // 新建模式
    await nextTick()
    initVditor('')
    return
  }

  // 编辑模式
  const result = await getArticleDetail(articleId)
  if (result.success) {
    const info = result.data.info
    editingArticle.value = info
    currentArticle.value = {
      title: info.title,
      content: result.data.content || '',
      category_id: info.category?.id || null,
      tag_ids: info.tags?.map(t => t.id) || []
    }
    
    // 设置已选择的标签
    if (info.tags) {
      selectedTags.value = info.tags.map(tag => ({
        id: tag.id,
        name: tag.name
      }))
    }
    
    await nextTick()
    initVditor(currentArticle.value.content)
  } else {
    showStatus('获取文章失败: ' + result.message, true)
    setTimeout(() => router.push('/personal'), 1500)
  }
}

/**
 * 保存逻辑
 */
const handleSave = async () => {
  if (!canSave.value) return
  
  saving.value = true
  
  const payload = {
    ...currentArticle.value,
    article_id: editingArticle.value?.id || null
  }

  const result = await autoSaveArticle(payload)
  if (result.success) {
    if (!editingArticle.value) {
      editingArticle.value = { id: result.data.article_id, status: 'draft' }
    }
    showStatus('已保存到草稿箱')
  } else {
    showStatus(result.message, true)
  }
  saving.value = false
}

const handlePublish = async () => {
  if (!editingArticle.value || publishing.value) return
  
  publishing.value = true
  const result = await publishArticle(editingArticle.value.id)
  if (result.success) {
    showStatus('发布成功！即将跳转...')
    setTimeout(() => router.push('/posts'), 1000)
  } else {
    showStatus(result.message, true)
  }
  publishing.value = false
}

const goBack = () => router.push('/personal')

onMounted(loadArticleData)

onUnmounted(() => {
  if (vditorInstance) {
    vditorInstance.destroy()
  }
})
</script>

<style scoped>
.editor-container-wide {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

#vditor-editor {
  width: 100%;
  min-height: 600px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

.editor-form {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.fallback-textarea {
  width: 100%;
  height: 600px;
  padding: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.message-banner {
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.message-banner.success {
  background-color: #f0fdf4;
  color: #166534;
  border-left: 4px solid #22c55e;
}

.message-banner.error {
  background-color: #fef2f2;
  color: #991b1b;
  border-left: 4px solid #ef4444;
}

.flex-row { display: flex; align-items: flex-end; }
.flex-1 { flex: 1; }
.flex-2 { flex: 2; }
.gap-20 { gap: 20px; }
.mb-20 { margin-bottom: 20px; }

/* 按钮基础样式（按需在全局 CSS 定义） */
.btn-publish {
  background-color: #8b5cf6;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
}
.btn-publish:hover { background-color: #7c3aed; }
.btn-publish:disabled { background-color: #c4b5fd; cursor: not-allowed; }

.select-field {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.select-field:focus {
  outline: none;
  border-color: #3b82f6;
}

.loading-text {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

/* 标签选择器 */
.tag-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  min-height: 40px;
  background: white;
}

.tag-select {
  flex: 1;
  min-width: 120px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.selected-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #e3f2fd;
  border: 1px solid #bbdefb;
  border-radius: 12px;
  font-size: 12px;
  color: #1976d2;
}

.remove-tag {
  cursor: pointer;
  font-weight: bold;
  color: #f44336;
}

.remove-tag:hover {
  color: #d32f2f;
}
</style>