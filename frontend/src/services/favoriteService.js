/**
 * 收藏服务 — /api/v1/favorites/*
 */
import { get, post } from '@/api/client'

/** POST /favorites/{articleId}/favorite */
export const toggleFavorite = (articleId) =>
  post(`/favorites/${articleId}/favorite`, {})

/** GET /favorites/my */
export const getMyFavorites = (params = {}) =>
  get('/favorites/my', params)

/** GET /favorites/check/{articleId} */
export const checkFavoriteStatus = (articleId) =>
  get(`/favorites/check/${articleId}`)
