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
      <div class="container-narrow">
        <div class="article-header">
          <h1 class="article-title" v-html="renderedTitle"></h1>
          <div class="article-meta flex-between">
            <div class="meta-info">
              <span class="author">作者: {{ article.info.author.username }}</span>
              <span class="publish-date">{{ formatDate(article.info.published_at) }}</span>
              <span class="view-count">阅读: {{ article.info.view_count }} 次</span>
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
            <div v-if="article.info.category" class="category-item">
              <span class="category-label">分类:</span>
              <span class="category-name">{{ article.info.category.name }}</span>
            </div>
            <div v-if="article.info.tags && article.info.tags.length > 0" class="tags-section">
              <span class="tags-label">标签:</span>
              <div class="tags-list">
                <span 
                  v-for="tag in article.info.tags" 
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
const loading = ref(true)
const error = ref(null)
const deleting = ref(false)

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
  if (!article.value?.content) return ''
  return md.render(article.value.content)
})

const renderedTitle = computed(() => {
  if (!article.value?.info?.title) return ''
  return md.renderInline(article.value.info.title)
})

// 加载文章
const loadArticle = async () => {
  loading.value = true
  error.value = null
  
  const articleId = route.params.id
  const result = await getArticleDetail(articleId)
  
  if (result.success) {
    article.value = result.data
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

// 初始化
onMounted(() => {
  loadArticle()
})
</script>