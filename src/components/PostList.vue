<template>
  <div class="post-list-wrapper">
    <div class="tab-header">
      <button 
        :class="{ active: currentTab === 'latest' }" 
        @click="currentTab = 'latest'"
      >最新文章</button>
      <button 
        :class="{ active: currentTab === 'hot' }" 
        @click="currentTab = 'hot'"
      >热门文章</button>
    </div>

    <div class="list-content">
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
import { ref, computed } from 'vue'
import PostItem from './PostItem.vue'

const currentTab = ref('latest')

const articles = ref([
  { id: 1, title: '如何使用 Vite 快速构建项目', summary: 'Vite 是下一代前端工具链，能够显著提升前端开发体验。', date: '2026-04-01', views: 120, type: 'latest' },
  { id: 2, title: 'Vue3 组合式 API 实战', summary: 'Setup 语法糖让你的代码更简洁，逻辑更易于复用和维护。', date: '2026-03-28', views: 540, type: 'hot' },
  { id: 3, title: 'CSS 现代布局指南', summary: '从 Flexbox 到 Grid，掌握现代 Web 布局的核心技术。', date: '2026-03-15', views: 320, type: 'latest' },
])

const filteredArticles = computed(() => {
  return currentTab.value === 'latest' 
    ? [...articles.value].sort((a, b) => b.id - a.id)
    : [...articles.value].sort((a, b) => b.views - a.views)
})
</script>

<style lang="scss" scoped>
.post-list-wrapper {
  max-width: 860px; // 稍微放宽，适合阅读
  margin: 0 auto;
  padding: 60px 24px; // 增加顶部高度，避开固定导航栏
}

.tab-header {
  display: flex;
  gap: 40px; 
  border-bottom: 1px solid rgba(0, 0, 0, 0.06); // 极淡的底线
  margin-bottom: 40px;
  
  button {
    padding: 14px 4px;
    background: none;
    border: none;
    font-size: 1.05rem;
    color: #86868b; // iOS 辅助色
    cursor: pointer;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:hover {
      color: #1d1d1f; // 悬停加深
    }

    &.active {
      color: #3b82f6; // 保持你的蓝色
      font-weight: 600;
      
      &::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 100%;
        height: 2.5px;
        background: #3b82f6;
        border-radius: 4px 4px 0 0; // 顶部微圆角
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