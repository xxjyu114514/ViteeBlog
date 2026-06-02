/**
 * 用户主页服务 — /api/v1/users/*
 */
import { get } from '@/api/client'

/** GET /users/{userId} — 获取用户公开主页信息 */
export const getUserProfile = (userId) =>
  get(`/users/${userId}`)

/** GET /users/{userId}/articles — 获取该用户发布的文章列表 */
export const getUserArticles = (userId, params = {}) =>
  get(`/users/${userId}/articles`, params)
