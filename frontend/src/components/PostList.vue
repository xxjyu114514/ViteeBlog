<template>
  <div class="post-list-wrapper container-narrow">
    <div class="tab-header">
      <button 
        :class="{ active: currentTab === 'latest' }" 
        @click="currentTab = 'latest'"
      >最新文章</button>
      <button 
        :class="{ active: currentTab === 'hot' }" 
        @click="currentTab = 'hot'"
      >热门文章</button>
      <button 
        class="refresh-btn"
        @click="loadArticles"
        :disabled="loading"
      >
        🔄 刷新
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载文章列表中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button class="btn-primary mt-20" @click="loadArticles">
        重新加载
      </button>
    </div>

    <div v-else-if="filteredArticles.length === 0" class="empty-state">
      <p>暂无文章</p>
    </div>

    <div v-else class="list-content">
      <PostItem 
        v-for="article in filteredArticles" 
        :key="article.id" 
        :post="article" 
        class="post-item-card"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PostItem from './PostItem.vue'
import { getPublicArticles } from '@/services/articleService'

const currentTab = ref('latest')
const articles = ref([])
const loading = ref(true)
const error = ref(null)

// 加载文章数据
const loadArticles = async () => {
  loading.value = true
  error.value = null
  
  const result = await getPublicArticles()
  
  if (result.success) {
    articles.value = result.data?.items || []
  } else {
    error.value = result.message
  }
  loading.value = false
}

// 过滤文章（最新/热门）
const filteredArticles = computed(() => {
  if (currentTab.value === 'hot') {
    // 热门文章按阅读量排序
    return [...articles.value].sort((a, b) => b.viewCount - a.view_count)
  } else {
    // 最新文章按发布时间排序（已经是降序）
    return articles.value
  }
})

// 初始化加载
onMounted(() => {
  loadArticles()
})

// 暴露方法给父组件
defineExpose({
  refresh: loadArticles
})

import "./PostList.scss"
</script>