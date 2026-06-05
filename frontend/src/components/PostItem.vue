<template>
  <div class="post-item-card card card-hover" @click="handleClick">
    <div class="post-meta meta-text">
      <span class="date">{{ formatDate(post.publishedAt) }}</span>
      <span class="dot">·</span>
      <span class="views">{{ post.viewCount }} 阅读</span>
    </div>
    <h2 class="post-title title-large" v-html="renderedTitle"></h2>
    <p class="post-summary text-clamp-2">{{ post.summary }}</p>
    <div class="post-footer">
      <span class="more">阅读全文</span>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import { useRouter } from 'vue-router'
import { formatDate, renderInline } from '@/utils'

const props = defineProps({
  post: Object
})

const router = useRouter()

// 渲染标题（支持 Markdown 语法）
const renderedTitle = computed(() => {
  if (!props.post?.title) return ''
  return renderInline(props.post.title)
})

// 处理点击事件
const handleClick = () => {
  if (props.post && props.post.id) {
    router.push(`/article/${props.post.id}`)
  }
}

import "./PostItem.scss"
</script>