<template>
  <div class="manage-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <button class="btn-back" @click="goBack">← 返回</button>
          <span class="card-title">{{ userStore.isAdmin ? '全站文章管理' : '我的文章' }}</span>
          <div class="header-actions">
            <span v-if="pendingCount > 0" class="pending-badge">待审核 {{ pendingCount }} 篇</span>
            <button class="btn btn-primary btn-sm" @click="handleCreateNew">新建</button>
          </div>
        </div>

        <div v-if="userStore.isAdmin" class="admin-bar">
          <div class="admin-left">
            <label class="admin-label">范围:</label>
            <select v-model="viewMode" class="admin-select" @change="fetchArticles(1)">
              <option value="all">全站</option>
              <option value="mine">我的</option>
            </select>
          </div>
          <div class="admin-links">
            <router-link to="/comment-reports" class="admin-link">举报管理</router-link>
            <router-link to="/comment-admin" class="admin-link">评论巡查</router-link>
            <router-link to="/article-import" class="admin-link">文章导入</router-link>
          </div>
        </div>

        <div class="card-body">
          <div v-if="articles.length > 0" class="article-list">
            <div v-for="article in articles" :key="article.id" class="article-item">
              <div class="article-info">
                <div class="article-title">{{ article.title }}</div>
                <div class="article-meta">
                  <span v-if="userStore.isAdmin && viewMode === 'all' && article.author">{{ article.author.username }} · </span>
                  <span>{{ formatDateTime(article.publishedAt || article.createdAt) }}</span>
                  <span :class="article.status === 'draft' ? 'badge-draft' : 'badge-published'">{{ article.status === 'draft' ? '草稿' : '已发布' }}</span>
                  <span>阅读 {{ article.viewCount || 0 }}</span>
                  <span v-if="article.isAudited" class="badge-audited">✓ 已审核</span>
                </div>
              </div>
              <div class="article-actions">
                <button v-if="canPublish(article)" class="act-btn act-publish" @click="handlePublish(article.id)" :disabled="publishingId === article.id">{{ publishingId === article.id ? '...' : '发布' }}</button>
                <button v-if="canEdit(article)" class="act-btn act-edit" @click="handleEdit(article.id)">编辑</button>
                <button v-if="canDelete(article)" class="act-btn act-delete" @click="handleSoftDelete(article.id)" :disabled="deletingId === article.id">{{ deletingId === article.id ? '...' : '删除' }}</button>
                <button v-if="canDelete(article)" class="act-btn act-hard" @click="handleHardDelete(article.id)" :disabled="hardDeletingId === article.id">{{ hardDeletingId === article.id ? '...' : '彻底删除' }}</button>
                <button v-if="userStore.isAdmin && !article.isAudited && article.status === 'pending'" class="act-btn act-audit" @click="openAudit(article.id)">审核</button>
                <button v-if="userStore.isAdmin" class="act-btn act-pin" @click="handleTogglePin(article.id)" :disabled="pinningId === article.id">{{ pinningId === article.id ? '...' : (article.isPinned ? '📌' : '📌') }}</button>
              </div>
            </div>

            <div v-if="totalPages > 1" class="pagination">
              <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">上一页</button>
              <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页（共 {{ totalArticles }} 篇）</span>
              <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">下一页</button>
            </div>
          </div>
          <div v-else-if="loading" class="state-msg"><div class="spinner"></div><p>加载中...</p></div>
          <div v-else class="state-msg"><p>{{ emptyMessage }}</p><button class="btn btn-primary btn-sm mt-20" @click="handleCreateNew">创建文章</button></div>
        </div>
      </div>
    </div>
    <AuditModal v-model:show="showAuditModal" :article-id="auditArticleId" @audit-success="onAuditSuccess" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import * as articleService from '@/services/articleService'
import { formatDateTime } from '@/utils'
import AuditModal from '@/components/AuditModal.vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const articles = ref([])
const publishingId = ref(null)
const deletingId = ref(null)
const hardDeletingId = ref(null)
const pinningId = ref(null)
const auditArticleId = ref(null)
const showAuditModal = ref(false)
const viewMode = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const totalArticles = ref(0)
const pendingCount = ref(0)
const slidIn = ref(false)

const emptyMessage = computed(() => {
  if (userStore.isAdmin) return viewMode.value === 'all' ? '全站暂无文章' : '您暂无文章'
  return '您暂无文章'
})
const totalPages = computed(() => Math.ceil(totalArticles.value / pageSize.value))
const canEdit = (article) => userStore.isAdmin || article.userId === userStore.userInfo?.id
const canDelete = (article) => userStore.isAdmin || article.userId === userStore.userInfo?.id
const canPublish = (article) => article.status === 'draft' && (userStore.isAdmin || article.userId === userStore.userInfo?.id)
const goBack = () => router.push('/personal')

const fetchArticles = async (page = 1) => {
  loading.value = true
  try {
    let result
    if (userStore.isAdmin && viewMode.value === 'all') result = await articleService.getAdminAllArticles({ page, size: pageSize.value })
    else result = await articleService.getMyArticles({ page, size: pageSize.value })
    if (result.success) { articles.value = result.data.items || []; totalArticles.value = result.data.total || 0; currentPage.value = page }
  } catch {}
  loading.value = false
}
const handleCreateNew = () => router.push('/edit-article')
const handleEdit = (id) => router.push(`/edit-article/${id}`)
const handlePublish = async (id) => { publishingId.value = id; const r = await articleService.publishArticle(id); if (r.success) await fetchArticles(currentPage.value); publishingId.value = null }
const handleSoftDelete = async (id) => { if (!confirm('移至回收站？')) return; deletingId.value = id; const r = await articleService.softDeleteArticle(id); if (r.success) await fetchArticles(currentPage.value); deletingId.value = null }
const handleHardDelete = async (id) => { if (!confirm('⚠️ 确定彻底删除？不可撤销！')) return; if (!confirm('再次确认！')) return; hardDeletingId.value = id; const r = await articleService.hardDeleteArticle(id); if (r.success) await fetchArticles(currentPage.value); hardDeletingId.value = null }
const handleTogglePin = async (id) => { pinningId.value = id; const r = await articleService.togglePinArticle(id); if (r.success) await fetchArticles(currentPage.value); pinningId.value = null }
const openAudit = (id) => { auditArticleId.value = id; showAuditModal.value = true }
const onAuditSuccess = () => fetchArticles(currentPage.value)
const goToPage = (page) => { if (page >= 1 && page <= totalPages.value) fetchArticles(page) }

onMounted(async () => {
  if (!userStore.isAdmin) viewMode.value = 'mine'
  const r = await articleService.getMyPendingCount()
  if (r.success) pendingCount.value = r.data.pendingCount ?? r.data.pending_count ?? 0
  await fetchArticles(1)
  requestAnimationFrame(() => { slidIn.value = true })
})
</script>

<style lang="scss">
@use 'sass:color';
@use './test_scss.scss' as *;

.manage-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }
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
  .header-actions { display: flex; align-items: center; gap: $space-sm; }
}
.pending-badge { padding: 3px 10px; background: rgba($color-warning, 0.15); color: $color-warning; border-radius: 12px; font-size: 0.75rem; font-weight: 500; }
.btn-sm { padding: 4px 12px; font-size: 0.8rem; }

.admin-bar {
  display: flex; justify-content: space-between; align-items: center;
  padding: $space-sm $space-xl; background: $bg-surface; border-bottom: 1px solid $glass-border; flex-shrink: 0;
  .admin-left { display: flex; align-items: center; gap: 8px; }
  .admin-label { font-size: 0.8rem; color: $text-secondary; }
  .admin-select { padding: 4px 8px; background: $bg-elevated; border: 1px solid $glass-border; color: $text-primary; font-size: 0.8rem; &:focus { outline: none; border-color: $color-primary; } option { background: $bg-surface; } }
  .admin-links { display: flex; gap: $space-sm; }
  .admin-link { padding: 4px 12px; background: $bg-hover; color: $color-primary; border-radius: 4px; text-decoration: none; font-size: 0.8rem; &:hover { background: rgba($color-primary, 0.15); } }
}

.card-body { flex: 1; overflow-y: auto; padding: $space-xl; }

.article-list { display: flex; flex-direction: column; gap: 8px; }
.article-item {
  padding: $space-md; transition: background 0.15s;
  &:hover { background: $bg-hover; }
  .article-info { margin-bottom: 8px; }
  .article-title { font-size: 1rem; font-weight: 500; color: $text-primary; margin-bottom: 4px; }
  .article-meta { font-size: 0.8rem; color: $text-tertiary; span { margin-right: 8px; } }
}
.badge-draft { color: $color-warning; }
.badge-published { color: $color-success; }
.badge-audited { color: $color-primary; }
.article-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.act-btn {
  padding: 4px 12px; font-size: 0.78rem; border: 1px solid $glass-border; background: transparent;
  color: $text-secondary; cursor: pointer; &:hover { border-color: $color-primary; color: $color-primary; }
  &:disabled { opacity: 0.4; cursor: not-allowed; }
}
.act-publish { color: $color-success; border-color: rgba($color-success, 0.3); &:hover { border-color: $color-success; } }
.act-edit { color: $color-primary; border-color: rgba($color-primary, 0.3); &:hover { border-color: $color-primary; } }
.act-delete { color: $color-error; border-color: rgba($color-error, 0.3); &:hover { border-color: $color-error; } }
.act-hard { color: $color-error; border-color: rgba($color-error, 0.3); &:hover { background: rgba($color-error, 0.1); } }
.act-audit { color: $color-accent; border-color: rgba($color-accent, 0.3); &:hover { border-color: $color-accent; } }
.act-pin { color: $color-secondary; border-color: rgba($color-secondary, 0.3); &:hover { border-color: $color-secondary; } }

.pagination { display: flex; justify-content: center; align-items: center; gap: $space-md; margin-top: $space-xl; }
.page-btn { padding: 6px 16px; background: $bg-elevated; border: 1px solid $glass-border; color: $text-secondary; cursor: pointer; font-size: 0.85rem; &:hover { color: $text-primary; border-color: $color-primary; } &:disabled { opacity: 0.4; cursor: not-allowed; } }
.page-info { font-size: 0.8rem; color: $text-tertiary; }
.state-msg { display: flex; flex-direction: column; align-items: center; gap: $space-md; padding: $space-2xl 0; p { color: $text-secondary; font-size: 0.95rem; } }
.spinner { width: 24px; height: 24px; border: 2px solid rgba($text-tertiary, 0.25); border-top-color: $color-primary; border-radius: 50%; animation: mspin 0.8s linear infinite; }
@keyframes mspin { to { transform: rotate(360deg); } }
.mt-20 { margin-top: 20px; }
</style>
