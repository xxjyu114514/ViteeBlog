<template>
  <div
    class="message-immersive-page"
    @wheel="onWheel"
  >
    <!-- ===== A: 背景图区域 30vh ===== -->
    <div class="bg-section">
      <div class="glass-overlay"></div>

      <div class="header-content">
        <h1 class="page-title">留言板</h1>
        <p class="page-subtitle">MESSAGE BOARD / 2026</p>
      </div>
    </div>

    <!-- ===== B: 频道消息预览区 70vh ===== -->
    <div class="list-section">
      <div class="list-header">
        <span class="channel-badge" v-if="channels.length > 0">{{ channels.length }} 个频道</span>
        <h2 class="list-title">最新消息</h2>
      </div>

      <div class="list-body" ref="listBodyRef">
        <!-- 加载状态 -->
        <div v-if="loading" class="state-display">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="state-display">
          <p class="error-msg">{{ error }}</p>
          <button class="btn btn-ghost" @click="loadData">重新加载</button>
        </div>

        <!-- 空状态（无频道） -->
        <div v-else-if="channels.length === 0" class="state-display">
          <p>暂无讨论频道</p>
        </div>

        <!-- 频道卡片列表 -->
        <div v-else class="channel-list">
          <div
            v-for="(ch, idx) in channels"
            :key="ch.id"
            class="channel-card"
            @click="router.push('/message')"
          >
            <div class="channel-card__header">
              <div class="meta-row">
                <span class="item-index">{{ String(idx + 1).padStart(2, '0') }}</span>
                <h3 class="channel-card__title"># {{ ch.name }}</h3>
              </div>
            </div>
            <div class="channel-card__footer">
              <span class="static-arrow">→</span>
            </div>
          </div>
        </div>
      </div>

      <div class="list-footer">
        <button class="btn btn-glass" @click="router.push('/message')">进入留言板</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'
import { getChannels } from '@/services/channelService'

const router = useRouter()
const { handleWheel } = usePrimaryPageWheel('message-immersive')

const channels = ref([])
const loading = ref(true)
const error = ref(null)

const loadData = async () => {
  loading.value = true
  error.value = null
  const r = await getChannels()
  if (r.success) {
    channels.value = r.data || []
  } else {
    error.value = r.message || '加载频道列表失败'
  }
  loading.value = false
}

/** 始终绑定的 wheel 拦截器，仅在 immersive 模式执行导航并阻止滚动 */
const onWheel = (e) => {
  e.preventDefault()
  handleWheel(e)
}

onMounted(() => { loadData() })
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

/* ============================================================
   基础容器 — 固定 100vh，不可滚动，与 PostPage 一致
   ============================================================ */
.message-immersive-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden !important;
  background: $bg-dark;
}

/* ============================================================
   A: 背景图区域 30vh
   ============================================================ */
.bg-section {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 30vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  background: $bg-dark url(#{$img-message-bg}) center / cover no-repeat;
  background-position-y: 30%;
  z-index: 1;

  .glass-overlay {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    opacity: 0.25;
    pointer-events: none;
  }

  .header-content {
    position: relative;
    z-index: 2;
    text-align: left;
    padding-left: 40px;
    width: 100%;

    .page-title {
      font-size: 2.5rem;
      font-weight: 700;
      color: $text-primary;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
      margin: 0;
    }

    .page-subtitle {
      font-size: 1.1rem;
      color: $text-primary;
      margin-top: 8px;
    }
  }
}

/* ============================================================
   B: 频道消息预览区 70vh
   ============================================================ */
.list-section {
  position: absolute;
  top: 30vh;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 2;
  background: $bg-base;

  .list-header {
    flex-shrink: 0;
    padding: 20px 24px 0;
    display: flex;
    align-items: center;
    gap: 12px;

    .list-title {
      font-size: 1.3rem;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }

    .channel-badge {
      font-size: 0.75rem;
      color: $color-primary;
      border: 1px solid rgba($color-primary, 0.25);
      padding: 2px 10px;
      font-weight: 500;
      letter-spacing: 0.5px;
    }
  }

  .list-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px 24px 0;
  }

  .list-footer {
    flex-shrink: 0;
    padding: 16px 24px;
    display: flex;
    justify-content: flex-end;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }
}

/* ============================================================
   频道卡片 — 与 PostPage 的 article-card 完全一致
   ============================================================ */
.channel-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 60vw;
  margin: 0 auto;
}

.channel-card {
  background: $bg-surface;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: $space-lg;
  position: relative;
  cursor: pointer;
  transition: border-color $transition-base, box-shadow $transition-base;

  &::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px; bottom: -1px;
    background: linear-gradient(to right,
      transparent 0%, rgba($color-primary, 0.06) 50%, rgba($color-primary, 0.15) 100%);
    opacity: 0;
    transition: opacity $transition-base;
    pointer-events: none;
    z-index: 1;
  }

  &:hover::before { opacity: 1; }
  &:hover { border-color: rgba($color-primary, 0.2); box-shadow: $glow-brand; }

  .channel-card__header { position: relative; z-index: 2; }

  .meta-row {
    display: flex;
    align-items: center;
    gap: 16px;

    .item-index {
      font-size: 1.2rem;
      font-weight: 600;
      color: $color-primary;
      flex-shrink: 0;
    }

    .channel-card__title {
      font-size: 1.1rem;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
      line-height: 1.3;
    }
  }

  .channel-card__footer {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 8px;
    padding-top: 6px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }

  .static-arrow {
    font-size: 1.2rem;
    color: $text-tertiary;
  }
}

/* ============================================================
   状态显示
   ============================================================ */
.state-display {
  padding: 2rem;
  text-align: center;

  .loading-spinner {
    width: 30px; height: 30px;
    border: 2px solid rgba(255, 255, 255, 0.08);
    border-top: 2px solid $color-primary;
    border-radius: 50% !important;
    animation: spin 1s linear infinite;
    margin: 0 auto 12px;
  }

  .error-msg { color: $color-error; font-size: 1rem; margin-bottom: 1rem; }
  p { font-size: 1rem; color: $text-secondary; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ============================================================
   响应式
   ============================================================ */
@media (max-width: 768px) {
  .bg-section {
    .header-content {
      padding-left: 20px;
      .page-title { font-size: 1.8rem; }
      .page-subtitle { font-size: 0.95rem; }
    }
  }

  .list-section {
    .list-body { padding: 12px 16px 0; }
    .list-footer { padding: 12px 16px; }
  }

  .channel-card { padding: $space-md; }
  .channel-list { max-width: 90vw; }
}
</style>
