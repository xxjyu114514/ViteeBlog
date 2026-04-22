<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div class="editor-container-wide">
      <div class="editor-header flex-between">
        <h1 class="title-large">{{ editingArticle ? '编辑文章' : '新建文章' }}</h1>
        <div class="editor-actions">
          <button class="btn-secondary" @click="goBack" :disabled="saving">返回</button>
          <button class="btn-primary" @click="handleSave" :disabled="saving || !canSave">
            {{ saving ? '保存中...' : '保存草稿' }}
          </button>
          <button 
            v-if="editingArticle && editingArticle.status === 'draft'"
            class="btn-publish" 
            @click="handlePublish"
            :disabled="saving || !canSave"
          >
            {{ publishing ? '发布中...' : '发布文章' }}
          </button>
        </div>
      </div>

      <div v-if="statusMessage" :class="['message-banner', isError ? 'error' : 'success']">
        {{ statusMessage }}
      </div>

      <div class="editor-form">
        <div class="form-group">
          <label>标题</label>
          <input 
            v-model="currentArticle.title" 
            type="text" 
            class="input-field"
            placeholder="请输入文章标题"
            :disabled="saving"
          >
        </div>
        
        <div class="flex-row gap-20">
          <div class="form-group flex-1">
            <label>分类ID</label>
            <input v-model="currentArticle.category_id" type="number" class="input-field" :disabled="saving">
          </div>
          <div class="form-group flex-2">
            <label>标签IDs（逗号分隔）</label>
            <input v-model="tagInput" type="text" class="input-field" placeholder="如：1,2,3" :disabled="saving">
          </div>
        </div>

        <div class="form-group">
          <label>内容 (支持拖拽/粘贴图片上传)</label>
          <div v-show="!editorLoadError" id="vditor-editor"></div>
          
          <textarea 
            v-if="editorLoadError" 
            v-model="currentArticle.content" 
            class="fallback-textarea"
            placeholder="高级编辑器加载失败，您可以使用普通文本模式编写..."
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useArticleAPI } from '@/composables/useArticleAPI'
import Vditor from 'vditor'
import 'vditor/dist/index.css'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { autoSaveArticle, publishArticle, getArticleDetail } = useArticleAPI()

// 后端基础配置
const BACKEND_URL = 'http://localhost:8000'

// 响应式状态
const currentArticle = ref({ title: '', content: '', category_id: null, tag_ids: [] })
const tagInput = ref('')
const saving = ref(false)
const publishing = ref(false)
const statusMessage = ref('')
const isError = ref(false)
const editingArticle = ref(null)
const editorLoadError = ref(false)
let vditorInstance = null

const canSave = computed(() => {
  return currentArticle.value.title.trim() !== '' && currentArticle.value.content.trim() !== ''
})

/**
 * 初始化编辑器
 */
const initVditor = (initialContent) => {
  if (vditorInstance) {
    vditorInstance.destroy()
  }

  vditorInstance = new Vditor('vditor-editor', {
    mode: 'ir', // 所见即所得模式
    height: 600,
    placeholder: '从这里开始创作...',
    value: initialContent || '',
    cache: { enable: false },
    toolbarConfig: { pin: true },
    // 注意：如果你的网络环境无法访问官方 CDN，可以重新开启并配置本地 cdn: '/vditor'
    
    upload: {
      url: `${BACKEND_URL}/api/v1/article/upload-image`,
      fieldName: 'file',
      max: 10 * 1024 * 1024,
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      },
      // 适配后端响应格式
      format: (files, responseText) => {
        try {
          const res = JSON.parse(responseText)
          const filename = res.filename || files[0].name
          return JSON.stringify({
            code: 0,
            msg: "",
            data: {
              errFiles: [],
              succMap: {
                [filename]: `${BACKEND_URL}${res.url}`
              }
            }
          })
        } catch (e) {
          return JSON.stringify({ code: 1, msg: "接口解析失败", data: { errFiles: [files[0].name] } })
        }
      },
      error: (msg) => {
        showStatus('图片上传失败: ' + msg, true)
      }
    },
    after: () => {
      editorLoadError.value = false
    },
    input: (val) => {
      currentArticle.value.content = val
    }
  })
}

/**
 * 消息提醒
 */
const showStatus = (msg, error = false) => {
  statusMessage.value = msg
  isError.value = error
  setTimeout(() => { statusMessage.value = '' }, 3000)
}

/**
 * 加载文章数据
 */
const loadArticleData = async () => {
  const articleId = route.params.id
  
  if (!articleId) {
    // 新建模式
    await nextTick()
    initVditor('')
    return
  }

  // 编辑模式
  const result = await getArticleDetail(articleId)
  if (result.success) {
    const info = result.data.info
    editingArticle.value = info
    currentArticle.value = {
      title: info.title,
      content: result.data.content || '',
      category_id: info.category?.id || null,
      tag_ids: info.tags?.map(t => t.id) || []
    }
    tagInput.value = currentArticle.value.tag_ids.join(',')
    
    await nextTick()
    initVditor(currentArticle.value.content)
  } else {
    showStatus('获取文章失败: ' + result.message, true)
    setTimeout(() => router.push('/personal'), 1500)
  }
}

/**
 * 保存逻辑
 */
const handleSave = async () => {
  if (!canSave.value) return
  
  saving.value = true
  
  // 处理标签
  const tag_ids = tagInput.value 
    ? tagInput.value.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
    : []

  const payload = {
    ...currentArticle.value,
    tag_ids,
    article_id: editingArticle.value?.id || null
  }

  const result = await autoSaveArticle(payload)
  if (result.success) {
    if (!editingArticle.value) {
      editingArticle.value = { id: result.data.article_id, status: 'draft' }
    }
    showStatus('已保存到草稿箱')
  } else {
    showStatus(result.message, true)
  }
  saving.value = false
}

const handlePublish = async () => {
  if (!editingArticle.value || publishing.value) return
  
  publishing.value = true
  const result = await publishArticle(editingArticle.value.id)
  if (result.success) {
    showStatus('发布成功！即将跳转...')
    setTimeout(() => router.push('/posts'), 1000)
  } else {
    showStatus(result.message, true)
  }
  publishing.value = false
}

const goBack = () => router.push('/personal')

onMounted(loadArticleData)

onUnmounted(() => {
  if (vditorInstance) {
    vditorInstance.destroy()
  }
})
</script>

<style scoped>
.editor-container-wide {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

#vditor-editor {
  width: 100%;
  min-height: 600px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

.editor-form {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.fallback-textarea {
  width: 100%;
  height: 600px;
  padding: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.message-banner {
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.message-banner.success {
  background-color: #f0fdf4;
  color: #166534;
  border-left: 4px solid #22c55e;
}

.message-banner.error {
  background-color: #fef2f2;
  color: #991b1b;
  border-left: 4px solid #ef4444;
}

.flex-row { display: flex; align-items: flex-end; }
.flex-1 { flex: 1; }
.flex-2 { flex: 2; }
.gap-20 { gap: 20px; }
.mb-20 { margin-bottom: 20px; }

/* 按钮基础样式（按需在全局 CSS 定义） */
.btn-publish {
  background-color: #8b5cf6;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
}
.btn-publish:hover { background-color: #7c3aed; }
.btn-publish:disabled { background-color: #c4b5fd; cursor: not-allowed; }
</style>