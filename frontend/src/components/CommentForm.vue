<template>
  <div class="comment-form">
    <div class="form-header">
      <h3 class="title">发表评论</h3>
      <p class="subtitle">分享您的想法和观点</p>
    </div>

    <div class="md-toolbar" v-if="userStore.isAuthenticated">
      <button type="button" class="toolbar-btn" @click="insertMarkdown('**', '**')" title="粗体"><b>B</b></button>
      <button type="button" class="toolbar-btn" @click="insertMarkdown('*', '*')" title="斜体"><i>I</i></button>
      <button type="button" class="toolbar-btn" @click="insertMarkdown('[', '](url)')" title="链接">🔗</button>
      <button type="button" class="toolbar-btn" @click="insertMarkdown('`', '`')" title="行内代码"><code>&lt;/&gt;</code></button>
      <button type="button" class="toolbar-btn" @click="insertMarkdown('```\n', '\n```')" title="代码块">📦</button>
      <button type="button" class="toolbar-btn" @click="insertMarkdown('- ', '')" title="无序列表">•</button>
      <button type="button" class="toolbar-btn" @click="insertMarkdown('> ', '')" title="引用">❝</button>
      <span class="toolbar-spacer"></span>
      <button type="button" class="toolbar-btn" :class="{ active: showPreview }" @click="showPreview = !showPreview">{{ showPreview ? '编辑' : '预览' }}</button>
    </div>

    <textarea
      v-if="!showPreview"
      v-model="commentContent"
      class="form-input"
      placeholder="写下您的评论...&#10;&#10;支持 Markdown 语法"
      :disabled="loading || !userStore.isAuthenticated"
      @input="clearError"
    ></textarea>

    <div v-else class="preview-area">
      <div class="preview-content" v-html="renderedPreview"></div>
    </div>

    <div class="form-actions">
      <span class="char-count">{{ commentContent.length }} / 1000</span>
      <button class="btn-submit" @click="handleSubmit" :disabled="!canSubmit || loading">
        {{ loading ? '提交中...' : '发表评论' }}
      </button>
    </div>

    <div v-if="error" class="form-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { createComment as createCommentApi } from '@/services/commentService'
import { renderMarkdown } from '@/utils'

const props = defineProps({
  articleId: { type: [String, Number], required: true },
})

const emit = defineEmits(['comment-submitted'])

const userStore = useUserStore()
const commentContent = ref('')
const loading = ref(false)
const error = ref(null)
const showPreview = ref(false)

const canSubmit = computed(() => {
  return commentContent.value.trim().length > 0 && commentContent.value.trim().length <= 1000
})

const renderedPreview = computed(() => {
  if (!commentContent.value) return '<p style="color:#999;">暂无内容</p>'
  return renderMarkdown(commentContent.value)
})

const clearError = () => { error.value = null }

const insertMarkdown = (before, after) => {
  const textarea = document.querySelector('.form-input')
  if (!textarea) return
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selected = commentContent.value.substring(start, end)
  const insertion = before + selected + after
  commentContent.value = commentContent.value.substring(0, start) + insertion + commentContent.value.substring(end)
  nextTick(() => {
    textarea.focus()
    textarea.selectionStart = textarea.selectionEnd = start + insertion.length
  })
}

const handleSubmit = async () => {
  if (!canSubmit.value || loading.value) return
  if (!userStore.isAuthenticated) { error.value = '请先登录后再发表评论'; return }
  loading.value = true; error.value = null
  try {
    const result = await createCommentApi(props.articleId, { content: commentContent.value.trim() })
    if (result.success) {
      commentContent.value = ''; showPreview.value = false
      emit('comment-submitted', result.data)
    } else {
      error.value = result.message || '发表评论失败，请稍后重试'
    }
  } catch (err) {
    error.value = '网络错误，请检查网络连接后重试'
  } finally { loading.value = false }
}
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;
@use '@/assets/styles/components/comment';

.form-error { margin-top: 12px; color: $color-error; font-size: 0.9rem; }

.md-toolbar {
  display: flex; align-items: center; gap: 4px; margin-bottom: 8px; flex-wrap: wrap;
  .toolbar-btn {
    padding: 4px 8px; border: 1px solid $border-white-light;
    background: $bg-surface; cursor: pointer; font-size: 0.85rem; line-height: 1.4;
    transition: background 0.15s; color: $text-primary;
    &:hover { background: $bg-hover; }
    &.active { background: rgba($color-primary, 0.12); border-color: $color-primary; color: $color-primary; }
    code { font-size: 0.8rem; }
  }
  .toolbar-spacer { flex: 1; }
}

.form-input {
  width: 100%; min-height: 100px; padding: 12px;
  border: 1px solid $border-white-light;
  font-size: 0.95rem; line-height: 1.6; resize: vertical;
  font-family: inherit; box-sizing: border-box;
  background: $bg-elevated; color: $text-primary;
  &:focus { outline: none; border-color: $color-primary; }
}

.preview-area {
  border: 1px solid $border-white-subtle; padding: 12px;
  min-height: 100px; background: $bg-surface;
  .preview-content { font-size: 0.95rem; line-height: 1.6; color: $text-primary; }
}

.form-actions {
  display: flex; justify-content: space-between; align-items: center; margin-top: 12px;
  .char-count { font-size: 0.8rem; color: $text-tertiary; }
}
</style>
