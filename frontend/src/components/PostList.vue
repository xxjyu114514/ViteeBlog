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
import { useArticleAPI } from '@/composables/useArticleAPI'

const currentTab = ref('latest')
const articles = ref([])
const loading = ref(true)
const error = ref(null)

const { getPublicArticles } = useArticleAPI()

// 加载文章数据
const loadArticles = async () => {
  loading.value = true
  error.value = null
  
  const result = await getPublicArticles()
  if (result.success) {
    // 后端返回的是分页对象 {items: [], total: number, page: number, size: number}
    // 需要提取 items 数组
    articles.value = result.data.items || []
  } else {
    error.value = result.message
  }
  loading.value = false
}

// 过滤文章（最新/热门）
const filteredArticles = computed(() => {
  if (currentTab.value === 'hot') {
    // 热门文章按阅读量排序
    return [...articles.value].sort((a, b) => b.view_count - a.view_count)
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
</script>

<style lang="scss" scoped>
.post-list-wrapper {
  padding: 60px 24px; // 增加顶部高度，避开固定导航栏
}

.tab-header {
  display: flex;
  gap: 20px; 
  border-bottom: 1px solid rgba(0, 0, 0, 0.06); // 极淡的底线
  margin-bottom: 40px;
  
  button {
    padding: 14px 12px;
    background: none;
    border: none;
    font-size: 1.05rem;
    color: var(--text-secondary);
    cursor: pointer;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:hover {
      color: var(--text-main);
    }

    &.active {
      color: var(--primary-color);
      font-weight: 600;
      
      &::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 100%;
        height: 2.5px;
        background: var(--primary-color);
        border-radius: 4px 4px 0 0; // 顶部微圆角
      }
    }
    
    &.refresh-btn {
      margin-left: auto;
      padding: 14px 16px;
      font-size: 0.9rem;
      color: var(--primary-color);
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

.list-content {
  display: flex;
  flex-direction: column;
  gap: 24px; // 帖子卡片之间的间距
}
</style>