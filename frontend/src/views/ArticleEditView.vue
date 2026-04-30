<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div class="editor-container-wide">
      <div class="editor-header flex-between">
        <h1 class="title-large">{{ editingArticle ? '编辑文章' : '新建文章' }}</h1>
        <div class="editor-actions">
          <button class="btn-secondary" @click="goBack" :disabled="saving">返回</button>
          <button 
            class="btn-primary" 
            @click="handleSave" 
            :disabled="saving || !canSave || isPending"
          >
            {{ saving ? '保存中...' : '保存草稿' }}
          </button>
          <button 
            v-if="editingArticle && editingArticle.status === 'draft'"
            class="btn-publish" 
            @click="handlePublish"
            :disabled="saving || !canSave || isPending"
          >
            {{ publishing ? '发布中...' : '发布文章' }}
          </button>
          <button 
            v-if="editingArticle && editingArticle.status === 'pending'"
            class="btn-secondary"
            @click="handleWithdraw"
            :disabled="withdrawing"
          >
            {{ withdrawing ? '撤回中...' : '撤回发布' }}
          </button>
        </div>
      </div>

      <div v-if="statusMessage" :class="['message-banner', isError ? 'error' : 'success']">
        {{ statusMessage }}
      </div>

      <!-- 待审核状态提示 -->
      <div v-if="isPending" class="pending-notice">
        <div class="notice-content">
          <span class="notice-icon">⚠️</span>
          <span>文章正在审核中，如需修改，请先撤回为草稿。</span>
        </div>
      </div>

      <div class="editor-form">
        <div class="form-group">
          <label>标题</label>
          <input 
            v-model="currentArticle.title" 
            type="text" 
            class="input-field"
            placeholder="请输入文章标题"
            :disabled="saving || isPending"
          >
        </div>
        
        <div class="form-group">
          <label>摘要</label>
          <textarea 
            v-model="currentArticle.summary" 
            class="input-field"
            placeholder="请输入文章摘要（可选，用于列表预览）"
            :disabled="saving || isPending"
            rows="3"
          ></textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group flex-1">
            <label>分类</label>
            <select 
              v-model="currentArticle.category_id" 
              class="input-field select-field"
              :disabled="saving || loadingCategories || isPending"
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
                :class="{ 'disabled': isPending }"
              >
                {{ tag.name }}
                <span 
                  v-if="!isPending" 
                  class="remove-tag" 
                  @click.stop="removeTag(tag.id)"
                >×</span>
              </div>
              <select 
                v-model="newTagId" 
                class="tag-select input-field"
                :disabled="saving || loadingTags || isPending"
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
            :disabled="isPending"
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Vditor from 'vditor'
import 'vditor/dist/index.css'
import { useUserStore } from '@/stores/user'
import { buildUrl } from '@/utils/apiUtils'
import { getBaseUrl } from '@/config/apiConfig'
import { useArticleAPI } from '@/composables/useArticleAPI'
import { useMetaAPI } from '@/composables/useMetaAPI'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const { autoSaveArticle, publishArticle, getArticleDetail, withdrawArticle } = useArticleAPI()
const { getCategories, getTags } = useMetaAPI()

// 响应式状态
const currentArticle = ref({ title: '', summary: '', content: '', category_id: null, tag_ids: [] })
const saving = ref(false)
const publishing = ref(false)
const withdrawing = ref(false)
const statusMessage = ref('')
const isError = ref(false)
const editingArticle = ref(null)
const editorLoadError = ref(false)
let vditorInstance = null

// 分类和标签数据
const categories = ref([])
const tags = ref([])
const loadingCategories = ref(true)
const loadingTags = ref(true)

// 新增：标签选择相关状态
const selectedTags = ref([])
const newTagId = ref('')

const canSave = computed(() => {
  return currentArticle.value.title.trim() !== '' && currentArticle.value.content.trim() !== ''
})

// 新增：是否处于待审核状态
const isPending = computed(() => {
  return editingArticle.value?.status === 'pending'
})

// 计算属性：可用的标签（未被选中的）
const availableTags = computed(() => {
  return tags.value.filter(tag => !selectedTags.value.some(selected => selected.id === tag.id))
})

// 标签操作函数
const addTag = () => {
  if (newTagId.value && !selectedTags.value.some(tag => tag.id === parseInt(newTagId.value))) {
    const tagToAdd = tags.value.find(tag => tag.id === parseInt(newTagId.value))
    if (tagToAdd) {
      selectedTags.value.push({ id: tagToAdd.id, name: tagToAdd.name })
      // 注意：这里不再直接操作 selectedTagIds，而是通过 currentArticle.value.tag_ids 同步或者在保存时处理
      // 为了保持简单，我们更新 currentArticle.value.tag_ids 以保持一致性
      if (!currentArticle.value.tag_ids.includes(tagToAdd.id)) {
        currentArticle.value.tag_ids.push(tagToAdd.id)
      }
    }
    newTagId.value = ''
  }
}

const removeTag = (tagId) => {
  selectedTags.value = selectedTags.value.filter(tag => tag.id !== tagId)
  currentArticle.value.tag_ids = currentArticle.value.tag_ids.filter(id => id !== tagId)
}

// 获取分类列表
const fetchCategories = async () => {
  loadingCategories.value = true
  try {
    const result = await getCategories()
    if (result.success) {
      categories.value = result.data || []
    } else {
      console.error('获取分类列表失败:', result.message)
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
    const result = await getTags()
    if (result.success) {
      tags.value = result.data || []
    } else {
      console.error('获取标签列表失败:', result.message)
    }
  } catch (error) {
    console.error('获取标签列表异常:', error)
  }
  loadingTags.value = false
}

/**
 * 初始化编辑器
 */
const initVditor = (initialContent) => {
  if (vditorInstance) {
    vditorInstance.destroy()
  }

  const BACKEND_URL = getBaseUrl()

  vditorInstance = new Vditor('vditor-editor', {
    mode: 'ir', // 所见即所得模式
    height: 600,
    placeholder: '从这里开始创作...',
    value: initialContent || '',
    cache: { enable: false },
    toolbarConfig: { pin: true },
    // 注意：如果你的网络环境无法访问官方 CDN，可以重新开启并配置本地 cdn: '/vditor'
    
    upload: {
      url: buildUrl('/article/upload-image'),
      fieldName: 'file',
      max: 10 * 1024 * 1024,
      // 使用setHeaders函数动态获取token，每次上传前都会调用
      setHeaders: () => {
        const userStore = useUserStore()
        return {
          'Authorization': `Bearer ${userStore.token}`
        }
      },
      // 适配后端响应格式
      format: (files, responseText) => {
        try {
          const res = JSON.parse(responseText)
          const filename = res.filename || files[0].name
          // 修复：静态资源应该使用后端基础URL，而不是前端origin
          // 后端返回的 res.url 是 "/storage/images/xxx.jpg" 格式
          // 获取后端基础URL（不含/api/v1前缀）
          const backendBaseUrl = getBaseUrl().replace('/api/v1', '')
          return JSON.stringify({
            code: 0,
            msg: "",
            data: {
              errFiles: [],
              succMap: {
                [filename]: `${backendBaseUrl}${res.url}`
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
    // 如果是待审核状态，从 content_path 加载内容；否则使用原有逻辑
    let contentToLoad = ''
    if (info.content_path) {
      try {
        const backendBaseUrl = getBaseUrl().replace('/api/v1', '')
        
        // 尝试标准化路径
        let normalizedPath = info.content_path.replace(/\\/g, '/')
        if (!normalizedPath.startsWith('/')) {
          normalizedPath = '/' + normalizedPath
        }
        const normalizedUrl = `${backendBaseUrl}${normalizedPath}`
        
        let contentResponse = await fetch(normalizedUrl)
        if (contentResponse.ok) {
          contentToLoad = await contentResponse.text()
        } else {
          // 尝试原始路径
          const originalUrl = `${backendBaseUrl}/${info.content_path.replace(/^\/+/, '')}`
          contentResponse = await fetch(originalUrl)
          if (contentResponse.ok) {
            contentToLoad = await contentResponse.text()
          } else {
            console.log('⚠️ 编辑页文件加载失败，两种路径都尝试了')
            // 由于数据库没有content字段，只能显示空内容
            contentToLoad = ''
          }
        }
      } catch (err) {
        console.error('加载待审核文章内容失败:', err)
        contentToLoad = ''
      }
    } else {
      contentToLoad = '' // 数据库没有content字段
    }
    
    currentArticle.value = {
      title: info.title,
      content: contentToLoad,
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
  if (!canSave.value || isPending.value) return
  
  // 确保内容不为空
  if (!currentArticle.value.content || currentArticle.value.content.trim() === '') {
    showStatus('文章内容不能为空', true)
    return
  }
  
  saving.value = true
  
  const payload = {
    ...currentArticle.value,
    id: editingArticle.value?.id || null
  }

  const result = await autoSaveArticle(payload)
  if (result.success) {
    if (!editingArticle.value) {
      editingArticle.value = { id: result.data.id, status: 'draft' }
    }
    showStatus('已保存到草稿箱')
  } else {
    showStatus(result.message, true)
  }
  saving.value = false
}

const handlePublish = async () => {
  if (!editingArticle.value || publishing.value || isPending.value) return
  
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

// 撤回发布
const handleWithdraw = async () => {
  if (!editingArticle.value || withdrawing.value || editingArticle.value.status !== 'pending') return
  
  if (!confirm('确定要撤回这篇文章吗？撤回后将回到草稿状态。')) return
  
  withdrawing.value = true
  const result = await withdrawArticle(editingArticle.value.id)
  if (result.success) {
    showStatus('已撤回至草稿状态')
    editingArticle.value.status = 'draft'
  } else {
    showStatus(result.message, true)
  }
  withdrawing.value = false
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
.pending-notice {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
}

.notice-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #856404;
  font-size: 14px;
}

.notice-icon {
  font-size: 16px;
}

.selected-tag.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.selected-tag.disabled .remove-tag {
  display: none;
}
</style>