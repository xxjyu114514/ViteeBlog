<template>
  <div v-if="showModal" class="report-modal-overlay" @click="closeModal">
    <div class="report-modal" @click.stop>
      <div class="modal-header">
        <h3>举报评论</h3>
        <button class="close-btn" @click="closeModal">×</button>
      </div>
      
      <div class="modal-body">
        <p class="help-text">请选择举报原因（必填）：</p>
        
        <div class="reason-options">
          <label 
            v-for="(reason, index) in reportReasons" 
            :key="index"
            class="reason-option"
            :class="{ selected: selectedReason === reason.value }"
          >
            <input
              type="radio"
              :value="reason.value"
              v-model="selectedReason"
              :id="'reason-' + index"
            />
            <span class="reason-label">{{ reason.label }}</span>
          </label>
        </div>
        
        <div class="custom-reason" v-if="selectedReason === 'other'">
          <label for="custom-reason-input">详细说明（可选）：</label>
          <textarea
            id="custom-reason-input"
            v-model="customReason"
            placeholder="请详细描述违规内容..."
            maxlength="200"
            rows="3"
          ></textarea>
          <div class="char-count">{{ customReason.length }}/200</div>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn-cancel" @click="closeModal">取消</button>
        <button 
          class="btn-submit" 
          @click="handleSubmit"
          :disabled="!canSubmit || loading"
        >
          {{ loading ? '提交中...' : '提交举报' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCommentAPI } from '@/composables/useCommentAPI'

const props = defineProps({
  commentId: {
    type: Number,
    required: true
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:show', 'report-success'])

// 举报原因选项
const reportReasons = [
  { value: 'spam', label: '垃圾广告' },
  { value: 'abuse', label: '人身攻击/辱骂' },
  { value: 'illegal', label: '违法违规内容' },
  { value: 'irrelevant', label: '与主题无关' },
  { value: 'other', label: '其他问题' }
]

const selectedReason = ref('')
const customReason = ref('')
const error = ref('')
const loading = ref(false)

// 使用计算属性同步props的show值到内部状态，实现双向绑定
const showModal = computed({
  get() {
    return props.show
  },
  set(value) {
    emit('update:show', value)
  }
})

// 监听show变化以重置表单状态
watch(() => props.show, (newVal) => {
  if (newVal) {
    // 重置表单状态
    selectedReason.value = ''
    customReason.value = ''
    error.value = ''
  }
})

// 关闭弹窗
const closeModal = () => {
  showModal.value = false
}

// 提交按钮可用性
const canSubmit = computed(() => {
  return selectedReason.value && !loading.value
})

// 获取实际举报原因
const getReportReason = () => {
  const baseReason = reportReasons.find(r => r.value === selectedReason.value)?.label || selectedReason.value
  if (selectedReason.value === 'other' && customReason.value.trim()) {
    return `${baseReason}: ${customReason.value.trim()}`
  }
  return baseReason
}

// 提交举报
const handleSubmit = async () => {
  if (!canSubmit.value) return
  
  const reason = getReportReason()
  if (!reason) {
    error.value = '请选择举报原因'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const { reportComment } = useCommentAPI()
    const result = await reportComment(props.commentId, reason)
    
    if (result.success) {
      emit('report-success')
      closeModal()
    } else {
      error.value = result.message || '举报失败，请稍后重试'
    }
  } catch (err) {
    console.error('Report submit error:', err)
    error.value = '网络错误，请检查网络连接后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
// 使用全局样式变量
.report-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* 增加z-index确保覆盖所有内容 */
}

.report-modal {
  background: white;
  border-radius: 16px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  position: relative; /* 确保内部元素的z-index相对于此容器 */
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
  
  h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #4b5563;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.2s ease;
    
    &:hover {
      background: #f5f5f5;
    }
  }
}

.modal-body {
  padding: 24px;
  
  .help-text {
    margin: 0 0 16px;
    color: #4b5563;
    font-size: 0.95rem;
  }
  
  .reason-options {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .reason-option {
    display: flex;
    align-items: center;
    padding: 12px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: #3b82f6;
      background: rgba(59, 130, 246, 0.05);
    }
    
    &.selected {
      border-color: #3b82f6;
      background: rgba(59, 130, 246, 0.1);
    }
    
    input[type="radio"] {
      margin-right: 12px;
      width: 18px;
      height: 18px;
      cursor: pointer;
    }
    
    .reason-label {
      font-size: 1rem;
      color: #1f2937;
      cursor: pointer;
    }
  }
  
  .custom-reason {
    margin-top: 16px;
    
    label {
      display: block;
      margin-bottom: 8px;
      font-size: 0.95rem;
      color: #1f2937;
    }
    
    textarea {
      width: 100%;
      padding: 12px;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      font-size: 1rem;
      line-height: 1.5;
      resize: vertical;
      transition: border-color 0.2s ease;
      
      &:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
      }
    }
    
    .char-count {
      text-align: right;
      font-size: 0.85rem;
      color: #4b5563;
      margin-top: 4px;
    }
  }
  
  .error-message {
    margin-top: 16px;
    padding: 12px;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid #ef4444;
    border-radius: 8px;
    color: #ef4444;
    font-size: 0.9rem;
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 24px;
  border-top: 1px solid #e5e7eb;
  
  .btn-cancel {
    background: none;
    border: 1px solid #e5e7eb;
    color: #4b5563;
    padding: 8px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    
    &:hover {
      background: #f5f5f5;
    }
  }
  
  .btn-submit {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    padding: 8px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    
    &:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
    }
    
    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
  }
}
</style>