<template>
  <div class="post-item-card card card-hover" @click="handleClick">
    <div class="post-meta meta-text">
      <span class="date">{{ formatDate(post.published_at) }}</span>
      <span class="dot">·</span>
      <span class="views">{{ post.view_count }} 阅读</span>
    </div>
    <h2 class="post-title title-large">{{ post.title }}</h2>
    <p class="post-summary text-clamp-2">{{ post.summary }}</p>
    <div class="post-footer">
      <span class="more">阅读全文</span>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  post: Object
})

const router = useRouter()

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 处理点击事件
const handleClick = () => {
  if (props.post && props.post.id) {
    router.push(`/article/${props.post.id}`)
  }
}
</script>

<style lang="scss" scoped>
.post-item-card {
  cursor: pointer;

  &:hover {
    .more {
      color: var(--primary-color);
      padding-left: 5px;
    }
  }
}

.post-meta {
  margin-bottom: 12px;
  .dot { opacity: 0.5; }
}

.post-title {
  margin-bottom: 12px;
}

.post-summary {
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 20px;
}

.post-footer {
  .more {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--text-secondary);
    transition: all 0.3s ease;
  }
}
</style>