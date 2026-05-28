<template>
  <div class="state-wrapper">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ loadingText }}</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button v-if="canRetry" class="btn-retry" @click="$emit('retry')">重新加载</button>
    </div>

    <div v-else-if="empty" class="empty-state">
      <slot name="empty">
        <p>{{ emptyText }}</p>
      </slot>
    </div>

    <slot v-else />
  </div>
</template>

<script setup>
defineProps({
  loading: { type: Boolean, default: false },
  error: { type: [String, Boolean], default: false },
  empty: { type: Boolean, default: false },
  loadingText: { type: String, default: '加载中...' },
  emptyText: { type: String, default: '暂无数据' },
  canRetry: { type: Boolean, default: true },
})

defineEmits(['retry'])
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.state-wrapper { width: 100%; }

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  text-align: center;

  .spinner {
    width: 32px; height: 32px;
    border: 3px solid rgba(0, 0, 0, 0.1);
    border-top: 3px solid $color-primary;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
  }
  p { color: $text-secondary; font-size: 1.1rem; }
}

.error-state {
  text-align: center;
  padding: 60px 0;

  .error-message { color: $color-danger; margin-bottom: 16px; }

  .btn-retry {
    padding: 8px 20px;
    background: $color-primary;
    color: $bg-base;
    border: none;
    cursor: pointer;
    font-size: 0.95rem;
    transition: background 0.2s;
    &:hover { background: $color-primary-hover; }
  }
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  p { color: $text-secondary; font-size: 1.1rem; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
