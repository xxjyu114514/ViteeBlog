<template>
  <div class="user-dashboard-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <span class="card-title">管理中心</span>
        </div>

        <div class="card-body">
          <div class="grid-layout">
            <!-- 我的文章 -->
            <div class="dash-card" @click="handleNav('/manage-articles')">
              <div class="dash-card-icon">📂</div>
              <div class="dash-card-info">
                <span class="dash-card-title">我的文章</span>
                <span class="dash-card-desc">管理、编辑、发布文章</span>
              </div>
            </div>

            <!-- 分类管理 -->
            <div class="dash-card" @click="handleNav('/categories')">
              <div class="dash-card-icon">📁</div>
              <div class="dash-card-info">
                <span class="dash-card-title">分类管理</span>
                <span class="dash-card-desc">创建、管理文章分类</span>
              </div>
            </div>

            <!-- 标签管理 -->
            <div class="dash-card" @click="handleNav('/tags')">
              <div class="dash-card-icon">🏷️</div>
              <div class="dash-card-info">
                <span class="dash-card-title">标签管理</span>
                <span class="dash-card-desc">创建、管理文章标签</span>
              </div>
            </div>

            <!-- 文章导入 -->
            <div class="dash-card" @click="handleNav('/article-import')">
              <div class="dash-card-icon">📥</div>
              <div class="dash-card-info">
                <span class="dash-card-title">文章导入</span>
                <span class="dash-card-desc">单篇/批量导入文章</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const slidIn = ref(false)

const handleNav = (path) => {
  router.push(path)
}

onMounted(() => {
  requestAnimationFrame(() => { slidIn.value = true })
})
</script>

<style lang="scss">
@use 'sass:color';
@use '../_design.scss' as *;

.user-dashboard-page {
  position: fixed;
  inset: 0;
  z-index: 1;
  overflow: hidden;
}

.glass-wrap {
  position: absolute;
  bottom: 0;
  left: $space-lg;
  right: $space-lg;
  height: calc(100vh - 90px - 5vh);
  display: flex;
  flex-direction: column;
}

.glass-card {
  background: rgba(26, 26, 31, 0.92);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid $glass-border;
  border-bottom: none;
  display: flex;
  flex-direction: column;
  height: 100%;
  transform: translateY(100%);
  opacity: 0;
  transition: transform 0.45s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.4s ease;
  overflow: hidden;
  &.slide-in { transform: translateY(0); opacity: 1; }
}

.card-header {
  display: flex;
  align-items: center;
  gap: $space-md;
  padding: $space-md $space-xl;
  border-bottom: 1px solid $glass-border;
  flex-shrink: 0;
  .card-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; flex: 1; }
}

.card-body {
  flex: 1;
  overflow-y: auto;
  padding: $space-xl;
}

.grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: $space-md;
}

.dash-card {
  display: flex;
  align-items: center;
  gap: $space-md;
  padding: $space-lg;
  background: $bg-surface;
  border: 1px solid $glass-border;
  cursor: pointer;
  transition: all 0.2s ease;
  &:hover { border-color: $color-primary; background: $bg-hover; }
}

.dash-card-icon { font-size: 1.8rem; flex-shrink: 0; }

.dash-card-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.dash-card-title { font-size: 0.95rem; font-weight: 600; color: $text-primary; }

.dash-card-desc { font-size: 0.78rem; color: $text-tertiary; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
