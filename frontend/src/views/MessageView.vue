<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div class="back-button" @click="router.go(-1)">← 返回</div>

    <div class="channel-layout">
      <div class="channel-sidebar">
        <h3 class="sidebar-title">频道</h3>
        <div class="channel-list">
          <button v-for="ch in channels" :key="ch.id" :class="['channel-item', { active: currentChannel?.id === ch.id }]" @click="selectChannel(ch)">
            <span class="channel-name"># {{ ch.name }}</span>
          </button>
        </div>
        <button v-if="userStore.isAdmin" class="btn-add-channel" @click="showCreateChannel = true">+ 创建频道</button>
      </div>

      <div class="chat-main">
        <div v-if="!currentChannel" class="chat-placeholder"><p>请选择一个频道开始聊天</p></div>

        <template v-else>
          <div class="chat-header"><h2># {{ currentChannel.name }}</h2></div>

          <div class="message-area" ref="messageAreaRef">
            <button v-if="hasMore" class="btn-load-more" @click="loadMore" :disabled="loadingMore">{{ loadingMore ? '加载中...' : '加载更多' }}</button>
            <div v-if="messages.length === 0 && !loadingMore" class="empty-chat">暂无消息</div>
            <div v-for="msg in messages" :key="msg.id" class="message-item" :class="{ own: msg.userId === userStore.userInfo?.id, withdrawn: msg.withdrawnAt }">
              <div class="msg-avatar">
                <img v-if="msg.sender?.avatar" :src="getFileUrl(msg.sender.avatar)" class="avatar-img" />
                <span v-else class="avatar-letter">{{ msg.sender?.username?.charAt(0).toUpperCase() || '?' }}</span>
              </div>
              <div class="msg-body">
                <div class="msg-header">
                  <span class="msg-author">{{ msg.sender?.username || '匿名' }}</span>
                  <span class="msg-time">{{ formatDateTime(msg.createdAt) }}</span>
                </div>
                <div v-if="msg.withdrawnAt" class="msg-content withdrawn">该消息已被撤回</div>
                <div v-else class="msg-content">{{ msg.content }}</div>
                <div v-if="!msg.withdrawnAt && msg.userId === userStore.userInfo?.id" class="msg-actions">
                  <button class="btn-withdraw" @click="handleWithdraw(msg.id)">撤回</button>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <textarea v-model="inputContent" class="chat-input" placeholder="输入消息... (Enter 发送)" :disabled="sending" @keydown.enter.exact.prevent="handleSend"></textarea>
            <button class="btn-send" @click="handleSend" :disabled="!inputContent.trim() || sending">{{ sending ? '发送中...' : '发送' }}</button>
          </div>
        </template>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showCreateChannel" class="modal-overlay" @click="showCreateChannel = false">
        <div class="modal-box" @click.stop>
          <h3>创建频道</h3>
          <input v-model="newChannelName" placeholder="频道名称" class="modal-input" @keydown.enter="handleCreateChannel" />
          <div class="modal-actions">
            <button class="btn-cancel" @click="showCreateChannel = false">取消</button>
            <button class="btn-confirm" @click="handleCreateChannel" :disabled="!newChannelName.trim()">创建</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getChannels, getMessages, sendMessage, withdrawMessage, createChannel } from '@/services/channelService'
import { formatDateTime } from '@/utils'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const router = useRouter()
const userStore = useUserStore()

const channels = ref([])
const currentChannel = ref(null)
const messages = ref([])
const inputContent = ref('')
const sending = ref(false)
const loadingMore = ref(false)
const hasMore = ref(false)
const nextCursor = ref(null)
const messageAreaRef = ref(null)
const showCreateChannel = ref(false)
const newChannelName = ref('')

const getFileUrl = (path) => path ? API_BASE.replace('/api/v1', '') + path : ''

const scrollToBottom = () => { nextTick(() => { const el = messageAreaRef.value; if (el) el.scrollTop = el.scrollHeight }) }

const fetchChannels = async () => {
  const r = await getChannels()
  if (r.success) channels.value = r.data || []
}

const selectChannel = async (ch) => {
  currentChannel.value = ch; messages.value = []; hasMore.value = false; nextCursor.value = null
  await loadMessages()
  scrollToBottom()
}

const loadMessages = async () => {
  if (!currentChannel.value) return
  const params = { limit: 30 }
  if (nextCursor.value) params.beforeId = nextCursor.value
  const r = await getMessages(currentChannel.value.id, params)
  if (r.success) {
    const raw = r.data.items || []
    // 强制按 id 升序排序，确保最旧在上、最新在下
    const sorted = [...raw].sort((a, b) => a.id - b.id)
    messages.value = [...sorted, ...messages.value]
    hasMore.value = r.data.hasMore ?? false
    nextCursor.value = r.data.nextCursor ?? null
  }
}

const loadMore = async () => { loadingMore.value = true; await loadMessages(); loadingMore.value = false }

const handleSend = async () => {
  if (!inputContent.value.trim() || sending.value || !currentChannel.value) return
  sending.value = true
  const r = await sendMessage(currentChannel.value.id, inputContent.value.trim())
  if (r.success) { inputContent.value = ''; messages.value.push(r.data); scrollToBottom() }
  sending.value = false
}

const handleWithdraw = async (messageId) => {
  if (!confirm('确定要撤回这条消息吗？')) return
  const r = await withdrawMessage(messageId)
  if (r.success) { const msg = messages.value.find(m => m.id === messageId); if (msg) msg.withdrawnAt = new Date().toISOString() }
  else { alert(r.message || '撤回失败') }
}

const handleCreateChannel = async () => {
  if (!newChannelName.value.trim()) return
  const r = await createChannel(newChannelName.value.trim())
  if (r.success) { channels.value.push(r.data); showCreateChannel.value = false; newChannelName.value = '' }
  else { alert(r.message || '创建失败') }
}

onMounted(() => { fetchChannels() })
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.channel-layout { display: flex; height: calc(100vh - 80px); max-width: 1200px; margin: 0 auto; border: 1px solid $border-color; border-radius: 12px; overflow: hidden; }
.channel-sidebar { width: 200px; background: $bg-smoke; padding: 16px; display: flex; flex-direction: column; border-right: 1px solid $border-color; }
.sidebar-title { font-size: 0.85rem; color: $text-secondary; margin: 0 0 12px; text-transform: uppercase; letter-spacing: 1px; }
.channel-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
.channel-item { padding: 8px 12px; border-radius: 8px; cursor: pointer; text-align: left; border: none; background: none; font-size: 0.95rem; color: $text-main; &:hover { background: rgba($color-primary, 0.08); } &.active { background: $color-primary; color: white; } }
.btn-add-channel { margin-top: 12px; padding: 8px; border: 1px dashed $border-color; border-radius: 8px; background: none; cursor: pointer; color: $text-secondary; font-size: 0.85rem; &:hover { border-color: $color-primary; color: $color-primary; } }

.chat-main { flex: 1; display: flex; flex-direction: column; }
.chat-placeholder { display: flex; align-items: center; justify-content: center; height: 100%; color: $text-secondary; }
.chat-header { padding: 12px 20px; border-bottom: 1px solid $border-color; h2 { margin: 0; font-size: 1.1rem; } }

.message-area { flex: 1; overflow-y: auto; padding: 16px 20px; display: flex; flex-direction: column; gap: 12px; }
.btn-load-more { align-self: center; padding: 6px 16px; border: 1px solid $border-color; border-radius: 6px; background: white; cursor: pointer; font-size: 0.85rem; &:hover { background: $bg-smoke; } }
.empty-chat { text-align: center; color: $text-secondary; padding: 40px 0; }

.message-item { display: flex; gap: 10px; max-width: 80%; &.own { align-self: flex-end; flex-direction: row-reverse; } &.withdrawn { opacity: 0.5; } }
.msg-avatar { flex-shrink: 0; }
.avatar-img { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }
.avatar-letter { width: 36px; height: 36px; border-radius: 50%; background: $color-primary; color: white; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 600; }
.msg-body { background: $bg-smoke; padding: 8px 12px; border-radius: 12px; min-width: 100px; }
.own .msg-body { background: rgba($color-primary, 0.1); }
.msg-header { display: flex; gap: 8px; margin-bottom: 4px; }
.msg-author { font-weight: 600; font-size: 0.85rem; color: $text-main; }
.msg-time { font-size: 0.75rem; color: $text-secondary; }
.msg-content { font-size: 0.95rem; line-height: 1.5; color: $text-main; white-space: pre-wrap; &.withdrawn { font-style: italic; color: $text-secondary; } }
.msg-actions { margin-top: 4px; }
.btn-withdraw { font-size: 0.75rem; color: $color-danger; background: none; border: none; cursor: pointer; padding: 0; &:hover { text-decoration: underline; } }

.chat-input-area { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid $border-color; background: white; }
.chat-input { flex: 1; padding: 10px 12px; border: 1px solid $border-color; border-radius: 8px; font-size: 0.95rem; resize: none; height: 44px; font-family: inherit; box-sizing: border-box; &:focus { outline: none; border-color: $color-primary; } }
.btn-send { padding: 0 20px; border: none; border-radius: 8px; background: $color-primary; color: white; font-weight: 500; cursor: pointer; &:disabled { opacity: 0.5; } &:hover:not(:disabled) { background: $color-primary-hover; } }

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background: white; border-radius: 12px; padding: 24px; width: 90%; max-width: 360px; h3 { margin: 0 0 16px; } }
.modal-input { width: 100%; padding: 10px 12px; border: 1px solid $border-color; border-radius: 8px; font-size: 0.95rem; box-sizing: border-box; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 16px; }
.btn-cancel { padding: 8px 20px; border: 1px solid $border-color; border-radius: 8px; background: white; cursor: pointer; }
.btn-confirm { padding: 8px 20px; border: none; border-radius: 8px; background: $color-primary; color: white; cursor: pointer; &:disabled { opacity: 0.5; } }
</style>
