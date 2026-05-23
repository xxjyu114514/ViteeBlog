/**
 * 频道服务 — /api/v1/channels/*
 */
import { get, post, put, del } from '@/api/client'

/** POST /channels/channels */
export const createChannel = (name) =>
  post('/channels/channels', { name })

/** GET /channels/channels */
export const getChannels = () =>
  get('/channels/channels')

/** PUT /channels/channels/{channelId} */
export const updateChannel = (channelId, name) =>
  put(`/channels/channels/${channelId}`, { name })

/** DELETE /channels/channels/{channelId} */
export const deleteChannel = (channelId) =>
  del(`/channels/channels/${channelId}`)

/** POST /channels/channels/{channelId}/messages */
export const sendMessage = (channelId, content) =>
  post(`/channels/channels/${channelId}/messages`, { content })

/** GET /channels/channels/{channelId}/messages */
export const getMessages = (channelId, params = {}) =>
  get(`/channels/channels/${channelId}/messages`, params)

/** POST /channels/channels/messages/{messageId}/withdraw */
export const withdrawMessage = (messageId) =>
  post(`/channels/channels/messages/${messageId}/withdraw`)

/** GET /channels/channels/messages/{messageId}/re-edit */
export const getWithdrawnContent = (messageId) =>
  get(`/channels/channels/messages/${messageId}/re-edit`)
