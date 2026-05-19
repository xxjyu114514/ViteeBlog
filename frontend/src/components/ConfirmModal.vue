<template>
  <Teleport to="body">
    <div v-if="show" class="confirm-overlay" @click="$emit('cancel')">
      <div class="confirm-modal" @click.stop>
        <div class="confirm-header">
          <h3>{{ title }}</h3>
        </div>
        <div class="confirm-body">
          <p>{{ message }}</p>
        </div>
        <div class="confirm-footer">
          <button class="btn-cancel" @click="$emit('cancel')">取消</button>
          <button class="btn-confirm" :class="{ danger: danger }" @click="$emit('confirm')" :disabled="loading">
            {{ loading ? '处理中...' : confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '确定要执行此操作吗？' },
  confirmText: { type: String, default: '确定' },
  danger: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})
defineEmits(['confirm', 'cancel'])
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;
.confirm-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.4); display: flex;
  justify-content: center; align-items: center; z-index: 2000;
}
.confirm-modal {
  background: white; border-radius: 12px; padding: 24px;
  width: 90%; max-width: 360px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.confirm-header { h3 { margin: 0 0 12px; font-size: 1.1rem; } }
.confirm-body { p { margin: 0 0 20px; color: #555; font-size: 0.95rem; line-height: 1.5; } }
.confirm-footer { display: flex; justify-content: flex-end; gap: 12px; }
.btn-cancel, .btn-confirm {
  padding: 8px 20px; border-radius: 8px; font-size: 0.9rem; font-weight: 500; cursor: pointer; border: none;
}
.btn-cancel { background: #f3f4f6; color: #333; &:hover { background: #e5e7eb; } }
.btn-confirm { background: $color-primary; color: white; &:hover { background: $color-primary-hover; } &:disabled { opacity: 0.6; } &.danger { background: #ef4444; &:hover { background: #dc2626; } } }
</style>
