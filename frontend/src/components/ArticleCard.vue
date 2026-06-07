<template>
  <div
    class="article-card"
    :class="{ 'is-immersive-item': immersive }"
    @click="$emit('click', article.id)"
  >
    <div class="article-card__header">
      <div v-if="immersive" class="meta-row">
        <span class="item-index">{{ String(index + 1).padStart(2, '0') }}</span>
        <h3 class="article-card__title">{{ article.title || '无标题文章' }}</h3>
      </div>
      <template v-else>
        <h3 class="article-card__title">
          <a href="javascript:void(0)">{{ article.title || '无标题文章' }}</a>
        </h3>
        <div class="article-card__meta">
          <span>作者</span>
          <span>{{ formatDate(article.publishedAt) }}</span>
          <span>· {{ article.viewCount || 0 }} 阅读</span>
        </div>
      </template>
    </div>

    <div v-if="article.summary" class="article-card__content">
      <p class="article-card__excerpt">{{ article.summary }}</p>
    </div>

    <div class="article-card__footer">
      <div class="article-card__stats">
        <span>❤️ {{ article.likeCount || 0 }}</span>
        <span>💬 {{ article.commentCount || 0 }}</span>
      </div>
      <span v-if="immersive" class="static-arrow">→</span>
      <span v-else class="article-card__tag">阅读全文 →</span>
    </div>
  </div>
</template>

<script setup>
import { formatDate } from '@/utils'

defineProps({
  article: { type: Object, required: true },
  index: { type: Number, default: 0 },
  immersive: { type: Boolean, default: false },
})

defineEmits(['click'])
</script>
