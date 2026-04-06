<template>
  <div class="post-item-card">
    <div class="post-meta">
      <span class="date">{{ post.date }}</span>
      <span class="dot">·</span>
      <span class="views">{{ post.views }} 阅读</span>
    </div>
    <h2 class="post-title">{{ post.title }}</h2>
    <p class="post-summary">{{ post.summary }}</p>
    <div class="post-footer">
      <span class="more">阅读全文</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  post: Object
})
</script>

<style lang="scss" scoped>
.post-item-card {
  padding: 30px;
  background: #ffffff;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.03); // 几乎看不见的边框
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  cursor: pointer;

  &:hover {
    transform: translateY(-6px); // 丝滑上移
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05); // 柔和阴影
    border-color: rgba(59, 130, 246, 0.15); // 悬停微蓝
    
    .more {
      color: #3b82f6;
      padding-left: 5px;
    }
  }
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #86868b;
  margin-bottom: 12px;
  
  .dot { opacity: 0.5; }
}

.post-title {
  font-size: 1.45rem;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
  line-height: 1.3;
}

.post-summary {
  font-size: 0.98rem;
  color: #48484a;
  line-height: 1.6;
  margin-bottom: 20px;
  /* 限制两行省略 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-footer {
  .more {
    font-size: 0.9rem;
    font-weight: 500;
    color: #86868b;
    transition: all 0.3s ease;
  }
}
</style>