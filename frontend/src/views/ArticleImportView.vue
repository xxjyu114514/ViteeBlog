<template>
  <div class="import-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <span class="card-title">文章导入</span>
        </div>
        <div class="card-body">
          <!-- 单篇导入 -->
          <div class="import-section">
            <h3 class="section-title">单篇导入</h3>
            <p class="section-desc">上传 .txt、.md 或 .docx 文件，自动提取标题并创建草稿</p>
            <div class="upload-area">
              <input ref="singleInputRef" type="file" accept=".txt,.md,.docx" style="display:none" @change="handleSingleImport" />
              <button class="btn btn-primary" :disabled="singleLoading" @click="singleInputRef?.click()">
                {{ singleLoading ? '导入中...' : '选择文件' }}
              </button>
              <span v-if="singleFileName" class="file-name">{{ singleFileName }}</span>
            </div>
            <div v-if="singleMsg" :class="['msg', singleOk ? 'ok' : 'err']">{{ singleMsg }}</div>
            <div v-if="singleResult" class="result-box">
              文章已导入：<router-link :to="`/edit-article/${singleResult.articleId}`" class="result-link">{{ singleResult.title }}</router-link>
              <span class="result-hint">（草稿状态，可前往编辑发布）</span>
            </div>
          </div>

          <div class="divider"></div>

          <!-- 批量导入 -->
          <div class="import-section">
            <h3 class="section-title">批量导入</h3>
            <p class="section-desc">一次选择多个文件，批量创建文章草稿</p>
            <div class="upload-area">
              <input ref="batchInputRef" type="file" accept=".txt,.md,.docx" multiple style="display:none" @change="handleBatchImport" />
              <button class="btn btn-primary" :disabled="batchLoading" @click="batchInputRef?.click()">
                {{ batchLoading ? '导入中...' : '选择多个文件' }}
              </button>
              <span v-if="batchFileCount > 0" class="file-name">已选 {{ batchFileCount }} 个文件</span>
            </div>
            <div v-if="batchMsg" :class="['msg', batchOk ? 'ok' : 'err']">{{ batchMsg }}</div>
            <div v-if="batchResult && batchResult.length > 0" class="result-list">
              <div v-for="item in batchResult" :key="item.articleId" class="result-item">
                <router-link :to="`/edit-article/${item.articleId}`" class="result-link">{{ item.title }}</router-link>
              </div>
            </div>
          </div>

          <div class="divider"></div>

          <!-- 批量上传图片 -->
          <div class="import-section">
            <h3 class="section-title">批量上传图片</h3>
            <p class="section-desc">上传 .zip 压缩包，自动解压并上传所有图片到图床</p>
            <div class="upload-area">
              <input ref="zipInputRef" type="file" accept=".zip" style="display:none" @change="handleZipUpload" />
              <button class="btn btn-primary" :disabled="zipLoading" @click="zipInputRef?.click()">
                {{ zipLoading ? '上传中...' : '选择 ZIP 文件' }}
              </button>
              <span v-if="zipFileName" class="file-name">{{ zipFileName }}</span>
            </div>
            <div v-if="zipMsg" :class="['msg', zipOk ? 'ok' : 'err']">{{ zipMsg }}</div>
            <div v-if="zipUrls && zipUrls.length > 0" class="result-box">
              <p>成功上传 {{ zipUrls.length }} 张图片</p>
              <div class="url-list">
                <div v-for="(url, i) in zipUrls" :key="i" class="url-item" @click="copyText(url)">{{ url }}</div>
              </div>
              <p class="copy-hint">点击链接可复制</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { importSingleArticle, importBatchArticles, batchUploadImages } from '@/services/articleService'

const router = useRouter()
const slidIn = ref(false)
const goBack = () => router.push('/manage-articles')

// 单篇导入
const singleInputRef = ref(null)
const singleLoading = ref(false)
const singleFileName = ref('')
const singleMsg = ref('')
const singleOk = ref(false)
const singleResult = ref(null)

const handleSingleImport = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  singleFileName.value = file.name
  singleMsg.value = ''
  singleResult.value = null
  singleLoading.value = true
  const r = await importSingleArticle(file)
  if (r.success && r.data) {
    singleMsg.value = '导入成功！'
    singleOk.value = true
    singleResult.value = r.data
  } else {
    singleMsg.value = r.message || '导入失败'
    singleOk.value = false
  }
  singleLoading.value = false
  e.target.value = ''
}

// 批量导入
const batchInputRef = ref(null)
const batchLoading = ref(false)
const batchFileCount = ref(0)
const batchMsg = ref('')
const batchOk = ref(false)
const batchResult = ref(null)

const handleBatchImport = async (e) => {
  const files = e.target.files
  if (!files || files.length === 0) return
  batchFileCount.value = files.length
  batchMsg.value = ''
  batchResult.value = null
  batchLoading.value = true
  const r = await importBatchArticles(Array.from(files))
  if (r.success && r.data) {
    batchMsg.value = `成功导入 ${r.data.success || 0} 篇，共提交 ${r.data.total || 0} 个文件`
    batchOk.value = true
    batchResult.value = r.data.articles || []
  } else {
    batchMsg.value = r.message || '批量导入失败'
    batchOk.value = false
  }
  batchLoading.value = false
  e.target.value = ''
}

// 批量上传图片
const zipInputRef = ref(null)
const zipLoading = ref(false)
const zipFileName = ref('')
const zipMsg = ref('')
const zipOk = ref(false)
const zipUrls = ref(null)

const handleZipUpload = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  zipFileName.value = file.name
  zipMsg.value = ''
  zipUrls.value = null
  zipLoading.value = true
  const r = await batchUploadImages(file)
  if (r.success && r.data) {
    zipMsg.value = `上传完成！成功处理 ${r.data.success || 0} 张图片`
    zipOk.value = true
    zipUrls.value = r.data.urls || []
  } else {
    zipMsg.value = r.message || '上传失败'
    zipOk.value = false
  }
  zipLoading.value = false
  e.target.value = ''
}

const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('已复制到剪贴板')
  } catch {
    prompt('手动复制链接：', text)
  }
}

requestAnimationFrame(() => { slidIn.value = true })
</script>

<style lang="scss">
@use 'sass:color';
@use './_design.scss' as *;

.import-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }

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
  // .btn-back 5df2572851685c40 views.scss 4e2d5b9a4e49
  .card-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; flex: 1; }
}

.card-body { flex: 1; overflow-y: auto; padding: $space-xl; }

.import-section { margin-bottom: $space-lg; }
.section-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; margin-bottom: 4px; }
.section-desc { font-size: 0.85rem; color: $text-tertiary; margin-bottom: $space-md; }

.upload-area { display: flex; align-items: center; gap: $space-sm; }
.file-name { font-size: 0.85rem; color: $text-secondary; }

.msg { padding: 10px 14px; font-size: 0.85rem; margin-top: $space-sm; }
.msg.ok { background: rgba($color-success, 0.12); color: $color-success; }
.msg.err { background: rgba($color-error, 0.12); color: $color-error; }

.result-box { margin-top: $space-md; padding: $space-md; background: $bg-surface; font-size: 0.9rem; }
.result-link { color: $color-primary; text-decoration: none; font-weight: 500; &:hover { text-decoration: underline; } }
.result-hint { color: $text-tertiary; font-size: 0.8rem; margin-left: 8px; }

.result-list { margin-top: $space-md; display: flex; flex-direction: column; gap: 6px; }
.result-item { padding: 8px 12px; background: $bg-surface; font-size: 0.9rem; }

.url-list { display: flex; flex-direction: column; gap: 4px; margin-top: $space-sm; }
.url-item {
  padding: 6px 10px; background: $bg-elevated; font-size: 0.8rem;
  color: $color-primary; cursor: pointer; word-break: break-all;
  &:hover { background: $bg-hover; }
}
.copy-hint { font-size: 0.75rem; color: $text-tertiary; margin-top: 4px; }

.divider { height: 1px; background: $glass-border; margin: $space-lg 0; }

.btn { padding: 8px 20px; border: none; cursor: pointer; font-size: 0.9rem; font-weight: 500; }
.btn-primary { background: $color-primary; color: $bg-base; &:hover { background: color.adjust($color-primary, $lightness: 8%); } &:disabled { opacity: 0.5; cursor: not-allowed; } }
</style>
