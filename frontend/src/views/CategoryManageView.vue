<template>
  <div class="category-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <button class="btn-back" @click="handleBack">← 返回</button>
          <span class="card-title">分类管理</span>
          <div class="header-actions">
            <button class="btn btn-primary btn-sm" @click="showCreateModal" :disabled="creating">{{ creating ? '创建中...' : '新建分类' }}</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="categories.length > 0" class="list">
            <div v-for="category in categories" :key="category.id" class="list-item">
              <div class="list-item-info">
                <span class="list-item-name">{{ category.name }}</span>
                <span class="list-item-id">ID: {{ category.id }}</span>
              </div>
              <div class="list-item-actions">
                <button class="act-btn" @click="showEditModal(category)" :disabled="updatingId === category.id">{{ updatingId === category.id ? '...' : '编辑' }}</button>
                <button class="act-btn act-del" @click="handleDelete(category.id)" :disabled="deletingId === category.id">{{ deletingId === category.id ? '...' : '删除' }}</button>
              </div>
            </div>
          </div>
          <StateWrapper v-else :loading="loading" empty-text="暂无分类" @retry="fetchCategories">
            <template #empty-action>
              <button class="btn btn-primary btn-sm mt-20" @click="showCreateModal">创建第一个分类</button>
            </template>
          </StateWrapper>
        </div>
      </div>
    </div>

    <!-- 创建/编辑模态框 -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-box" @click.stop>
          <h3>{{ editingCategory ? '编辑分类' : '新建分类' }}</h3>
          <input v-model="categoryName" class="modal-input" placeholder="分类名称" maxlength="50" :disabled="creating || updatingId" @keydown.enter="handleSubmit" />
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="closeModal">取消</button>
            <button class="btn btn-primary" :disabled="!categoryName.trim() || creating || updatingId" @click="handleSubmit">{{ creating || updatingId ? '处理中...' : (editingCategory ? '保存' : '创建') }}</button>
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
import StateWrapper from '@/components/StateWrapper.vue'

const router = useRouter()
const slidIn = ref(false)
const categories = ref([])
const loading = ref(false)
const editingCategory = ref(null)
const categoryName = ref('')
const creating = ref(false)
const updatingId = ref(null)
const deletingId = ref(null)
const showModal = ref(false)

const fetchCategories = async () => {
  loading.value = true
  const result = await metaService.getCategories()
  if (result.success) categories.value = result.data || []
  else alert(result.message || '获取分类列表失败')
  loading.value = false
}

const showCreateModal = () => { editingCategory.value = null; categoryName.value = ''; showModal.value = true }
const showEditModal = (category) => { editingCategory.value = { ...category }; categoryName.value = category.name; showModal.value = true }
const closeModal = () => { showModal.value = false; editingCategory.value = null; categoryName.value = '' }
const handleBack = () => router.go(-1)

const handleSubmit = async () => {
  if (!categoryName.value.trim()) return
  if (editingCategory.value) {
    updatingId.value = editingCategory.value.id
    const r = await metaService.updateCategory(editingCategory.value.id, categoryName.value.trim())
    if (r.success) { await fetchCategories(); closeModal() } else alert(r.message || '更新失败')
    updatingId.value = null
  } else {
    creating.value = true
    const r = await metaService.createCategory(categoryName.value.trim())
    if (r.success) { await fetchCategories(); closeModal() } else alert(r.message || '创建失败')
    creating.value = false
  }
}

const handleDelete = async (categoryId) => {
  if (!confirm('确定删除此分类？')) return
  deletingId.value = categoryId
  const r = await metaService.deleteCategory(categoryId)
  if (r.success) await fetchCategories()
  else alert(r.message || '删除失败')
  deletingId.value = null
}

onMounted(() => { fetchCategories(); requestAnimationFrame(() => { slidIn.value = true }) })
</script>

<style lang="scss">
@use 'sass:color';
@use './_design.scss' as *;

.category-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }

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

.btn { padding: 6px 16px; border: none; cursor: pointer; font-size: 0.9rem; }
.btn-primary { background: $color-primary; color: $bg-base; &:hover { background: color.adjust($color-primary, $lightness: 8%); } }
.btn-sm { padding: 4px 12px; font-size: 0.8rem; }
.btn-ghost { background: transparent; color: $text-secondary; &:hover { background: $bg-hover; color: $text-primary; } }
.mt-20 { margin-top: 20px; }
</style>
