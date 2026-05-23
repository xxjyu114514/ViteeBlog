<template>
  <Teleport to="body">
    <div v-if="show" class="audit-modal-overlay" @click="close">
      <div class="audit-modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">审核文章</h3>
          <button class="modal-close" @click="close">&times;</button>
        </div>

        <div class="modal-body">
          <!-- 文章预览区域 -->
          <div class="preview-section">
            <h4 class="preview-title">文章预览</h4>

            <div v-if="loadingArticle" class="preview-loading">
              <div class="loading-spinner"></div>
              <p>加载文章内容中...</p>
            </div>

            <div v-else-if="articleData" class="preview-content">
              <div class="preview-header">
                <h3 class="preview-article-title">{{ articleData.title || '[无标题]' }}</h3>
                <div class="preview-meta">
                  <span v-if="articleData.author">作者：{{ articleData.author.username }}</span>
                  <span>提交时间：{{ formatDateTime(articleData.submittedAt || articleData.createdAt) }}</span>
                  <span v-if="articleData.category">分类：{{ articleData.category.name }}</span>
                </div>
              </div>
              <div class="preview-summary" v-if="articleData.summary">
                <strong>摘要：</strong>{{ articleData.summary }}
              </div>
              <div class="preview-content-area">
                <h5>文章内容：</h5>
                <div class="markdown-content" v-html="renderedPreview"></div>
              </div>
            </div>

            <div v-else class="preview-error">
              <p>无法加载文章预览</p>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">审核结果:</label>
            <div class="radio-group">
              <label class="radio-option">
                <input type="radio" v-model="passAudit" :value="true" />
                <span class="radio-text">✅ 通过审核</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="passAudit" :value="false" />
                <span class="radio-text">❌ 驳回文章</span>
              </label>
            </div>
          </div>

          <div v-if="!passAudit" class="form-group">
            <label class="form-label">驳回原因:</label>
            <textarea
              v-model="remark"
              class="textarea-field"
              placeholder="请输入驳回原因..."
              rows="4"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <div class="modal-actions">
            <button class="btn-secondary" @click="close">取消</button>
            <button
              class="btn-primary"
              @click="handleAudit"
              :disabled="submitting"
            >
              {{ submitting ? '审核中...' : '确认审核' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { getArticleDetail, reviewArticle, loadArticleContent } from '@/services/articleService'
import { formatDateTime, renderMarkdown } from '@/utils'

const props = defineProps({
  show: { type: Boolean, default: false },
  articleId: { type: [Number, String], default: null },
})

const emit = defineEmits(['update:show', 'audit-success'])

const articleData = ref(null)
const loadingArticle = ref(false)
const passAudit = ref(true)
const remark = ref('')
const submitting = ref(false)

const renderedPreview = computed(() => {
  if (!articleData.value?.content) return ''
  return renderMarkdown(articleData.value.content)
})

const close = () => {
  emit('update:show', false)
}

const loadData = async (articleId) => {
  if (!articleId) return
  loadingArticle.value = true
  articleData.value = null
  passAudit.value = true
  remark.value = ''

  const result = await getArticleDetail(articleId)
  if (result.success) {
    const info = result.data
    let contentToLoad = ''
    if (info.contentPath) {
      const contentResult = await loadArticleContent(info.contentPath)
      contentToLoad = contentResult.success ? contentResult.data : '[内容加载失败]'
    }
    articleData.value = {
      ...info,
      content: contentToLoad || info.summary || '[无内容]',
    }
  } else {
    alert('加载文章详情失败：' + result.message)
  }
  loadingArticle.value = false
}

const handleAudit = async () => {
  if (!props.articleId || submitting.value) return
  submitting.value = true
  try {
    const result = await reviewArticle(props.articleId, {
      pass_audit: passAudit.value,
      remark: remark.value,
    })
    if (result.success) {
      emit('audit-success')
      close()
    } else {
      alert(result.message || '审核操作失败')
    }
  } catch (error) {
    console.error('审核文章异常:', error)
    alert('审核操作失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

watch(() => props.show, (val) => {
  if (val && props.articleId) {
    loadData(props.articleId)
  }
})
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.audit-modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.audit-modal-content {
  background: $bg-white;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  .modal-title {
    font-size: 1.25rem;
    font-weight: 600;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: $text-secondary;

    &:hover { color: $color-primary; }
  }
}

.preview-section {
  margin-bottom: 20px;

  .preview-title {
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 16px;
  }

  .preview-loading {
    text-align: center;
    padding: 20px;
    
    .loading-spinner {
      width: 32px; height: 32px;
      border: 4px solid rgba($color-primary, 0.1);
      border-top: 4px solid $color-primary;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 10px;
    }
  }

  .preview-header {
    margin-bottom: 15px;

    .preview-article-title {
      margin: 0 0 8px;
      font-size: 1.3rem;
      color: $text-main;
      font-weight: 600;
    }
    .preview-meta {
      display: flex; gap: 15px;
      color: $text-secondary;
      font-size: 0.85rem; flex-wrap: wrap;
    }
  }

  .preview-summary {
    margin-bottom: 15px;
    padding: 12px;
    background: $bg-smoke;
    border-radius: 8px;
    font-size: 0.95rem;
    line-height: 1.5;
  }

  .preview-content-area {
    h5 { margin: 0 0 10px; color: $text-main; }
    
    :deep(.markdown-content) {
      font-size: 0.95rem; line-height: 1.6;
      max-height: 300px; overflow-y: auto; padding: 10px 0;
      color: $text-main;
      p { margin: 8px 0; }
      h1, h2, h3, h4 { margin: 16px 0 8px; }
      code { background: $bg-smoke; padding: 2px 4px; border-radius: 4px; }
      pre { background: $bg-smoke; padding: 12px; border-radius: 8px; overflow-x: auto; }
      blockquote { border-left: 4px solid $color-primary; padding-left: 16px; color: $text-secondary; margin: 12px 0; }
      ul, ol { margin: 12px 0; padding-left: 20px; }
      a { color: $color-primary; text-decoration: underline; }
      img { max-width: 100%; height: auto; margin: 12px 0; }
    }
  }

  .preview-error p { color: $color-danger; }
}

.form-group {
  margin-bottom: 16px;
  
  .form-label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 8px; color: $text-main; }
  
  .radio-group {
    display: flex; gap: 16px;
    .radio-option { display: flex; align-items: center; cursor: pointer; }
  }
  
  .textarea-field {
    width: 100%; padding: 12px;
    border: 1px solid $border-color-light;
    border-radius: 8px; font-size: 0.875rem;
    color: $text-secondary; resize: vertical; box-sizing: border-box;
  }
}

.modal-footer {
  .modal-actions {
    display: flex; justify-content: flex-end; gap: 16px;
    
    .btn-secondary {
      padding: 8px 16px; background: rgba($text-secondary, 0.1);
      color: $text-secondary; border-radius: 8px; font-weight: 500;
      border: none; cursor: pointer; transition: all 0.2s ease;
      &:hover { background: rgba($text-secondary, 0.2); }
    }
    
    .btn-primary {
      padding: 8px 16px; background: $color-primary;
      color: white; border-radius: 8px; font-weight: 500;
      border: none; cursor: pointer; transition: all 0.2s ease;
      &:hover { background: $color-primary-hover; }
      &:disabled { opacity: 0.6; cursor: not-allowed; }
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
