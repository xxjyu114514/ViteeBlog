<template>
  <div class="article-edit-page">
    <div class="glass-wrap">
      <div class="glass-card-editor" :class="{ 'slide-in': slidIn }">
        <!-- 头部 -->
        <div class="card-header">
          <span class="card-title">{{ editingArticle ? '编辑文章' : '新建文章' }}</span>
          <div class="header-actions">
            <button class="btn btn-primary" @click="handleSave" :disabled="saving || !canSave || isPending">
              {{ saving ? '保存中...' : '保存' }}
            </button>
            <button v-if="editingArticle && editingArticle.status === 'draft'" class="btn btn-accent" @click="handlePublish" :disabled="saving || !canSave || isPending">
              {{ publishing ? '发布中...' : '发布' }}
            </button>
            <button v-if="editingArticle && editingArticle.status === 'pending'" class="btn btn-outline" @click="handleWithdraw" :disabled="withdrawing">
              {{ withdrawing ? '撤回中...' : '撤回' }}
            </button>
            <button class="btn-drawer-toggle" @click="drawerOpen = !drawerOpen" :title="drawerOpen ? '关闭设置' : '打开设置'">
              {{ drawerOpen ? '▶' : '◀' }}
            </button>
          </div>
        </div>

        <!-- 消息 -->
        <div v-if="statusMessage" :class="['msg-banner', isError ? 'err' : 'ok']">{{ statusMessage }}</div>
        <div v-if="isPending" class="pending-notice"><span class="notice-icon">⚠️</span><span>文章正在审核中</span></div>

        <!-- 主体：编辑器 + 侧拉框 -->
        <div class="card-body">
          <div class="editor-main" :class="{ 'with-drawer': drawerOpen }">
            <div class="editor-area">
              <div class="form-group">
                <input v-model="currentArticle.title" class="input-title" placeholder="输入文章标题..." :disabled="saving || isPending">
              </div>
              <div class="editor-content">
                <div v-show="!editorLoadError" id="vditor-editor"></div>
                <textarea v-if="editorLoadError" v-model="currentArticle.content" class="form-textarea" placeholder="高级编辑器加载失败，请使用普通文本模式..." :disabled="isPending"></textarea>
              </div>
            </div>

            <!-- 侧拉框 -->
            <transition name="drawer-slide">
              <div v-if="drawerOpen" class="drawer-panel">
                <div class="drawer-section">
                  <label class="drawer-label">摘要</label>
                  <textarea v-model="currentArticle.summary" class="drawer-input drawer-textarea" placeholder="文章摘要（可选）" :disabled="saving || isPending" rows="3"></textarea>
                </div>
                <div class="drawer-section">
                  <label class="drawer-label">分类</label>
                  <select v-model="currentArticle.category_id" class="drawer-input drawer-select" :disabled="saving || loadingCategories || isPending">
                    <option value="">选择分类</option>
                    <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                  <div v-if="loadingCategories" class="load-hint">加载中...</div>
                </div>
                <div class="drawer-section">
                  <label class="drawer-label">标签</label>
                  <div class="drawer-tags">
                    <div v-for="tag in selectedTags" :key="tag.id" class="tag-pill" :class="{ disabled: isPending }">
                      {{ tag.name }}<span v-if="!isPending" class="tag-remove" @click="removeTag(tag.id)">×</span>
                    </div>
                  </div>
                  <select v-model="newTagId" class="drawer-input drawer-select" :disabled="saving || loadingTags || isPending" @change="addTag">
                    <option value="">+ 添加标签</option>
                    <option v-for="tag in availableTags" :key="tag.id" :value="tag.id" :disabled="selectedTags.some(t => t.id === tag.id)">{{ tag.name }}</option>
                  </select>
                  <div v-if="loadingTags" class="load-hint">加载中...</div>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Vditor from 'vditor'
import 'vditor/dist/index.css'
import { useUserStore } from '@/stores/user'
import { getArticleDetail, autoSaveArticle, publishArticle, withdrawArticle } from '@/services/articleService'
import { getCategories, getTags } from '@/services/metaService'
import { buildUrl } from '@/utils/apiUtils'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const BACKEND_BASE = API_BASE_URL.replace('/api/v1', '')
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const currentArticle = ref({ title: '', summary: '', content: '', category_id: null, tag_ids: [] })
const saving = ref(false)
const publishing = ref(false)
const withdrawing = ref(false)
const statusMessage = ref('')
const isError = ref(false)
const editingArticle = ref(null)
const editorLoadError = ref(false)
let vditorInstance = null
const categories = ref([])
const tags = ref([])
const loadingCategories = ref(true)
const loadingTags = ref(true)
const selectedTags = ref([])
const newTagId = ref('')
const slidIn = ref(false)
const drawerOpen = ref(false)

const canSave = computed(() => currentArticle.value.title.trim() !== '' && currentArticle.value.content.trim() !== '')
const isPending = computed(() => editingArticle.value?.status === 'pending')
const availableTags = computed(() => tags.value.filter(tag => !selectedTags.value.some(s => s.id === tag.id)))

const addTag = () => {
  if (newTagId.value && !selectedTags.value.some(t => t.id === parseInt(newTagId.value))) {
    const t = tags.value.find(t => t.id === parseInt(newTagId.value))
    if (t) {
      selectedTags.value.push({ id: t.id, name: t.name })
      if (!currentArticle.value.tag_ids.includes(t.id)) currentArticle.value.tag_ids.push(t.id)
    }
    newTagId.value = ''
  }
}
const removeTag = (tagId) => {
  selectedTags.value = selectedTags.value.filter(t => t.id !== tagId)
  currentArticle.value.tag_ids = currentArticle.value.tag_ids.filter(id => id !== tagId)
}

const fetchCategories = async () => {
  loadingCategories.value = true; const r = await getCategories()
  if (r.success) categories.value = r.data || []; loadingCategories.value = false
}
const fetchTags = async () => {
  loadingTags.value = true; const r = await getTags()
  if (r.success) tags.value = r.data || []; loadingTags.value = false
}

const initVditor = (initialContent) => {
  if (vditorInstance) vditorInstance.destroy()
  vditorInstance = new Vditor('vditor-editor', {
    mode: 'ir', height: 600, placeholder: '从这里开始创作...',
    value: initialContent || '', cache: { enable: false },
    toolbarConfig: { pin: true },
    upload: {
      url: API_BASE_URL + buildUrl('/article/upload-image'),
      fieldName: 'file', max: 10 * 1024 * 1024,
      setHeaders: () => { const s = useUserStore(); return { Authorization: `Bearer ${s.token}` } },
      format: (files, responseText) => {
        try { const r = JSON.parse(responseText); return JSON.stringify({ code: 0, msg: '', data: { errFiles: [], succMap: { [r.filename || files[0].name]: `${BACKEND_BASE}${r.url}` } } }) }
        catch { return JSON.stringify({ code: 1, msg: '解析失败', data: { errFiles: [files[0].name] } }) }
      },
      error: (msg) => showStatus('图片上传失败: ' + msg, true),
    },
    after: () => { editorLoadError.value = false },
    input: (val) => { currentArticle.value.content = val },
  })
}

const showStatus = (msg, error = false) => { statusMessage.value = msg; isError.value = error; setTimeout(() => { statusMessage.value = '' }, 3000) }

const loadArticleData = async () => {
  const articleId = route.params.id
  const isInvalidId = !articleId || articleId === 'undefined' || articleId === 'null' || articleId === ''
  await Promise.all([fetchCategories(), fetchTags()])
  if (isInvalidId) { await nextTick(); initVditor(''); return }
  const result = await getArticleDetail(articleId)
  if (result.success) {
    const info = result.data; editingArticle.value = info
    // 文章内容直接由 API 返回（最新后端将 content 存储在数据库）
    currentArticle.value = { title: info.title, content: info.content || '', category_id: info.category?.id || null, tag_ids: info.tags?.map(t => t.id) || [] }
    if (info.tags) selectedTags.value = info.tags.map(tag => ({ id: tag.id, name: tag.name }))
    await nextTick(); initVditor(currentArticle.value.content)
  } else { showStatus('获取文章失败: ' + result.message, true); setTimeout(() => router.push('/personal'), 1500) }
}

const handleSave = async () => {
  if (!canSave.value || isPending.value) return
  if (!currentArticle.value.content?.trim()) { showStatus('文章内容不能为空', true); return }
  saving.value = true
  const payload = { ...currentArticle.value, id: editingArticle.value?.id || null }
  const r = await autoSaveArticle(payload)
  if (r.success) { if (!editingArticle.value) editingArticle.value = { id: r.data.id, status: 'draft' }; showStatus('已保存到草稿箱') }
  else showStatus(r.message, true)
  saving.value = false
}

const handlePublish = async () => {
  if (!editingArticle.value || publishing.value || isPending.value) return
  publishing.value = true
  const r = await publishArticle(editingArticle.value.id)
  if (r.success) { showStatus('发布成功！'); setTimeout(() => router.push('/posts'), 1000) }
  else showStatus(r.message, true)
  publishing.value = false
}

const handleWithdraw = async () => {
  if (!editingArticle.value || withdrawing.value || editingArticle.value.status !== 'pending') return
  if (!confirm('确定要撤回这篇文章吗？')) return
  withdrawing.value = true
  const r = await withdrawArticle(editingArticle.value.id)
  if (r.success) { showStatus('已撤回至草稿状态'); editingArticle.value.status = 'draft' }
  else showStatus(r.message, true)
  withdrawing.value = false
}

onMounted(() => { loadArticleData(); requestAnimationFrame(() => { slidIn.value = true }) })
onUnmounted(() => { if (vditorInstance) vditorInstance.destroy() })
</script>

<style lang="scss">
@use 'sass:color';
@use '../_design.scss' as *;

.article-edit-page {
  position: fixed; inset: 0; z-index: 1;
  overflow: hidden;
}

.glass-wrap {
  position: absolute; bottom: 0; left: $space-lg; right: $space-lg;
  height: calc(100vh - 90px - 5vh); display: flex; flex-direction: column;
}

.glass-card-editor {
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
  // .btn-back 5df2572851685c40 views.scss 4e2d5b9a4e49
  .card-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; flex: 1; }
  .header-actions { display: flex; align-items: center; gap: $space-sm; }
}

.btn-drawer-toggle {
  background: $bg-hover; border: 1px solid $glass-border; color: $text-secondary;
  cursor: pointer; padding: $space-2xs $space-sm; font-size: 0.8rem; transition: all 0.2s;
  &:hover { color: $text-primary; border-color: $color-primary; }
}

.msg-banner { padding: 10px $space-xl; font-size: 0.85rem; flex-shrink: 0; &.ok { background: rgba($color-success, 0.15); color: $color-success; } &.err { background: rgba($color-error, 0.15); color: $color-error; } }
.pending-notice { display: flex; align-items: center; gap: 8px; padding: 10px $space-xl; flex-shrink: 0; background: rgba($color-warning, 0.12); color: $color-warning; font-size: 0.85rem; .notice-icon { font-size: 1rem; } }

.card-body { flex: 1; overflow: hidden; }

// 主编辑器区域
.editor-main {
  display: flex; height: 100%;
}

.editor-area {
  flex: 1; display: flex; flex-direction: column; padding: $space-lg;
  overflow: hidden;
  transition: flex 0.3s ease;
}

.input-title {
  width: 100%; padding: 14px 16px; font-size: 1.3rem; font-weight: 600;
  background: transparent; border: none; border-bottom: 1px solid $glass-border;
  color: $text-primary; outline: none; margin-bottom: $space-md;
  &::placeholder { color: $text-tertiary; }
  &:focus { border-bottom-color: $color-primary; }
}

.editor-content { flex: 1; overflow-y: auto; }

// 侧拉框
.drawer-panel {
  width: 16vw; min-width: 200px; max-width: 320px;
  background: $bg-surface; border-left: 1px solid $glass-border;
  padding: $space-lg; overflow-y: auto;
  flex-shrink: 0;
}

.drawer-slide-enter-active, .drawer-slide-leave-active {
  transition: width 0.3s ease, opacity 0.3s ease, padding 0.3s ease;
}
.drawer-slide-enter-from, .drawer-slide-leave-to {
  width: 0 !important; min-width: 0 !important; padding: $space-lg 0; opacity: 0; overflow: hidden;
}

.drawer-section { margin-bottom: $space-lg; }
.drawer-label { display: block; font-family: $font-mono; font-size: 0.75rem; color: $text-secondary; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em; }
.drawer-input {
  width: 100%; padding: 8px 10px; background: $bg-elevated; border: 1px solid $glass-border;
  color: $text-primary; font-size: 0.85rem; box-sizing: border-box;
  &:focus { outline: none; border-color: $color-primary; }
}
.drawer-textarea { resize: vertical; min-height: 60px; font-family: $font-sans; }
.drawer-select { cursor: pointer; option { background: $bg-surface; color: $text-primary; } }
.drawer-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 6px; }

.tag-pill {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 3px 8px; background: $bg-hover; border: 1px solid $glass-border;
  color: $text-primary; font-size: 0.78rem;
  &.disabled { opacity: 0.5; }
}
.tag-remove { cursor: pointer; color: $text-tertiary; margin-left: 2px; &:hover { color: $color-error; } }

.load-hint { font-size: 0.75rem; color: $text-tertiary; margin-top: 4px; }

.form-textarea {
  width: 100%; min-height: 300px; padding: 12px; background: $bg-elevated; border: 1px solid $glass-border;
  color: $text-primary; font-size: 0.95rem; font-family: $font-mono; box-sizing: border-box;
  &:focus { outline: none; border-color: $color-primary; }
}
</style>
