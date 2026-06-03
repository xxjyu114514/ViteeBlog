<template>
  <div class="tag-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <button class="btn-back" @click="handleBack">← 返回</button>
          <span class="card-title">标签管理</span>
          <div class="header-actions">
            <button class="btn btn-primary btn-sm" @click="openModalForCreate" :disabled="creating">{{ creating ? '创建中...' : '新建标签' }}</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="tags.length > 0" class="list">
            <div v-for="tag in tags" :key="tag.id" class="list-item">
              <div class="list-item-info">
                <span class="list-item-name">{{ tag.name }}</span>
                <span class="list-item-id">ID: {{ tag.id }}</span>
              </div>
              <div class="list-item-actions">
                <button class="act-btn" @click="openModalForEdit(tag)" :disabled="updatingId === tag.id">{{ updatingId === tag.id ? '...' : '编辑' }}</button>
                <button class="act-btn act-del" @click="handleDelete(tag.id)" :disabled="deletingId === tag.id">{{ deletingId === tag.id ? '...' : '删除' }}</button>
              </div>
            </div>
          </div>
          <div v-else-if="loading" class="state-msg"><div class="spinner"></div><p>加载中...</p></div>
          <div v-else class="state-msg"><p>暂无标签</p><button class="btn btn-primary btn-sm mt-20" @click="openModalForCreate">创建第一个标签</button></div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="isModalOpen" class="modal-overlay" @click="closeModal">
        <div class="modal-box" @click.stop>
          <h3>{{ editingTag ? '编辑标签' : '新建标签' }}</h3>
          <input v-model="tagName" class="modal-input" placeholder="标签名称" maxlength="50" :disabled="creating || updatingId" @keydown.enter="handleCreateOrUpdateTag" />
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="closeModal">取消</button>
            <button class="btn btn-primary" :disabled="!tagName.trim() || creating || updatingId" @click="handleCreateOrUpdateTag">{{ creating || updatingId ? '处理中...' : (editingTag ? '保存' : '创建') }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as metaService from '@/services/metaService'

const router = useRouter()
const slidIn = ref(false)
const loading = ref(false)
const tags = ref([])
const creating = ref(false)
const updatingId = ref(null)
const deletingId = ref(null)
const tagName = ref('')
const editingTag = ref(null)
const isModalOpen = ref(false)

const fetchTags = async () => {
  loading.value = true
  const result = await metaService.getTags()
  if (result.success) tags.value = result.data || []
  else alert(result.message || '获取标签列表失败')
  loading.value = false
}

const openModalForCreate = () => { tagName.value = ''; editingTag.value = null; isModalOpen.value = true }
const openModalForEdit = (tag) => { tagName.value = tag.name; editingTag.value = tag; isModalOpen.value = true }
const closeModal = () => { isModalOpen.value = false; tagName.value = ''; editingTag.value = null }
const handleBack = () => router.go(-1)

const handleCreateOrUpdateTag = async () => {
  if (!tagName.value.trim()) return
  if (editingTag.value) {
    updatingId.value = editingTag.value.id
    const r = await metaService.updateTag(editingTag.value.id, tagName.value.trim())
    if (r.success) { await fetchTags(); closeModal() } else alert(r.message || '更新失败')
    updatingId.value = null
  } else {
    creating.value = true
    const r = await metaService.createTag(tagName.value.trim())
    if (r.success) { await fetchTags(); closeModal() } else alert(r.message || '创建失败')
    creating.value = false
  }
}

const handleDelete = async (tagId) => {
  if (!confirm('确定删除此标签？')) return
  deletingId.value = tagId
  const r = await metaService.deleteTag(tagId)
  if (r.success) await fetchTags()
  else alert(r.message || '删除失败')
  deletingId.value = null
}

onMounted(() => { fetchTags(); requestAnimationFrame(() => { slidIn.value = true }) })
</script>

<style lang="scss">
@use 'sass:color';
@use './test_scss.scss' as *;

.tag-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }

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

.card-body { flex: 1; overflow-y: auto; padding: $space-xl; }

.list { display: flex; flex-direction: column; gap: 4px; }

.list-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: $space-md; transition: background 0.15s;
  &:hover { background: $bg-hover; }
}

.list-item-info { display: flex; flex-direction: column; gap: 2px; }
.list-item-name { font-size: 0.95rem; font-weight: 500; color: $text-primary; }
.list-item-id { font-size: 0.75rem; color: $text-tertiary; }

.list-item-actions { display: flex; gap: 6px; }

.act-btn {
  padding: 4px 12px; font-size: 0.78rem; border: 1px solid $glass-border; background: transparent;
  color: $text-secondary; cursor: pointer;
  &:hover { border-color: $color-primary; color: $color-primary; }
  &:disabled { opacity: 0.4; cursor: not-allowed; }
}
.act-del { color: $color-error; border-color: rgba($color-error, 0.3); &:hover { border-color: $color-error; } }

.state-msg { display: flex; flex-direction: column; align-items: center; gap: $space-md; padding: $space-2xl 0; p { color: $text-secondary; font-size: 0.95rem; } }
.spinner { width: 24px; height: 24px; border: 2px solid rgba($text-tertiary, 0.25); border-top-color: $color-primary; border-radius: 50%; animation: mspin 0.8s linear infinite; }
@keyframes mspin { to { transform: rotate(360deg); } }

.btn { padding: 6px 16px; border: none; cursor: pointer; font-size: 0.9rem; }
.btn-primary { background: $color-primary; color: $bg-base; &:hover { background: color.adjust($color-primary, $lightness: 8%); } }
.btn-sm { padding: 4px 12px; font-size: 0.8rem; }
.btn-ghost { background: transparent; color: $text-secondary; &:hover { background: $bg-hover; color: $text-primary; } }
.mt-20 { margin-top: 20px; }
</style>
