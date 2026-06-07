<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div class="container-narrow">
      <h1 class="title-large mb-30">文章归档</h1>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="archive.length === 0" class="empty-state">
        <p>暂无已发布的文章</p>
      </div>

      <div v-else class="archive-list">
        <div v-for="(group, yearIdx) in groupedArchive" :key="yearIdx" class="archive-year-group">
          <h2 class="year-title">{{ group.year }} 年</h2>
          <div class="month-list">
            <div
              v-for="item in group.months"
              :key="item.month"
              class="month-item"
              @click="goToMonth(item.year, item.month)"
            >
              <span class="month-name">{{ item.month }} 月</span>
              <span class="month-count">{{ item.count }} 篇</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getArticleArchive } from '@/services/articleService'

const router = useRouter()
const archive = ref([])
const loading = ref(true)

const groupedArchive = computed(() => {
  const map = new Map()
  for (const item of archive.value) {
    if (!map.has(item.year)) {
      map.set(item.year, { year: item.year, months: [] })
    }
    map.get(item.year).months.push(item)
  }
  return Array.from(map.values()).sort((a, b) => b.year - a.year)
})

const goToMonth = (year, month) => {
  router.push(`/posts?year=${year}&month=${month}`)
}

onMounted(async () => {
  const r = await getArticleArchive()
  if (r.success) {
    archive.value = r.data || []
  }
  loading.value = false
})
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.title-large { font-size: 1.8rem; font-weight: 700; color: $text-primary; }

.mb-30 { margin-bottom: 30px; }

.loading-state { text-align: center; padding: 80px 0; p { color: $text-secondary; } }
.loading-spinner { width: 28px; height: 28px; border: 2px solid rgba(255,255,255,0.08); border-top-color: $color-primary; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state { text-align: center; padding: 80px 0; p { color: $text-secondary; } }

.archive-year-group { margin-bottom: 36px; }

.year-title {
  font-size: 1.4rem; font-weight: 600; color: $color-primary;
  padding-bottom: 12px; border-bottom: 1px solid $border-white-subtle; margin-bottom: 16px;
}

.month-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }

.month-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 18px; background: $bg-surface; border: 1px solid $glass-border;
  cursor: pointer; transition: all 0.2s ease;
  &:hover { border-color: $color-primary; background: $bg-hover; }
}

.month-name { font-weight: 500; color: $text-primary; font-size: 0.95rem; }
.month-count { font-size: 0.8rem; color: $text-tertiary; }
</style>
