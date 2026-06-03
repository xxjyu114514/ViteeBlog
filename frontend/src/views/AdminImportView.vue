<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div class="container-narrow">
      <div class="back-button" @click="router.go(-1)">← 返回</div>
      <h1 class="page-title">导入管理</h1>

      <!-- 单篇导入 -->
      <section class="import-section card">
        <h2 class="section-title">单篇导入</h2>
        <p class="section-desc">上传 .md / .txt / .docx 文件，自动解析为文章草稿</p>
        <div class="upload-area">
          <input ref="singleInput" type="file" accept=".md,.txt,.docx" hidden @change="onSingleFile" />
          <button class="btn" :class="singleLoading ? 'btn-disabled' : 'btn-primary'" @click="singleInput.click()" :disabled="singleLoading">
            {{ singleLoading ? '导入中...' : '选择文件并导入' }}
          </button>
          <span v-if="singleMsg" :class="['msg', singleOk ? 'msg-ok' : 'msg-err']">{{ singleMsg }}</span>
        </div>
      </section>

      <!-- 批量导入 -->
      <section class="import-section card">
        <h2 class="section-title">批量导入</h2>
        <p class="section-desc">一次选择多个 .md / .txt / .docx 文件</p>
        <div class="upload-area">
          <input ref="batchInput" type="file" multiple accept=".md,.txt,.docx" hidden @change="onBatchFiles" />
          <button class="btn" :class="batchLoading ? 'btn-disabled' : 'btn-primary'" @click="batchInput.click()" :disabled="batchLoading">
            {{ batchLoading ? '导入中...' : '选择多个文件' }}
          </button>
          <div v-if="batchResult" class="batch-result">
            <p :class="batchResult.success > 0 ? 'msg-ok' : 'msg-err'">
              成功 {{ batchResult.success }} / {{ batchResult.total }} 篇
            </p>
            <p v-for="(f, i) in batchResult.failed" :key="i" class="msg-err">❌ {{ f.filename }}: {{ f.reason }}</p>
          </div>
        </div>
      </section>

      <!-- ZIP 批量上传图片 -->
      <section class="import-section card">
        <h2 class="section-title">批量上传图片（ZIP）</h2>
        <p class="section-desc">上传 ZIP 压缩包，自动解压并上传所有图片</p>
        <div class="upload-area">
          <input ref="zipInput" type="file" accept=".zip" hidden @change="onZipFile" />
          <button class="btn" :class="zipLoading ? 'btn-disabled' : 'btn-accent'" @click="zipInput.click()" :disabled="zipLoading">
            {{ zipLoading ? '上传中...' : '选择 ZIP 文件' }}
          </button>
          <div v-if="zipResult" class="batch-result">
            <p :class="zipResult.success > 0 ? 'msg-ok' : 'msg-err'">
              成功上传 {{ zipResult.success }} / {{ zipResult.total }} 张
            </p>
            <p v-for="(url, i) in (zipResult.urls || []).slice(0, 5)" :key="i" class="msg-url">
              {{ url }}
            </p>
            <p v-if="(zipResult.urls || []).length > 5" class="msg-url">... 还有 {{ zipResult.urls.length - 5 }} 张</p>
            <p v-if="zipResult.urls && zipResult.urls.length > 0" class="msg-hint">以上 URL 可直接用于文章 Markdown</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadArticleImage, importSingleArticle, importBatchArticles, batchUploadImages } from '@/services/articleService'

const router = useRouter()
const singleInput = ref(null)
const batchInput = ref(null)
const zipInput = ref(null)
const singleLoading = ref(false)
const batchLoading = ref(false)
const zipLoading = ref(false)
const singleMsg = ref('')
const singleOk = ref(false)
const batchResult = ref(null)
const zipResult = ref(null)

const onSingleFile = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  singleLoading.value = true; singleMsg.value = ''
  const result = await importSingleArticle(file)
  if (result.success) {
    singleMsg.value = `导入成功！文章ID: ${result.data?.articleId || result.data?.id}「${result.data?.title || ''}」`
    singleOk.value = true
  } else {
    singleMsg.value = result.message || '导入失败'
    singleOk.value = false
  }
  singleLoading.value = false
}

const onBatchFiles = async (e) => {
  const files = e.target.files
  if (!files || files.length === 0) return
  batchLoading.value = true; batchResult.value = null
  const result = await importBatchArticles(files)
  if (result.success) {
    batchResult.value = result.data || { total: 0, success: 0, failed: [] }
  } else {
    batchResult.value = { total: 0, success: 0, failed: [{ filename: '批量导入', reason: result.message }] }
  }
  batchLoading.value = false
}

const onZipFile = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  zipLoading.value = true; zipResult.value = null
  const result = await batchUploadImages(file)
  if (result.success) {
    zipResult.value = result.data || { total: 0, success: 0, urls: [], failed: [] }
  } else {
    zipResult.value = { total: 0, success: 0, urls: [], failed: [{ filename: file.name, reason: result.message }] }
  }
  zipLoading.value = false
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.page-title { font-size: 1.8rem; font-weight: 700; color: $text-primary; margin: 24px 0; }

.back-button {
  display: inline-flex; align-items: center; gap: 4px;
  color: $color-primary; cursor: pointer; font-size: 0.95rem; margin-bottom: 8px;
}

.import-section { padding: 24px; margin-bottom: 24px; }

.section-title { font-size: 1.2rem; font-weight: 600; color: $text-primary; margin: 0 0 4px; }
.section-desc { font-size: 0.85rem; color: $text-secondary; margin: 0 0 16px; }

.upload-area { display: flex; flex-direction: column; gap: 12px; }

.btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 10px 24px; font-size: 0.95rem; font-weight: 500;
  border: none; cursor: pointer; transition: background 0.2s;
  max-width: 300px;
  &-primary { background: $color-primary; color: $bg-base; &:hover { background: $color-primary-hover; } }
  &-accent { background: $color-accent; color: $bg-base; &:hover { filter: brightness(1.1); } }
  &-disabled { opacity: 0.5; cursor: not-allowed; }
}

.msg { font-size: 0.85rem; padding: 6px 12px; }
.msg-ok { color: $color-success; }
.msg-err { color: $color-error; font-size: 0.85rem; }
.msg-url { color: $color-primary; font-size: 0.8rem; word-break: break-all; }
.msg-hint { color: $text-tertiary; font-size: 0.8rem; }

.batch-result { display: flex; flex-direction: column; gap: 4px; }
</style>
