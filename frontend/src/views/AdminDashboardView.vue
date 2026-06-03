<template>
  <div class="admin-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <button class="btn-back" @click="goBack">← 返回</button>
          <span class="card-title">管理中心</span>
          <span v-if="pendingCount > 0" class="pending-badge">待审核 {{ pendingCount }} 篇</span>
        </div>

        <div class="card-body">
          <div class="grid-layout">
            <!-- 文章管理 -->
            <div class="admin-card" @click="handleNav('/manage-articles')">
              <div class="admin-card-icon">📂</div>
              <div class="admin-card-info">
                <span class="admin-card-title">文章管理</span>
                <span class="admin-card-desc">全站文章管理、审核、置顶</span>
              </div>
            </div>

            <!-- 分类管理 -->
            <div class="admin-card" @click="handleNav('/categories')">
              <div class="admin-card-icon">📁</div>
              <div class="admin-card-info">
                <span class="admin-card-title">分类管理</span>
                <span class="admin-card-desc">创建、编辑、删除文章分类</span>
              </div>
            </div>

            <!-- 标签管理 -->
            <div class="admin-card" @click="handleNav('/tags')">
              <div class="admin-card-icon">🏷️</div>
              <div class="admin-card-info">
                <span class="admin-card-title">标签管理</span>
                <span class="admin-card-desc">创建、编辑、删除文章标签</span>
              </div>
            </div>

            <!-- 评论巡查 -->
            <div class="admin-card" @click="handleNav('/comment-admin')">
              <div class="admin-card-icon">💬</div>
              <div class="admin-card-info">
                <span class="admin-card-title">评论巡查</span>
                <span class="admin-card-desc">全站评论审核、批量操作</span>
              </div>
            </div>

            <!-- 举报管理 -->
            <div class="admin-card" @click="handleNav('/comment-reports')">
              <div class="admin-card-icon">🚨</div>
              <div class="admin-card-info">
                <span class="admin-card-title">举报管理</span>
                <span class="admin-card-desc">处理用户举报的不当评论</span>
              </div>
            </div>

            <!-- 文章导入 -->
            <div class="admin-card" @click="handleNav('/article-import')">
              <div class="admin-card-icon">📥</div>
              <div class="admin-card-info">
                <span class="admin-card-title">文章导入</span>
                <span class="admin-card-desc">单篇/批量导入、ZIP图床上传</span>
              </div>
            </div>

            <!-- 频道管理 -->
            <div class="admin-card" @click="handleNav('/message')">
              <div class="admin-card-icon">💬</div>
              <div class="admin-card-info">
                <span class="admin-card-title">频道管理</span>
                <span class="admin-card-desc">管理聊天频道、编辑或删除</span>
              </div>
            </div>

            <!-- 用户管理（待定扩展） -->
            <div class="admin-card admin-card-disabled">
              <div class="admin-card-icon">👥</div>
              <div class="admin-card-info">
                <span class="admin-card-title">用户管理</span>
                <span class="admin-card-desc">用户角色管理（开发中）</span>
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
import { getMyPendingCount } from '@/services/articleService'

const router = useRouter()
const slidIn = ref(false)
const pendingCount = ref(0)

const goBack = () => router.push('/personal')

const handleNav = (path) => {
  router.push(path)
}

onMounted(async () => {
  const r = await getMyPendingCount()
  if (r.success) pendingCount.value = r.data.pendingCount ?? r.data.pending_count ?? 0
  requestAnimationFrame(() => { slidIn.value = true })
})
</script>

<style lang="scss">
@use 'sass:color';
@use './test_scss.scss' as *;

.admin-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }

.glass-wrap {
  position: absolute; bottom: 0; left: $space-lg; right: $space-lg;
  height: calc(100vh - 90px - 5vh); display: flex; flex-direction: column;
}

.glass-card {
  background: rgba(26, 26, 31, 0.92);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid $glass-border; border-bottom: none;
  display: flex; flex-direction: column; height: 100%;
  transform: translateY(100%);
  opacity: 0;
  transition: transform 0.45s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.4s ease;
  overflow: hidden;
  &.slide-in { transform: translateY(0); opacity: 1; }
}

.card-header {
  display: flex; align-items: center; gap: $space-md;
  padding: $space-md $space-xl;
  border-bottom: 1px solid $glass-border; flex-shrink: 0;
  .btn-back { background: none; border: none; color: $text-secondary; cursor: pointer; font-size: 0.9rem; padding: 0; &:hover { color: $text-primary; } }
  .card-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; flex: 1; }
}

.pending-badge { padding: 3px 10px; background: rgba($color-warning, 0.15); color: $color-warning; border-radius: 12px; font-size: 0.75rem; font-weight: 500; }

.card-body { flex: 1; overflow-y: auto; padding: $space-xl; }

.grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: $space-md;
}

.admin-card {
  display: flex; align-items: center; gap: $space-md;
  padding: $space-lg; background: $bg-surface; border: 1px solid $glass-border;
  cursor: pointer; transition: all 0.2s ease;
  &:hover { border-color: $color-primary; background: $bg-hover; }
}

.admin-card-disabled {
  opacity: 0.4; cursor: not-allowed;
  &:hover { border-color: $glass-border; background: $bg-surface; }
}

.admin-card-icon { font-size: 1.8rem; flex-shrink: 0; }

.admin-card-info {
  display: flex; flex-direction: column; gap: 4px; min-width: 0;
}

.admin-card-title { font-size: 0.95rem; font-weight: 600; color: $text-primary; }

.admin-card-desc { font-size: 0.78rem; color: $text-tertiary; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
