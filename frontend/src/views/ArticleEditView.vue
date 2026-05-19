<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div class="editor-container-wide">
      <div class="editor-header flex-between">
        <h1 class="title-large">{{ editingArticle ? '编辑文章' : '新建文章' }}</h1>
        <div class="editor-actions">
          <button class="btn-secondary" @click="goBack" :disabled="saving">返回</button>
          <button class="btn-primary" @click="handleSave" :disabled="saving || !canSave || isPending">
            {{ saving ? '保存中...' : '保存草稿' }}
          </button>
          <button v-if="editingArticle && editingArticle.status === 'draft'" class="btn-publish" @click="handlePublish" :disabled="saving || !canSave || isPending">
            {{ publishing ? '发布中...' : '发布文章' }}
          </button>
          <button v-if="editingArticle && editingArticle.status === 'pending'" class="btn-secondary" @click="handleWithdraw" :disabled="withdrawing">
            {{ withdrawing ? '撤回中...' : '撤回发布' }}
          </button>
        </div>
      </div>

      <div v-if="statusMessage" :class="['message-banner', isError ? 'error' : 'success']">
        {{ statusMessage }}
      </div>

      <div v-if="isPending" class="pending-notice">
        <div class="notice-content">
          <span class="notice-icon">⚠️</span>
          <span>文章正在审核中，如需修改，请先撤回为草稿。</span>
        </div>
      </div>

      <div class="editor-form">
        <div class="form-group">
          <label>标题</label>
          <input v-model="currentArticle.title" type="text" class="input-field" placeholder="请输入文章标题" :disabled="saving || isPending">
        </div>
        
        <div class="form-group">
          <label>摘要</label>
          <textarea v-model="currentArticle.summary" class="input-field" placeholder="请输入文章摘要（可选，用于列表预览）" :disabled="saving || isPending" rows="3"></textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group flex-1">
            <label>分类</label>
            <select v-model="currentArticle.category_id" class="input-field select-field" :disabled="saving || loadingCategories || isPending">
              <option value="">请选择分类</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
            </select>
            <div v-if="loadingCategories" class="loading-text">加载分类中...</div>
          </div>
          <div class="form-group flex-2">
            <label>标签</label>
            <div class="tag-selector">
              <div v-for="tag in selectedTags" :key="tag.id" class="selected-tag" :class="{ 'disabled': isPending }">
                {{ tag.name }}
                <span v-if="!isPending" class="remove-tag" @click.stop="removeTag(tag.id)">×</span>
              </div>
              <select v-model="newTagId" class="tag-select input-field" :disabled="saving || loadingTags || isPending" @change="addTag">
                <option value="">+ 选择标签</option>
                <option v-for="tag in availableTags" :key="tag.id" :value="tag.id" :disabled="selectedTags.some(t => t.id === tag.id)">{{ tag.name }}</option>
              </select>
            </div>
            <div v-if="loadingTags" class="loading-text">加载标签中...</div>
          </div>
        </div>

        <div class="form-group">
          <label>内容 (支持拖拽/粘贴图片上传)</label>
          <div v-show="!editorLoadError" id="vditor-editor"></div>
          <textarea v-if="editorLoadError" v-model="currentArticle.content" class="fallback-textarea" placeholder="高级编辑器加载失败，您可以使用普通文本模式编写..." :disabled="isPending"></textarea>
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
import { getArticleDetail, autoSaveArticle, publishArticle, withdrawArticle, loadArticleContent } from '@/services/articleService'
import { getCategories, getTags } from '@/services/metaService'
import { buildUrl } from '@/utils/apiUtils'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const BACKEND_BASE = API_BASE_URL.replace('/api/v1', '')

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const currentArticle = ref({ title: '', summary: '', content: '', category_id: null, tag_ids: [] })
const saving = ref(false)
const publishing = ref(false)
const withdrawing = ref(false)
const statusMessage = ref('')
const isError = ref(false)
const editingArticle = ref(null)
const editorLoadError = ref(false)
let vditorInstance = null

const categories = ref([])
const tags = ref([])
const loadingCategories = ref(true)
const loadingTags = ref(true)

const selectedTags = ref([])
const newTagId = ref('')

const canSave = computed(() => {
  return currentArticle.value.title.trim() !== '' && currentArticle.value.content.trim() !== ''
})

const isPending = computed(() => {
  return editingArticle.value?.status === 'pending'
})

const availableTags = computed(() => {
  return tags.value.filter(tag => !selectedTags.value.some(selected => selected.id === tag.id))
})

const addTag = () => {
  if (newTagId.value && !selectedTags.value.some(tag => tag.id === parseInt(newTagId.value))) {
    const tagToAdd = tags.value.find(tag => tag.id === parseInt(newTagId.value))
    if (tagToAdd) {
      selectedTags.value.push({ id: tagToAdd.id, name: tagToAdd.name })
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

const fetchCategories = async () => {
  loadingCategories.value = true
  try {
    const result = await getCategories()
    if (result.success) categories.value = result.data || []
  } catch (error) {
    console.error('获取分类列表异常:', error)
  }
  loadingCategories.value = false
}

const fetchTags = async () => {
  loadingTags.value = true
  try {
    const result = await getTags()
    if (result.success) tags.value = result.data || []
  } catch (error) {
    console.error('获取标签列表异常:', error)
  }
  loadingTags.value = false
}

const initVditor = (initialContent) => {
  if (vditorInstance) vditorInstance.destroy()

  vditorInstance = new Vditor('vditor-editor', {
    mode: 'ir',
    height: 600,
    placeholder: '从这里开始创作...',
    value: initialContent || '',
    cache: { enable: false },
    toolbarConfig: { pin: true },

    upload: {
      url: API_BASE_URL + buildUrl('/article/upload-image'),
      fieldName: 'file',
      max: 10 * 1024 * 1024,
      setHeaders: () => {
        const store = useUserStore()
        return { 'Authorization': `Bearer ${store.token}` }
      },
      format: (files, responseText) => {
        try {
          const res = JSON.parse(responseText)
          const filename = res.filename || files[0].name
          return JSON.stringify({
            code: 0,
            msg: '',
            data: {
              errFiles: [],
              succMap: { [filename]: `${BACKEND_BASE}${res.url}` }
            }
          })
        } catch (e) {
          return JSON.stringify({ code: 1, msg: '接口解析失败', data: { errFiles: [files[0].name] } })
        }
      },
      error: (msg) => showStatus('图片上传失败: ' + msg, true),
    },
    after: () => { editorLoadError.value = false },
    input: (val) => { currentArticle.value.content = val },
  })
}

const showStatus = (msg, error = false) => {
  statusMessage.value = msg
  isError.value = error
  setTimeout(() => { statusMessage.value = '' }, 3000)
}

const loadArticleData = async () => {
  const articleId = route.params.id

  const isInvalidId = !articleId || articleId === 'undefined' || articleId === 'null' || articleId === ''

  await Promise.all([fetchCategories(), fetchTags()])

  if (isInvalidId) {
    await nextTick()
    initVditor('')
    return
  }

  const result = await getArticleDetail(articleId)
  if (result.success) {
    const info = result.data
    editingArticle.value = info

    let contentToLoad = ''
    if (info.contentPath) {
      const contentResult = await loadArticleContent(info.contentPath)
      contentToLoad = contentResult.success ? contentResult.data : ''
    }

    currentArticle.value = {
      title: info.title,
      content: contentToLoad,
      category_id: info.category?.id || null,
      tag_ids: info.tags?.map(t => t.id) || [],
    }

    if (info.tags) {
      selectedTags.value = info.tags.map(tag => ({ id: tag.id, name: tag.name }))
    }

    await nextTick()
    initVditor(currentArticle.value.content)
  } else {
    showStatus('获取文章失败: ' + result.message, true)
    setTimeout(() => router.push('/personal'), 1500)
  }
}

const handleSave = async () => {
  if (!canSave.value || isPending.value) return
  if (!currentArticle.value.content || currentArticle.value.content.trim() === '') {
    showStatus('文章内容不能为空', true)
    return
  }
  saving.value = true
  const payload = { ...currentArticle.value, id: editingArticle.value?.id || null }
  const result = await autoSaveArticle(payload)
  if (result.success) {
    if (!editingArticle.value) editingArticle.value = { id: result.data.id, status: 'draft' }
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
onUnmounted(() => { if (vditorInstance) vditorInstance.destroy() })
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
.notice-icon { font-size: 16px; }
.selected-tag.disabled { opacity: 0.6; cursor: not-allowed; }
.selected-tag.disabled .remove-tag { display: none; }
</style>
