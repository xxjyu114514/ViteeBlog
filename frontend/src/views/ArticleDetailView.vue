<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载文章中...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-content">
        <h2 class="error-title">文章加载失败</h2>
        <p class="error-message">{{ error }}</p>
        <button class="btn-primary mt-20" @click="loadArticle">
          重新加载
        </button>
        <button class="btn-secondary mt-10" @click="goBack">
          返回首页
        </button>
      </div>
    </div>
    
    <div v-else-if="article" class="article-detail-container">
      <div class="back-button" @click="handleBack">
        ← 返回
      </div>
      
      <div class="container-narrow">
        <div class="article-header">
          <h1 class="article-title" v-html="renderedTitle"></h1>
          <div class="article-meta flex-between">
            <div class="meta-info">
              <span class="author">作者: {{ getAuthorName() }}</span>
              <span class="publish-date">{{ formatDate(article.published_at) }}</span>
              <span class="view-count">阅读: {{ article.view_count || 0 }} 次</span>
            </div>
            <div v-if="userStore.isAdmin" class="admin-actions">
              <button class="btn-action btn-edit" @click="editArticle">
                编辑
              </button>
              <button 
                class="btn-action btn-delete" 
                @click="deleteArticle"
                :disabled="deleting"
              >
                {{ deleting ? '删除中...' : '删除' }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="article-content">
          <div 
            class="markdown-content" 
            v-html="renderedContent"
          ></div>
        </div>
        
        <div class="article-footer">
          <div class="category-tags">
            <div v-if="article.category" class="category-item">
              <span class="category-label">分类:</span>
              <span class="category-name">{{ article.category.name }}</span>
            </div>
            <div v-if="article.tags && article.tags.length > 0" class="tags-section">
              <span class="tags-label">标签:</span>
              <div class="tags-list">
                <span 
                  v-for="tag in article.tags" 
                  :key="tag.id" 
                  class="tag-item"
                >
                  {{ tag.name }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
const { getArticleDetail, softDeleteArticle } = useArticleAPI()

// 状态
const article = ref(null)
const articleContent = ref('') // 新增：存储从文件读取的Markdown内容
const loading = ref(true)
const error = ref(null)
const deleting = ref(false)

// 获取作者名称（处理author关系可能未加载的情况）
const getAuthorName = () => {
  if (article.value?.author?.username) {
    return article.value.author.username
  }
  // 如果author关系未加载，尝试从其他字段获取
  if (article.value?.user_id) {
    // 这里可以添加逻辑来根据user_id获取用户名，但需要额外API调用
    // 临时方案：显示用户ID或默认名称
    return `用户${article.value.user_id}`
  }
  return '匿名作者'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 渲染内容
const renderedContent = computed(() => {
  if (!articleContent.value) return ''
  return md.render(articleContent.value)
})

const renderedTitle = computed(() => {
  if (!article.value?.title) return ''
  return md.renderInline(article.value.title)
})

// 从文件路径加载Markdown内容
const loadArticleContent = async (contentPath) => {
  try {
    // contentPath 格式: "storage/articles/xxx.md"
    // 后端静态文件服务: /static/storage -> storage/
    // 所以URL应该是: /static/storage/articles/xxx.md
    let normalizedPath = contentPath.replace(/\\/g, '/')
    if (!normalizedPath.startsWith('/')) {
      normalizedPath = '/' + normalizedPath
    }
    // 将 "/storage/" 替换为 "/static/storage/"
    const urlPath = normalizedPath.replace(/^\/storage\//, '/static/storage/')
    const url = `http://127.0.0.1:8000${urlPath}`
    console.log('加载文章内容URL:', url)
    
    const response = await fetch(url)
    if (response.ok) {
      const content = await response.text()
      articleContent.value = content
    } else {
      console.error('加载文章内容失败:', response.status, response.statusText)
      articleContent.value = '# 文章内容加载失败'
    }
  } catch (err) {
    console.error('加载文章内容异常:', err)
    articleContent.value = '# 文章内容加载失败'
  }
}

// 加载文章
const loadArticle = async () => {
  loading.value = true
  error.value = null
  
  const articleId = route.params.id
  const result = await getArticleDetail(articleId)
  
  if (result.success) {
    article.value = result.data
    // 从 content_path 加载实际内容
    if (result.data.content_path) {
      await loadArticleContent(result.data.content_path)
    } else {
      articleContent.value = result.data.content || ''
    }
  } else {
    error.value = result.message
  }
  loading.value = false
}

// 编辑文章
const editArticle = () => {
  router.push(`/edit-article/${route.params.id}`)
}

// 删除文章
const deleteArticle = async () => {
  if (!confirm('确定要将此文章移至回收站吗？')) return
  
  deleting.value = true
  const result = await softDeleteArticle(route.params.id)
  if (result.success) {
    alert('文章已移至回收站')
    router.push('/posts')
  } else {
    alert(result.message)
  }
  deleting.value = false
}

// 返回首页
const goBack = () => {
  router.push('/')
}

// 返回上一页
const handleBack = () => {
  router.go(-1)
}

// 初始化
onMounted(() => {
  loadArticle()
})
</script>