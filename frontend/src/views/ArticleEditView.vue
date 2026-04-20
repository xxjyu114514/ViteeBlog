<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div class="container-narrow">
      <div class="editor-header flex-between">
        <h1 class="title-large">{{ editingArticle ? '编辑文章' : '新建文章' }}</h1>
        <div class="editor-actions">
          <button 
            class="btn-secondary" 
            @click="goBack"
            :disabled="saving"
          >
            返回
          </button>
          <button 
            class="btn-primary" 
            @click="handleSave"
            :disabled="saving || !canSave"
          >
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

      <div v-if="errorMessage" class="error-message mb-20">
        {{ errorMessage }}
      </div>

      <div class="editor-form">
        <div class="form-group">
          <label>标题（支持Markdown）</label>
          <input 
            v-model="currentArticle.title" 
            type="text" 
            class="input-field"
            placeholder="请输入文章标题（支持Markdown语法）"
            :disabled="saving"
          >
          <div v-if="currentArticle.title" class="title-preview mt-10">
            <strong>标题预览:</strong>
            <div class="markdown-preview" v-html="renderedTitle"></div>
          </div>
        </div>
        
        <div class="form-group">
          <label>分类ID</label>
          <input 
            v-model="currentArticle.category_id" 
            type="number" 
            class="input-field"
            placeholder="可选，输入分类ID"
            :disabled="saving"
          >
        </div>
        
        <div class="form-group">
          <label>标签IDs（用逗号分隔）</label>
          <input 
            v-model="tagInput" 
            type="text" 
            class="input-field"
            placeholder="可选，如：1,2,3"
            :disabled="saving"
          >
        </div>

        <div class="form-group">
          <label>内容（Markdown）</label>
          <div class="editor-container">
            <textarea 
              v-model="currentArticle.content" 
              class="editor-textarea"
              placeholder="请输入文章内容（支持Markdown语法）"
              :disabled="saving"
              @input="handleContentChange"
            ></textarea>
            <div class="preview-panel">
              <h3>预览</h3>
              <div 
                class="markdown-preview" 
                v-html="renderedContent"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useArticleAPI } from '@/composables/useArticleAPI'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

// 初始化Markdown解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(str, { language: lang }).value
    }
    return ''
  }
})

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { autoSaveArticle, publishArticle, getArticleDetail } = useArticleAPI()

// 状态
const currentArticle = ref({
  title: '',
  content: '',
  category_id: null,
  tag_ids: []
})
const tagInput = ref('')
const saving = ref(false)
const publishing = ref(false)
const errorMessage = ref('')
const editingArticle = ref(null)

// 计算属性
const canSave = computed(() => {
  return currentArticle.value.title.trim() !== '' && 
         currentArticle.value.content.trim() !== ''
})

const renderedContent = computed(() => {
  if (!currentArticle.value.content) return ''
  return md.render(currentArticle.value.content)
})

const renderedTitle = computed(() => {
  if (!currentArticle.value.title) return ''
  return md.renderInline(currentArticle.value.title)
})

// 处理内容变化
const handleContentChange = () => {
  // 可以在这里添加实时预览逻辑
}

// 保存文章
const handleSave = async () => {
  if (!canSave.value) return
  
  // 解析标签输入
  if (tagInput.value.trim()) {
    try {
      currentArticle.value.tag_ids = tagInput.value
        .split(',')
        .map(id => parseInt(id.trim()))
        .filter(id => !isNaN(id))
    } catch (e) {
      errorMessage.value = '标签格式错误，请输入数字ID，用逗号分隔'
      return
    }
  } else {
    currentArticle.value.tag_ids = []
  }

  saving.value = true
  errorMessage.value = ''
  
  const articleData = {
    title: currentArticle.value.title,
    content: currentArticle.value.content,
    article_id: editingArticle.value?.id || null,
    category_id: currentArticle.value.category_id || null,
    tag_ids: currentArticle.value.tag_ids
  }

  const result = await autoSaveArticle(articleData)
  if (result.success) {
    // 如果是新建文章，更新编辑状态
    if (!editingArticle.value) {
      editingArticle.value = { id: result.data.article_id, status: 'draft' }
    }
    errorMessage.value = '保存成功！'
    setTimeout(() => {
      errorMessage.value = ''
    }, 3000)
  } else {
    errorMessage.value = result.message
  }
  saving.value = false
}

// 发布文章
const handlePublish = async () => {
  if (!editingArticle.value || !canSave.value) return
  
  publishing.value = true
  const result = await publishArticle(editingArticle.value.id)
  if (result.success) {
    alert('文章已成功发布！')
    router.push('/posts')
  } else {
    alert(result.message)
  }
  publishing.value = false
}

// 返回
const goBack = () => {
  router.push('/personal')
}

// 加载文章详情（如果是编辑模式）
const loadArticle = async () => {
  const articleId = route.params.id
  if (!articleId) return

  const result = await getArticleDetail(articleId)
  if (result.success) {
    editingArticle.value = result.data.info
    currentArticle.value = {
      title: result.data.info.title,
      content: result.data.content,
      category_id: result.data.info.category?.id || null,
      tag_ids: result.data.info.tags.map(tag => tag.id) || []
    }
    tagInput.value = currentArticle.value.tag_ids.join(',')
  } else {
    alert(result.message)
    router.push('/personal')
  }
}

// 监听标签输入变化
watch(tagInput, (newVal) => {
  if (newVal === '') {
    currentArticle.value.tag_ids = []
  }
})

// 初始化
onMounted(() => {
  if (route.params.id) {
    loadArticle()
  }
})
</script>