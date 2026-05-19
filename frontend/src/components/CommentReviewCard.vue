<template>
  <div
    class="comment-card"
    :class="[type === 'report' ? 'report-card' : 'pending-card', { selected }]"
  >
    <div class="comment-header">
      <div class="comment-checkbox">
        <input
          type="checkbox"
          :checked="selected"
          @change="$emit('update:selected', $event.target.checked)"
        />
      </div>

      <div class="comment-meta">
        <div class="author-info">
          <span class="username">{{ comment.author?.username || '匿名' }}</span>
          <span class="role-badge" v-if="comment.author?.role === 'admin'">管理员</span>
        </div>
        <div class="time-info">
          <span v-if="type === 'report'" class="report-time">
            举报时间: {{ formatDateTime(reportData?.createdAt) }}
          </span>
          <span class="comment-time">
            评论时间: {{ formatDateTime(comment.createdAt) }}
          </span>
        </div>
      </div>
    </div>

    <div v-if="type === 'report' && reportData" class="report-reason">
      <span class="reason-label">举报原因:</span>
      <span class="reason-text">{{ getReportReasonText(reportData.reason) }}</span>
      <span v-if="reportData.customReason" class="custom-reason">({{ reportData.customReason }})</span>
    </div>

    <div class="comment-content">
      <p>{{ comment.content }}</p>
    </div>

    <div class="comment-actions">
      <button
        class="btn-approve"
        @click="$emit('approve', comment.id)"
        :disabled="loading"
      >
        {{ loading ? '处理中...' : '恢复显示' }}
      </button>
      <button
        class="btn-reject"
        @click="$emit('reject', comment.id)"
        :disabled="loading"
      >
        {{ loading ? '处理中...' : '标记违规' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { formatDateTime } from '@/utils'

const props = defineProps({
  comment: { type: Object, required: true },
  type: { type: String, default: 'pending' },
  selected: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  reportData: { type: Object, default: null },
})

defineEmits(['update:selected', 'approve', 'reject'])

const getReportReasonText = (reason) => {
  const map = {
    spam: '垃圾广告',
    abuse: '人身攻击/辱骂',
    illegal: '违法违规内容',
    irrelevant: '与主题无关',
    other: '其他问题',
  }
  return map[reason] || reason
}
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.comment-card {
  background: white;
  border: 1px solid $border-color;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;

  &.selected {
    border-color: $color-primary;
    background: rgba($color-primary, 0.05);
  }
}

.comment-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.comment-checkbox {
  margin-top: 4px;
  input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; }
}

.comment-meta { flex: 1; }

.author-info {
  display: flex; gap: 12px; margin-bottom: 8px; flex-wrap: wrap;
  .username { font-weight: 600; color: $text-main; }
  .role-badge { color: $text-secondary; font-size: 0.85rem; }
}

.time-info {
  display: flex; gap: 12px;
  span { color: $text-secondary; font-size: 0.9rem; }
}

.report-reason {
  margin-bottom: 12px;
  .reason-label { font-weight: 500; color: $text-main; }
  .reason-text { color: $color-warning; }
  .custom-reason { color: $text-secondary; font-size: 0.85rem; }
}

.comment-content {
  margin-bottom: 16px;
  p { color: $text-main; line-height: 1.6; white-space: pre-wrap; margin: 0; }
}

.comment-actions {
  display: flex; gap: 12px;
}

.btn-approve, .btn-reject {
  border: none; padding: 6px 16px; border-radius: 6px;
  cursor: pointer; font-size: 0.9rem; font-weight: 500;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  &:hover:not(:disabled) { transform: translateY(-1px); }
  &:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
}

.btn-approve {
  background: linear-gradient(135deg, $color-success 0%, darken($color-success, 10%) 100%);
  color: white;
  box-shadow: 0 2px 8px rgba($color-success, 0.3);
  &:hover:not(:disabled) { box-shadow: 0 4px 12px rgba($color-success, 0.4); }
}

.btn-reject {
  background: linear-gradient(135deg, $color-danger 0%, darken($color-danger, 10%) 100%);
  color: white;
  box-shadow: 0 2px 8px rgba($color-danger, 0.3);
  &:hover:not(:disabled) { box-shadow: 0 4px 12px rgba($color-danger, 0.4); }
}
</style>
