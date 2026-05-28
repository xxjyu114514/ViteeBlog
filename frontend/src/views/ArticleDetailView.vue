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
@use 'sass:color';
@use '@/assets/styles/variables' as *;
@use '@/assets/styles/components/comment';

.article-detail-container { max-width: 800px; margin: 0 auto; padding: 0 20px; }

.back-button {
  margin-bottom: 24px; color: $color-primary; cursor: pointer; font-size: 0.95rem;
  display: inline-flex; align-items: center; gap: 4px;
  &:hover { color: color.adjust($color-primary, $lightness: 8%); }
}

.article-header { margin-bottom: 32px; }

.article-title {
  font-size: 2.2rem; font-weight: 700; line-height: 1.3;
  margin-bottom: 16px; color: $text-primary;
}

.article-meta {
  .meta-info {
    display: flex; gap: 16px; color: $text-secondary; font-size: 0.95rem;
    flex-wrap: wrap;
  }
  .like-count { display: inline-flex; }
  .btn-like {
    background: none; border: none; cursor: pointer; font-size: 0.95rem;
    padding: 0; color: $text-secondary;
    &:hover { color: $color-error; }
    &.liked { color: $color-error; }
    &:disabled { opacity: 0.5; }
  }
  .btn-follow {
    background: none; border: 1px solid $color-primary;
    padding: 2px 10px; font-size: 0.8rem; cursor: pointer;
    color: $color-primary; white-space: nowrap;
    &:hover { background: $color-primary; color: $bg-base; }
    &:disabled { opacity: 0.5; }
  }
  .admin-actions { display: flex; gap: 12px; }
  .btn-action {
    padding: 6px 16px; border: none; font-size: 0.9rem; cursor: pointer;
  }
  .btn-edit {
    background: rgba($color-primary, 0.12); color: $color-primary;
    &:hover { background: rgba($color-primary, 0.2); }
  }
  .btn-delete {
    background: rgba($color-error, 0.12); color: $color-error;
    &:hover:not(:disabled) { background: rgba($color-error, 0.2); }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}

.article-actions { display: flex; gap: 8px; align-items: center; }

.btn-favorite {
  padding: 6px 14px; border: 1px solid $border-white-light;
  background: $bg-surface; cursor: pointer; font-size: 0.9rem; color: $text-primary;
  &:hover:not(:disabled) { border-color: $color-warning; background: rgba($color-warning, 0.1); }
  &:disabled { opacity: 0.6; }
  &.favorited { border-color: $color-warning; background: rgba($color-warning, 0.1); }
}

/* === 文章正文（核心修复：文字颜色+加粗效果） === */
.article-content {
  margin-bottom: 60px;
  line-height: 1.7;
  font-size: 1.05rem;
  color: $text-primary;

  /* 加粗修复 */
  :deep(strong),
  :deep(b) {
    font-weight: 700;
    color: $text-primary;
  }

  :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
    font-weight: 600;
    color: $text-primary;
    margin-top: 32px;
    margin-bottom: 16px;
  }
  :deep(h1) { font-size: 1.8rem; }
  :deep(h2) { font-size: 1.5rem; }
  :deep(h3) { font-size: 1.3rem; }

  :deep(p) { margin-bottom: 20px; }

  :deep(a) {
    color: $color-primary;
    text-decoration: none;
    &:hover { text-decoration: underline; }
  }

  :deep(img) {
    max-width: 100%; height: 80vh; width: auto;
    margin: 24px auto; object-fit: contain; display: block;
  }

  :deep(blockquote) {
    margin: 20px 0; padding: 16px 24px;
    border-left: 4px solid $color-primary;
    background: rgba($color-primary, 0.05);
    color: $text-secondary;
    font-style: italic;
  }

  :deep(code) {
    padding: 2px 6px;
    background: $bg-hover;
    font-family: $font-mono;
    font-size: 0.9em;
    color: $color-accent;
  }

  :deep(pre) {
    margin: 20px 0; padding: 20px;
    background: $bg-elevated;
    overflow-x: auto;
    code { background: none; padding: 0; color: $text-primary; font-size: 0.95em; }
  }

  :deep(ul), :deep(ol) {
    margin: 20px 0; padding-left: 30px;
    li { margin-bottom: 8px; line-height: 1.6; }
  }

  :deep(table) {
    width: 100%; border-collapse: collapse; margin: 20px 0;
    th, td { padding: 12px; border: $border-white-subtle; text-align: left; }
    th { background: $bg-surface; font-weight: 600; }
  }

  :deep(hr) {
    border: none; border-top: $divider-emphasis; margin: 32px 0;
  }
}
</style>
