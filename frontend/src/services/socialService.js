/**
 * 社交关注服务 — /api/v1/social/*
 */
import { get, post, del } from '@/api/client'

/** POST /social/follow/{userId} */
export const followUser = (userId) =>
  post(`/social/follow/${userId}`, {})

/** DELETE /social/follow/{userId} */
export const unfollowUser = (userId) =>
  del(`/social/follow/${userId}`)

/** GET /social/following/{userId} */
export const getFollowing = (userId, params = {}) =>
  get(`/social/following/${userId}`, params)

/** GET /social/followers/{userId} */
export const getFollowers = (userId, params = {}) =>
  get(`/social/followers/${userId}`, params)
