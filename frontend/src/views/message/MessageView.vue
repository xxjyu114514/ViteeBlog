<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div class="back-button" @click="router.go(-1)">← 返回</div>

    <div class="channel-layout">
      <div class="channel-sidebar">
        <h3 class="sidebar-title">频道</h3>
        <div class="channel-list">
          <div v-for="ch in channels" :key="ch.id" :class="['channel-item-wrap', { active: currentChannel?.id === ch.id }]">
            <button class="channel-item" @click="selectChannel(ch)">
              <span class="channel-name"># {{ ch.name }}</span>
            </button>
            <div v-if="userStore.isAdmin" class="channel-admin-actions">
              <button class="ch-btn ch-edit" @click.stop="openEditChannel(ch)" title="编辑频道">✎</button>
              <button class="ch-btn ch-del" @click.stop="handleDeleteChannel(ch.id)" title="删除频道" :disabled="deletingChannelId === ch.id">✕</button>
            </div>
          </div>
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
                <div class="msg-actions">
                  <button v-if="!msg.withdrawnAt && msg.userId === userStore.userInfo?.id" class="btn-withdraw" @click="handleWithdraw(msg.id)">撤回</button>
                  <button v-if="msg.withdrawnAt && msg.userId === userStore.userInfo?.id" class="btn-reedit" @click="handleReEdit(msg.id)" :disabled="reEditingId === msg.id">{{ reEditingId === msg.id ? '加载中...' : '重新编辑' }}</button>
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

    <!-- 编辑频道弹窗 -->
    <Teleport to="body">
      <div v-if="showEditChannel" class="modal-overlay" @click="showEditChannel = false">
        <div class="modal-box" @click.stop>
          <h3>编辑频道</h3>
          <div v-if="editChannelMsg" :class="['modal-msg', editChannelErr ? 'err' : 'ok']">{{ editChannelMsg }}</div>
          <input v-model="editChannelName" placeholder="频道名称" class="modal-input" @keydown.enter="handleUpdateChannel" />
          <div class="modal-actions">
            <button class="btn-cancel" @click="showEditChannel = false">取消</button>
            <button class="btn-confirm" @click="handleUpdateChannel" :disabled="!editChannelName.trim() || updatingChannel">
              {{ updatingChannel ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getChannels, getMessages, sendMessage, withdrawMessage, createChannel, getWithdrawnContent, updateChannel, deleteChannel } from '@/services/channelService'
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
const reEditingId = ref(null)
const showEditChannel = ref(false)
const editChannelName = ref('')
const editChannelId = ref(null)
const updatingChannel = ref(false)
const editChannelMsg = ref('')
const editChannelErr = ref(false)
const deletingChannelId = ref(null)
let pollTimer = null

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
  startPolling()
}

const startPolling = () => {
  stopPolling()
  pollTimer = setInterval(pollForNewMessages, 5000)
}

const stopPolling = () => {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

const pollForNewMessages = async () => {
  if (!currentChannel.value || messages.value.length === 0) return
  const newestId = messages.value[messages.value.length - 1].id
  const r = await getMessages(currentChannel.value.id, { limit: 10 })
  if (r.success) {
    const raw = r.data.items || []
    const sorted = [...raw].sort((a, b) => a.id - b.id)
    const newOnes = sorted.filter(m => m.id > newestId)
    if (newOnes.length > 0) {
      messages.value = [...messages.value, ...newOnes]
      scrollToBottom()
    }
  }
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
  const msg = messages.value.find(m => m.id === messageId)
  if (msg?.createdAt) {
    const elapsed = Date.now() - new Date(msg.createdAt).getTime()
    if (elapsed > 120000) {
      alert('消息发送已超过2分钟，无法撤回')
      return
    }
  }
  if (!confirm('确定要撤回这条消息吗？')) return
  const r = await withdrawMessage(messageId)
  if (r.success) { if (msg) msg.withdrawnAt = new Date().toISOString() }
  else { alert(r.message || '撤回失败') }
}

const handleReEdit = async (messageId) => {
  if (reEditingId.value) return
  reEditingId.value = messageId
  const r = await getWithdrawnContent(messageId)
  if (r.success && r.data) {
    inputContent.value = r.data.content || ''
    // 聚焦到输入框
    await nextTick()
    const textarea = document.querySelector('.chat-input')
    if (textarea) textarea.focus()
  } else {
    alert(r.message || '获取失败')
  }
  reEditingId.value = null
}

const handleCreateChannel = async () => {
  if (!newChannelName.value.trim()) return
  const r = await createChannel(newChannelName.value.trim())
  if (r.success) { channels.value.push(r.data); showCreateChannel.value = false; newChannelName.value = '' }
  else { alert(r.message || '创建失败') }
}

const openEditChannel = (ch) => {
  editChannelId.value = ch.id
  editChannelName.value = ch.name
  editChannelMsg.value = ''
  editChannelErr.value = false
  showEditChannel.value = true
}

const handleUpdateChannel = async () => {
  if (!editChannelName.value.trim() || updatingChannel.value) return
  updatingChannel.value = true
  editChannelMsg.value = ''
  const r = await updateChannel(editChannelId.value, editChannelName.value.trim())
  if (r.success) {
    editChannelMsg.value = '频道名称已更新'
    editChannelErr.value = false
    // 更新本地数据
    const ch = channels.value.find(c => c.id === editChannelId.value)
    if (ch) ch.name = editChannelName.value.trim()
    setTimeout(() => { showEditChannel.value = false }, 1000)
  } else {
    editChannelMsg.value = r.message || '更新失败'
    editChannelErr.value = true
  }
  updatingChannel.value = false
}

const handleDeleteChannel = async (channelId) => {
  if (!confirm('确定要删除此频道吗？所有聊天记录将一并删除！')) return
  deletingChannelId.value = channelId
  const r = await deleteChannel(channelId)
  if (r.success) {
    channels.value = channels.value.filter(c => c.id !== channelId)
    if (currentChannel.value?.id === channelId) {
      currentChannel.value = null
      messages.value = []
    }
  } else {
    alert(r.message || '删除失败')
  }
  deletingChannelId.value = null
}

onMounted(() => { fetchChannels() })
onUnmounted(() => { stopPolling() })
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.page-wrapper-base {
  background: $bg-dark url(#{$img-message-bg}) center / cover no-repeat fixed;
  min-height: 100vh;
  position: relative;
}

.channel-layout {
  display: flex;
  height: calc(100vh - 100px);
  max-width: 1200px;
  margin: 0 auto;
  overflow: hidden;
  background: rgba(45, 51, 59, 0.82);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.10);
}
.channel-sidebar { width: 200px; background: rgba(45, 51, 59, 0.5); padding: 16px; display: flex; flex-direction: column; border-right: 1px solid rgba(255, 255, 255, 0.08); }
.sidebar-title { font-size: 0.85rem; color: $text-secondary; margin: 0 0 12px; text-transform: uppercase; letter-spacing: 1px; }
.channel-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
.channel-item-wrap {
  display: flex; align-items: center; gap: 4px;
  border-radius: 8px;
  &.active { background: $color-primary; .channel-item { color: $bg-base; } }
}
.channel-item {
  flex: 1; padding: 8px 12px; cursor: pointer; text-align: left;
  border: none; background: none; font-size: 0.95rem; color: $text-main;
  &:hover { background: rgba($color-primary, 0.08); }
}
.channel-admin-actions {
  display: flex; gap: 2px; padding-right: 4px;
}
.ch-btn {
  width: 20px; height: 20px; padding: 0; border: none; border-radius: 4px;
  cursor: pointer; font-size: 0.7rem; display: flex; align-items: center; justify-content: center;
  background: transparent; opacity: 0.5; transition: opacity 0.15s;
  &:hover { opacity: 1; }
}
.ch-edit { color: $color-primary; &:hover { background: rgba($color-primary, 0.15); } }
.ch-del { color: $color-danger; &:hover { background: rgba($color-danger, 0.15); } &:disabled { opacity: 0.3; cursor: not-allowed; } }
.btn-add-channel { margin-top: 12px; padding: 8px; border: 1px dashed $border-color; border-radius: 8px; background: none; cursor: pointer; color: $text-secondary; font-size: 0.85rem; &:hover { border-color: $color-primary; color: $color-primary; } }

.modal-msg { padding: 8px 12px; font-size: 0.85rem; margin-bottom: 8px; border-radius: 4px; &.err { background: rgba($color-danger, 0.1); color: $color-danger; } &.ok { background: rgba($color-success, 0.1); color: $color-success; } }

.chat-main { flex: 1; display: flex; flex-direction: column; background: rgba(45, 51, 59, 0.3); }
.chat-placeholder { display: flex; align-items: center; justify-content: center; height: 100%; color: $text-secondary; }
.chat-header { padding: 12px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); h2 { margin: 0; font-size: 1.1rem; } }

.message-area { flex: 1; overflow-y: auto; padding: 16px 20px; display: flex; flex-direction: column; gap: 12px; }
.btn-load-more { align-self: center; padding: 6px 16px; border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; background: rgba(255,255,255,0.06); cursor: pointer; font-size: 0.85rem; &:hover { background: rgba(255,255,255,0.10); } }
.empty-chat { text-align: center; color: $text-secondary; padding: 40px 0; }

.message-item { display: flex; gap: 10px; max-width: 80%; &.own { align-self: flex-end; flex-direction: row-reverse; } &.withdrawn { opacity: 0.5; } }
.msg-avatar { flex-shrink: 0; }
.avatar-img { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }
.avatar-letter { width: 36px; height: 36px; border-radius: 50%; background: $color-primary; color: $bg-base; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 600; }
.msg-body { background: rgba(45, 51, 59, 0.5); padding: 8px 12px; border-radius: 12px; min-width: 100px; }
.own .msg-body { background: rgba($color-primary, 0.12); }
.msg-header { display: flex; gap: 8px; margin-bottom: 4px; }
.msg-author { font-weight: 600; font-size: 0.85rem; color: $text-main; }
.msg-time { font-size: 0.75rem; color: $text-secondary; }
.msg-content { font-size: 0.95rem; line-height: 1.5; color: $text-main; white-space: pre-wrap; &.withdrawn { font-style: italic; color: $text-secondary; } }
.msg-actions { margin-top: 4px; }
.btn-withdraw { font-size: 0.75rem; color: $color-danger; background: none; border: none; cursor: pointer; padding: 0; &:hover { text-decoration: underline; } }
.btn-reedit { font-size: 0.75rem; color: $color-primary; background: none; border: none; cursor: pointer; padding: 0; &:hover { text-decoration: underline; } &:disabled { opacity: 0.5; cursor: not-allowed; } }

.chat-input-area { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid rgba(255, 255, 255, 0.08); background: rgba(45, 51, 59, 0.4); }
.chat-input { flex: 1; padding: 10px 12px; border: 1px solid $border-color; border-radius: 8px; font-size: 0.95rem; resize: none; height: 44px; font-family: inherit; box-sizing: border-box; &:focus { outline: none; border-color: $color-primary; } }
.btn-send { padding: 0 20px; border: none; border-radius: 8px; background: $color-primary; color: $bg-base; font-weight: 500; cursor: pointer; &:disabled { opacity: 0.5; } &:hover:not(:disabled) { background: $color-primary-hover; } }

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background: $bg-surface; border-radius: 12px; padding: 24px; width: 90%; max-width: 360px; h3 { margin: 0 0 16px; } }
.modal-input { width: 100%; padding: 10px 12px; border: 1px solid $border-color; border-radius: 8px; font-size: 0.95rem; box-sizing: border-box; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 16px; }
.btn-cancel { padding: 8px 20px; border: 1px solid $border-color; border-radius: 8px; background: $bg-surface; cursor: pointer; }
.btn-confirm { padding: 8px 20px; border: none; border-radius: 8px; background: $color-primary; color: $bg-base; cursor: pointer; &:disabled { opacity: 0.5; } }
</style>
