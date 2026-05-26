/**
 * 认证服务 — /api/v1/auth/*
 * 所有函数返回 ApiResponse 格式
 */
import { get, post, put, del, uploadFile } from '@/api/client'

/** POST /auth/login */
export const login = (username, password) =>
  post('/auth/login', { username, password })

/** POST /auth/register */
export const register = (data) =>
  post('/auth/register', data)

/** POST /auth/send-register-code */
export const sendRegisterCode = (email) =>
  post('/auth/send-register-code', { email })

/** PUT /auth/change-password */
export const changePassword = (oldPassword, newPassword) =>
  put('/auth/change-password', { old_password: oldPassword, new_password: newPassword })

/** POST /auth/forgot-password/send-code */
export const sendForgotCode = (email) =>
  post('/auth/forgot-password/send-code', { email })

/** POST /auth/forgot-password/reset */
export const resetPassword = (email, code, newPassword) =>
  post('/auth/forgot-password/reset', { email, code, new_password: newPassword })

/** DELETE /auth/delete-account */
export const deleteAccount = () =>
  del('/auth/delete-account')

/** PUT /auth/admin/users/{userId}/role */
export const updateUserRole = (userId, newRole) =>
  put(`/auth/admin/users/${userId}/role`, { new_role: newRole })

/** PUT /auth/admin/users/{userId}/restore */
export const restoreUser = (userId) =>
  put(`/auth/admin/users/${userId}/restore`)

/** POST /auth/upload-avatar */
export const uploadAvatar = (file) =>
  uploadFile('/auth/upload-avatar', file, 'file')

/** PUT /auth/update-profile */
export const updateProfile = (data) =>
  put('/auth/update-profile', data)
