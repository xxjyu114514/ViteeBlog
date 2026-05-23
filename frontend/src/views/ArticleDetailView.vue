<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载文章中...</p>
    </div>
    <div v-else-if="error" class="error-container">
      <div class="error-content">
        <h2 class="error-title">文章加载失败</h2>
        <p class="error-message">{{ error }}</p>
        <button class="btn-primary mt-20" @click="loadArticle">重新加载</button>
        <button class="btn-secondary mt-10" @click="goBack">返回首页</button>
      </div>
    </div>
    <div v-else-if="article" class="article-detail-container">
      <div class="back-button" @click="handleBack">← 返回</div>
      <div class="container-narrow">
        <div class="article-header">
          <h1 class="article-title" v-html="renderedTitle"></h1>
          <div class="article-meta flex-between">
            <div class="meta-info">
              <span class="author">作者: {{ getAuthorName() }}</span>
              <button v-if="canFollow" class="btn-follow" @click="toggleFollow" :disabled="followLoading">
                {{ followLoading ? '...' : (isFollowing ? '✓ 已关注' : '+ 关注') }}
              </button>
              <span class="publish-date">{{ formatDateTime(article.publishedAt) }}</span>
              <span class="view-count">阅读: {{ article.viewCount || 0 }} 次</span>
              <span class="like-count">
                <button class="btn-like" :class="{ liked: isLiked }" :disabled="likeLoading" @click="toggleLike">
                  {{ isLiked ? '❤️' : '🤍' }} {{ likeCount }}
                </button>
              </span>
            </div>
            <div class="article-actions">
              <button class="btn-favorite" :class="{ favorited: isFavorited }" :disabled="favoriteLoading" @click="toggleFav">
                {{ isFavorited ? '❤️ 已收藏' : '🤍 收藏' }}
              </button>
              <div v-if="userStore.isAdmin" class="admin-actions">
                <button class="btn-action btn-edit" @click="editArticle">编辑</button>
                <button class="btn-action btn-delete" @click="deleteArticle" :disabled="deleting">{{ deleting ? '删除中...' : '删除' }}</button>
              </div>
            </div>
          </div>
        </div>
        <div class="article-content" v-html="renderedContent"></div>
        <div class="comment-section">
          <div class="section-header">
            <h2 class="title">评论区</h2>
            <span class="count">{{ commentCount }} 条评论</span>
          </div>
          <CommentForm :article-id="route.params.id" @comment-submitted="handleNewComment" />
          <CommentList :article-id="route.params.id" @comments-loaded="updateCommentCount" ref="commentListRef" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getArticleDetail as fetchArticleDetail, softDeleteArticle, loadArticleContent, toggleArticleLike, getArticleLikeCount } from '@/services/articleService'
import { toggleFavorite, checkFavoriteStatus } from '@/services/favoriteService'
import { followUser, unfollowUser } from '@/services/socialService'
import CommentForm from '@/components/CommentForm.vue'
import CommentList from '@/components/CommentList.vue'
import { formatDateTime, renderMarkdown, renderInline } from '@/utils'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const article = ref(null)
const articleContent = ref('')
const loading = ref(true)
const error = ref(null)
const deleting = ref(false)
const commentCount = ref(0)
const commentListRef = ref(null)
const isFavorited = ref(false)
const favoriteLoading = ref(false)
const isLiked = ref(false)
const likeCount = ref(0)
const likeLoading = ref(false)
const isFollowing = ref(false)
const followLoading = ref(false)
const authorId = ref(null)

const canFollow = computed(() => userStore.isAuthenticated && authorId.value && authorId.value !== userStore.userInfo?.id)

const getAuthorName = () => {
  if (article.value?.author?.username) return article.value.author.username
  if (article.value?.userId) return `用户${article.value.userId}`
  return '匿名作者'
}

const renderedContent = computed(() => { if (!articleContent.value) return ''; return renderMarkdown(articleContent.value) })
const renderedTitle = computed(() => { if (!article.value?.title) return ''; return renderInline(article.value.title) })

const loadArticle = async () => {
  loading.value = true; error.value = null
  const articleId = route.params.id
  const result = await fetchArticleDetail(articleId)
  if (result.success) {
    article.value = result.data
    if (result.data.contentPath) {
      const contentResult = await loadArticleContent(result.data.contentPath)
      articleContent.value = contentResult.success ? contentResult.data : (result.data.content || '')
    } else {
      articleContent.value = result.data.content || ''
    }
    if (userStore.isAuthenticated) {
      const favResult = await checkFavoriteStatus(articleId)
      if (favResult.success) isFavorited.value = favResult.data.favorited
    }
    if (result.data.isLiked !== undefined) isLiked.value = result.data.isLiked
    if (result.data.likeCount !== undefined) likeCount.value = result.data.likeCount
    authorId.value = result.data.author?.id || result.data.userId
  } else { error.value = result.message }
  loading.value = false
}

const updateCommentCount = (count) => { commentCount.value = count }
const handleNewComment = () => { if (commentListRef.value) setTimeout(() => { commentListRef.value.refreshComments() }, 300) }
const editArticle = () => router.push(`/edit-article/${route.params.id}`)

const deleteArticle = async () => {
  if (!confirm('确定要将此文章移至回收站吗？')) return
  deleting.value = true
  const r = await softDeleteArticle(route.params.id)
  if (r.success) { alert('文章已移至回收站'); router.push('/posts') }
  else { alert(r.message) }
  deleting.value = false
}

const toggleFav = async () => {
  if (!userStore.isAuthenticated) { router.push('/login'); return }
  favoriteLoading.value = true
  const r = await toggleFavorite(route.params.id)
  if (r.success) isFavorited.value = r.data.favorited ?? !isFavorited.value
  favoriteLoading.value = false
}

const toggleLike = async () => {
  if (!userStore.isAuthenticated) { router.push('/login'); return }
  if (likeLoading.value) return
  likeLoading.value = true
  isLiked.value = !isLiked.value
  likeCount.value += isLiked.value ? 1 : -1
  const r = await toggleArticleLike(route.params.id)
  if (!r.success) { isLiked.value = !isLiked.value; likeCount.value -= isLiked.value ? 1 : -1 }
  const countR = await getArticleLikeCount(route.params.id)
  if (countR.success) likeCount.value = countR.data.likeCount ?? likeCount.value
  likeLoading.value = false
}

const toggleFollow = async () => {
  if (!authorId.value || followLoading.value) return
  followLoading.value = true
  const r = isFollowing.value ? await unfollowUser(authorId.value) : await followUser(authorId.value)
  if (r.success) isFollowing.value = !isFollowing.value
  followLoading.value = false
}

const goBack = () => router.push('/')
const handleBack = () => router.go(-1)

onMounted(() => { loadArticle() })
</script>

<style scoped lang="scss">
@use '@/assets/styles/components/comment';
.article-detail-container { max-width: 800px; margin: 0 auto; padding: 0 20px; }
.back-button { margin-bottom: 24px; color: #3b82f6; cursor: pointer; font-size: 0.95rem; display: inline-flex; align-items: center; gap: 4px; }
.article-header { margin-bottom: 32px; }
.article-title { font-size: 2.2rem; font-weight: 700; line-height: 1.3; margin-bottom: 16px; color: #1f2937; }
.article-meta {
  .meta-info { display: flex; gap: 16px; color: #6b7280; font-size: 0.95rem; }
  .like-count { display: inline-flex; }
  .btn-like { background: none; border: none; cursor: pointer; font-size: 0.95rem; padding: 0; color: #6b7280; &:hover { color: #ef4444; } &.liked { color: #ef4444; } }
  .btn-follow { background: none; border: 1px solid #3b82f6; border-radius: 4px; padding: 2px 10px; font-size: 0.8rem; cursor: pointer; color: #3b82f6; white-space: nowrap; &:hover { background: #3b82f6; color: white; } &:disabled { opacity: 0.5; } }
  .admin-actions { display: flex; gap: 12px; }
  .btn-action { padding: 6px 16px; border: none; border-radius: 6px; font-size: 0.9rem; cursor: pointer; }
  .btn-edit { background: #dbeafe; color: #2563eb; &:hover { background: #bfdbfe; } }
  .btn-delete { background: #fee2e2; color: #dc2626; &:hover:not(:disabled) { background: #fecaca; } &:disabled { opacity: 0.6; cursor: not-allowed; } }
}
.article-actions { display: flex; gap: 8px; align-items: center; }
.btn-favorite { padding: 6px 14px; border: 1px solid #e5e7eb; border-radius: 6px; background: white; cursor: pointer; font-size: 0.9rem; &:hover:not(:disabled) { border-color: #f59e0b; background: #fffbeb; } &:disabled { opacity: 0.6; } &.favorited { border-color: #f59e0b; background: #fffbeb; } }
.article-content { margin-bottom: 60px; line-height: 1.7; color: #374151; }
.article-content :deep(img) { max-width: 100%; height: 80vh; width: auto; margin: 24px auto; border-radius: 8px; object-fit: contain; display: block; }
</style>
