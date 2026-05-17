<template>
  <div class="api-test-container">
    <h1>API 接口测试工具</h1>
    <p class="description">此页面用于测试所有API接口是否正常工作，请确保已登录管理员账户以测试完整功能</p>
    
    <div class="test-section">
      <h2>用户认证模块</h2>
      <div class="test-group">
        <button @click="testSendRegisterCode" :disabled="loading.sendRegisterCode">
          {{ loading.sendRegisterCode ? '发送中...' : '发送注册验证码' }}
        </button>
        <div v-if="results.sendRegisterCode" class="result" :class="{ success: results.sendRegisterCode.success, error: !results.sendRegisterCode.success }">
          {{ results.sendRegisterCode.message || JSON.stringify(results.sendRegisterCode.data) }}
        </div>
      </div>
      
      <div class="test-group">
        <button @click="testRegister" :disabled="loading.register">
          {{ loading.register ? '注册中...' : '注册测试' }}
        </button>
        <div v-if="results.register" class="result" :class="{ success: results.register.success, error: !results.register.success }">
          {{ results.register.message || JSON.stringify(results.register.data) }}
        </div>
      </div>
      
      <!-- 登录测试需要在实际登录状态下进行，这里只显示当前登录状态 -->
      <div class="test-group">
        <span>当前登录状态: {{ userStore.user ? '已登录' : '未登录' }}</span>
        <span v-if="userStore.user">用户名: {{ userStore.user.username }} | 角色: {{ userStore.user.role }}</span>
      </div>
    </div>

    <div class="test-section">
      <h2>文章管理模块</h2>
      <div class="test-group">
        <button @click="testAutoSaveArticle" :disabled="loading.autoSaveArticle">
          {{ loading.autoSaveArticle ? '保存中...' : '自动保存文章' }}
        </button>
        <div v-if="results.autoSaveArticle" class="result" :class="{ success: results.autoSaveArticle.success, error: !results.autoSaveArticle.success }">
          {{ results.autoSaveArticle.message || JSON.stringify(results.autoSaveArticle.data) }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentArticleId">
        <button @click="testGetArticleDetail" :disabled="loading.getArticleDetail">
          {{ loading.getArticleDetail ? '获取中...' : '获取文章详情' }}
        </button>
        <div v-if="results.getArticleDetail" class="result" :class="{ success: results.getArticleDetail.success, error: !results.getArticleDetail.success }">
          {{ results.getArticleDetail.message || `标题: ${results.getArticleDetail.data?.title}` }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentArticleId">
        <button @click="testPublishArticle" :disabled="loading.publishArticle">
          {{ loading.publishArticle ? '发布中...' : '发布/提交审核' }}
        </button>
        <div v-if="results.publishArticle" class="result" :class="{ success: results.publishArticle.success, error: !results.publishArticle.success }">
          {{ results.publishArticle.message }}
        </div>
      </div>
      
      <div class="test-group">
        <button @click="testGetPublicArticles" :disabled="loading.getPublicArticles">
          {{ loading.getPublicArticles ? '获取中...' : '获取公开文章列表' }}
        </button>
        <div v-if="results.getPublicArticles" class="result" :class="{ success: results.getPublicArticles.success, error: !results.getPublicArticles.success }">
          {{ results.getPublicArticles.message || `共 ${results.getPublicArticles.data?.total || 0} 篇文章` }}
        </div>
      </div>
      
      <div class="test-group">
        <button @click="testGetMyArticles" :disabled="loading.getMyArticles">
          {{ loading.getMyArticles ? '获取中...' : '获取我的文章列表' }}
        </button>
        <div v-if="results.getMyArticles" class="result" :class="{ success: results.getMyArticles.success, error: !results.getMyArticles.success }">
          {{ results.getMyArticles.message || `共 ${results.getMyArticles.data?.total || 0} 篇文章` }}
        </div>
      </div>
      
      <div class="test-group" v-if="userStore.user?.role === 'admin'">
        <button @click="testGetPendingArticles" :disabled="loading.getPendingArticles">
          {{ loading.getPendingArticles ? '获取中...' : '获取待审核文章列表' }}
        </button>
        <div v-if="results.getPendingArticles" class="result" :class="{ success: results.getPendingArticles.success, error: !results.getPendingArticles.success }">
          {{ results.getPendingArticles.message || `共 ${results.getPendingArticles.data?.length || 0} 篇待审核文章` }}
        </div>
      </div>
      
      <div class="test-group" v-if="userStore.user?.role === 'admin'">
        <button @click="testGetAdminAllArticles" :disabled="loading.getAdminAllArticles">
          {{ loading.getAdminAllArticles ? '获取中...' : '获取全站文章列表' }}
        </button>
        <div v-if="results.getAdminAllArticles" class="result" :class="{ success: results.getAdminAllArticles.success, error: !results.getAdminAllArticles.success }">
          {{ results.getAdminAllArticles.message || `共 ${results.getAdminAllArticles.data?.total || 0} 篇文章` }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentArticleId">
        <button @click="testWithdrawArticle" :disabled="loading.withdrawArticle">
          {{ loading.withdrawArticle ? '撤回中...' : '撤回文章' }}
        </button>
        <div v-if="results.withdrawArticle" class="result" :class="{ success: results.withdrawArticle.success, error: !results.withdrawArticle.success }">
          {{ results.withdrawArticle.message }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentArticleId">
        <button @click="testSoftDeleteArticle" :disabled="loading.softDeleteArticle">
          {{ loading.softDeleteArticle ? '删除中...' : '软删除文章' }}
        </button>
        <div v-if="results.softDeleteArticle" class="result" :class="{ success: results.softDeleteArticle.success, error: !results.softDeleteArticle.success }">
          {{ results.softDeleteArticle.message }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentArticleId">
        <button @click="testRestoreArticle" :disabled="loading.restoreArticle">
          {{ loading.restoreArticle ? '恢复中...' : '恢复文章' }}
        </button>
        <div v-if="results.restoreArticle" class="result" :class="{ success: results.restoreArticle.success, error: !results.restoreArticle.success }">
          {{ results.restoreArticle.message }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentArticleId && userStore.user?.role === 'admin'">
        <button @click="testHardDeleteArticle" :disabled="loading.hardDeleteArticle">
          {{ loading.hardDeleteArticle ? '彻底删除中...' : '彻底删除文章' }}
        </button>
        <div v-if="results.hardDeleteArticle" class="result" :class="{ success: results.hardDeleteArticle.success, error: !results.hardDeleteArticle.success }">
          {{ results.hardDeleteArticle.message }}
        </div>
      </div>
      
      <!-- 文章审核功能 -->
      <div class="test-group" v-if="pendingArticleId && userStore.user?.role === 'admin'">
        <button @click="testReviewArticlePass" :disabled="loading.reviewArticlePass">
          {{ loading.reviewArticlePass ? '审核中...' : '审核通过文章' }}
        </button>
        <div v-if="results.reviewArticlePass" class="result" :class="{ success: results.reviewArticlePass.success, error: !results.reviewArticlePass.success }">
          {{ results.reviewArticlePass.message }}
        </div>
      </div>
      
      <div class="test-group" v-if="pendingArticleId && userStore.user?.role === 'admin'">
        <button @click="testReviewArticleReject" :disabled="loading.reviewArticleReject">
          {{ loading.reviewArticleReject ? '审核中...' : '审核驳回文章' }}
        </button>
        <div v-if="results.reviewArticleReject" class="result" :class="{ success: results.reviewArticleReject.success, error: !results.reviewArticleReject.success }">
          {{ results.reviewArticleReject.message }}
        </div>
      </div>
    </div>

    <div class="test-section">
      <h2>图片管理模块</h2>
      <div class="test-group">
        <input type="file" @change="handleFileSelect" accept="image/*" />
        <button @click="testUploadImage" :disabled="!selectedFile || loading.uploadImage">
          {{ loading.uploadImage ? '上传中...' : '上传图片' }}
        </button>
        <div v-if="results.uploadImage" class="result" :class="{ success: results.uploadImage.success, error: !results.uploadImage.success }">
          {{ results.uploadImage.message || `URL: ${results.uploadImage.data?.url}` }}
        </div>
      </div>
      
      <div class="test-group" v-if="uploadedImageUrl">
        <button @click="testDeleteImage" :disabled="loading.deleteImage">
          {{ loading.deleteImage ? '删除中...' : '删除图片' }}
        </button>
        <div v-if="results.deleteImage" class="result" :class="{ success: results.deleteImage.success, error: !results.deleteImage.success }">
          {{ results.deleteImage.message }}
        </div>
      </div>
    </div>

    <div class="test-section">
      <h2>元数据管理模块</h2>
      <div class="test-group">
        <button @click="testGetCategories" :disabled="loading.getCategories">
          {{ loading.getCategories ? '获取中...' : '获取分类列表' }}
        </button>
        <div v-if="results.getCategories" class="result" :class="{ success: results.getCategories.success, error: !results.getCategories.success }">
          {{ results.getCategories.message || `共 ${results.getCategories.data?.length || 0} 个分类` }}
        </div>
      </div>
      
      <div class="test-group" v-if="userStore.user?.role === 'admin'">
        <input v-model="newCategoryName" placeholder="输入新分类名称" @keyup.enter="testCreateCategory" />
        <button @click="testCreateCategory" :disabled="!newCategoryName || loading.createCategory">
          {{ loading.createCategory ? '创建中...' : '创建分类' }}
        </button>
        <div v-if="results.createCategory" class="result" :class="{ success: results.createCategory.success, error: !results.createCategory.success }">
          {{ results.createCategory.message || `分类ID: ${results.createCategory.data?.id}` }}
        </div>
      </div>
      
      <div class="test-group">
        <button @click="testGetTags" :disabled="loading.getTags">
          {{ loading.getTags ? '获取中...' : '获取标签列表' }}
        </button>
        <div v-if="results.getTags" class="result" :class="{ success: results.getTags.success, error: !results.getTags.success }">
          {{ results.getTags.message || `共 ${results.getTags.data?.length || 0} 个标签` }}
        </div>
      </div>
      
      <div class="test-group">
        <input v-model="newTagName" placeholder="输入新标签名称" @keyup.enter="testCreateTag" />
        <button @click="testCreateTag" :disabled="!newTagName || loading.createTag">
          {{ loading.createTag ? '创建中...' : '创建标签' }}
        </button>
        <div v-if="results.createTag" class="result" :class="{ success: results.createTag.success, error: !results.createTag.success }">
          {{ results.createTag.message || `标签ID: ${results.createTag.data?.id}` }}
        </div>
      </div>
    </div>

    <div class="test-section">
      <h2>评论管理模块</h2>
      <div class="test-group">
        <input v-model="commentArticleId" placeholder="输入文章ID" type="number" />
        <button @click="testGetComments" :disabled="!commentArticleId || loading.getComments">
          {{ loading.getComments ? '获取中...' : '获取文章评论' }}
        </button>
        <div v-if="results.getComments" class="result" :class="{ success: results.getComments.success, error: !results.getComments.success }">
          {{ results.getComments.message || `共 ${results.getComments.data?.length || 0} 条评论` }}
        </div>
      </div>
      
      <div class="test-group" v-if="commentArticleId">
        <textarea v-model="newCommentContent" placeholder="输入评论内容" rows="3"></textarea>
        <button @click="testPostComment" :disabled="!newCommentContent || loading.postComment">
          {{ loading.postComment ? '发表中...' : '发表评论' }}
        </button>
        <div v-if="results.postComment" class="result" :class="{ success: results.postComment.success, error: !results.postComment.success }">
          {{ results.postComment.message || `评论ID: ${results.postComment.data?.id}` }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentCommentId">
        <button @click="testDeleteComment" :disabled="loading.deleteComment">
          {{ loading.deleteComment ? '删除中...' : '删除评论' }}
        </button>
        <div v-if="results.deleteComment" class="result" :class="{ success: results.deleteComment.success, error: !results.deleteComment.success }">
          {{ results.deleteComment.message }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentCommentId">
        <textarea v-model="reportReason" placeholder="输入举报原因" rows="2"></textarea>
        <button @click="testReportComment" :disabled="!reportReason || loading.reportComment">
          {{ loading.reportComment ? '举报中...' : '举报评论' }}
        </button>
        <div v-if="results.reportComment" class="result" :class="{ success: results.reportComment.success, error: !results.reportComment.success }">
          {{ results.reportComment.message || `举报ID: ${results.reportComment.data?.id}` }}
        </div>
      </div>
      
      <div class="test-group" v-if="userStore.user?.role === 'admin'">
        <button @click="testGetReports" :disabled="loading.getReports">
          {{ loading.getReports ? '获取中...' : '获取举报列表' }}
        </button>
        <div v-if="results.getReports" class="result" :class="{ success: results.getReports.success, error: !results.getReports.success }">
          {{ results.getReports.message || `共 ${results.getReports.data?.length || 0} 条举报` }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentReportId && userStore.user?.role === 'admin'">
        <button @click="testResolveReport" :disabled="loading.resolveReport">
          {{ loading.resolveReport ? '处理中...' : '处理举报' }}
        </button>
        <div v-if="results.resolveReport" class="result" :class="{ success: results.resolveReport.success, error: !results.resolveReport.success }">
          {{ results.resolveReport.message }}
        </div>
      </div>
      
      <div class="test-group" v-if="userStore.user?.role === 'admin'">
        <button @click="testGetAdminAllComments" :disabled="loading.getAdminAllComments">
          {{ loading.getAdminAllComments ? '获取中...' : '获取全站评论' }}
        </button>
        <div v-if="results.getAdminAllComments" class="result" :class="{ success: results.getAdminAllComments.success, error: !results.getAdminAllComments.success }">
          {{ results.getAdminAllComments.message || `共 ${results.getAdminAllComments.data?.total || 0} 条评论` }}
        </div>
      </div>
      
      <div class="test-group" v-if="currentCommentId">
        <button @click="testToggleCommentLike" :disabled="loading.toggleCommentLike">
          {{ loading.toggleCommentLike ? '操作中...' : '点赞/取消点赞' }}
        </button>
        <div v-if="results.toggleCommentLike" class="result" :class="{ success: results.toggleCommentLike.success, error: !results.toggleCommentLike.success }">
          {{ results.toggleCommentLike.message }}
        </div>
      </div>
    </div>

    <div class="test-section">
      <h2>批量测试</h2>
      <div class="test-group">
        <button @click="testAllApis" :disabled="isTestingAll">
          {{ isTestingAll ? '批量测试中...' : '批量测试所有接口' }}
        </button>
        <div v-if="allTestResults" class="result" :class="{ success: allTestResults.success, error: !allTestResults.success }">
          {{ allTestResults.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import { useAuthAPI } from '@/composables/useAuthAPI'
import { useArticleAPI } from '@/composables/useArticleAPI'
import { useMetaAPI } from '@/composables/useMetaAPI'
import { useCommentAPI } from '@/composables/useCommentAPI'

const userStore = useUserStore()
const authAPI = useAuthAPI()
const articleAPI = useArticleAPI()
const metaAPI = useMetaAPI()
const commentAPI = useCommentAPI()

// 测试状态
const loading = reactive({
  sendRegisterCode: false,
  register: false,
  autoSaveArticle: false,
  getArticleDetail: false,
  publishArticle: false,
  getPublicArticles: false,
  getMyArticles: false,
  getPendingArticles: false,
  getAdminAllArticles: false,
  withdrawArticle: false,
  softDeleteArticle: false,
  restoreArticle: false,
  hardDeleteArticle: false,
  uploadImage: false,
  deleteImage: false,
  getCategories: false,
  getTags: false,
  createCategory: false,
  createTag: false,
  reviewArticlePass: false,
  reviewArticleReject: false,
  getComments: false,
  postComment: false,
  deleteComment: false,
  reportComment: false,
  getReports: false,
  resolveReport: false,
  getAdminAllComments: false,
  toggleCommentLike: false
})

const results = reactive({
  sendRegisterCode: null,
  register: null,
  autoSaveArticle: null,
  getArticleDetail: null,
  publishArticle: null,
  getPublicArticles: null,
  getMyArticles: null,
  getPendingArticles: null,
  getAdminAllArticles: null,
  withdrawArticle: null,
  softDeleteArticle: null,
  restoreArticle: null,
  hardDeleteArticle: null,
  uploadImage: null,
  deleteImage: null,
  getCategories: null,
  getTags: null,
  createCategory: null,
  createTag: null,
  reviewArticlePass: null,
  reviewArticleReject: null,
  getComments: null,
  postComment: null,
  deleteComment: null,
  reportComment: null,
  getReports: null,
  resolveReport: null,
  getAdminAllComments: null,
  toggleCommentLike: null
})

// 测试数据
const currentArticleId = ref(null)
const pendingArticleId = ref(null)
const selectedFile = ref(null)
const uploadedImageUrl = ref(null)
const isTestingAll = ref(false)
const allTestResults = ref(null)
const newCategoryName = ref('')
const newTagName = ref('')
const commentArticleId = ref('')
const newCommentContent = ref('')
const currentCommentId = ref(null)
const reportReason = ref('')
const currentReportId = ref(null)

// 文件选择处理
const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
}

// 测试方法
const testSendRegisterCode = async () => {
  loading.sendRegisterCode = true
  results.sendRegisterCode = null
  
  try {
    // 使用测试邮箱
    const testEmail = `test_${Date.now()}@example.com`
    const result = await authAPI.sendRegisterCode(testEmail)
    results.sendRegisterCode = result
  } catch (error) {
    results.sendRegisterCode = { success: false, message: '发送验证码失败: ' + error.message }
  } finally {
    loading.sendRegisterCode = false
  }
}

const testRegister = async () => {
  loading.register = true
  results.register = null
  
  try {
    const testEmail = `test_${Date.now()}@example.com`
    const userData = {
      username: `testuser_${Date.now()}`,
      email: testEmail,
      password: 'Test123456',
      email_code: '123456' // 测试用验证码
    }
    const result = await authAPI.register(userData)
    results.register = result
  } catch (error) {
    results.register = { success: false, message: '注册失败: ' + error.message }
  } finally {
    loading.register = false
  }
}

const testAutoSaveArticle = async () => {
  loading.autoSaveArticle = true
  results.autoSaveArticle = null
  
  try {
    const articleData = {
      id: null,
      title: `测试文章 ${new Date().toISOString()}`,
      summary: '这是测试文章的摘要',
      content: '# 测试文章内容\n\n这是自动生成的测试内容...',
      category_id: 1,
      tag_ids: [],
      version: null
    }
    const result = await articleAPI.autoSaveArticle(articleData)
    if (result.success) {
      currentArticleId.value = result.data.id
    }
    results.autoSaveArticle = result
  } catch (error) {
    results.autoSaveArticle = { success: false, message: '保存文章失败: ' + error.message }
  } finally {
    loading.autoSaveArticle = false
  }
}

const testGetArticleDetail = async () => {
  if (!currentArticleId.value) return
  
  loading.getArticleDetail = true
  results.getArticleDetail = null
  
  try {
    const result = await articleAPI.getArticleDetail(currentArticleId.value)
    results.getArticleDetail = result
  } catch (error) {
    results.getArticleDetail = { success: false, message: '获取文章详情失败: ' + error.message }
  } finally {
    loading.getArticleDetail = false
  }
}

const testPublishArticle = async () => {
  if (!currentArticleId.value) return
  
  loading.publishArticle = true
  results.publishArticle = null
  
  try {
    const result = await articleAPI.publishArticle(currentArticleId.value)
    results.publishArticle = result
  } catch (error) {
    results.publishArticle = { success: false, message: '发布文章失败: ' + error.message }
  } finally {
    loading.publishArticle = false
  }
}

const testGetPublicArticles = async () => {
  loading.getPublicArticles = true
  results.getPublicArticles = null
  
  try {
    const result = await articleAPI.getPublicArticles(null, 1, 5)
    results.getPublicArticles = result
  } catch (error) {
    results.getPublicArticles = { success: false, message: '获取公开文章列表失败: ' + error.message }
  } finally {
    loading.getPublicArticles = false
  }
}

const testGetMyArticles = async () => {
  loading.getMyArticles = true
  results.getMyArticles = null
  
  try {
    const result = await articleAPI.getMyArticles(1, 5)
    results.getMyArticles = result
  } catch (error) {
    results.getMyArticles = { success: false, message: '获取我的文章列表失败: ' + error.message }
  } finally {
    loading.getMyArticles = false
  }
}

const testGetPendingArticles = async () => {
  loading.getPendingArticles = true
  results.getPendingArticles = null
  
  try {
    const result = await articleAPI.getPendingArticles()
    if (result.success && result.data.length > 0) {
      pendingArticleId.value = result.data[0].id
    }
    results.getPendingArticles = result
  } catch (error) {
    results.getPendingArticles = { success: false, message: '获取待审核文章列表失败: ' + error.message }
  } finally {
    loading.getPendingArticles = false
  }
}

const testGetAdminAllArticles = async () => {
  loading.getAdminAllArticles = true
  results.getAdminAllArticles = null
  
  try {
    const result = await articleAPI.getAdminAllArticles(1, 5)
    results.getAdminAllArticles = result
  } catch (error) {
    results.getAdminAllArticles = { success: false, message: '获取全站文章列表失败: ' + error.message }
  } finally {
    loading.getAdminAllArticles = false
  }
}

const testWithdrawArticle = async () => {
  if (!currentArticleId.value) return
  
  loading.withdrawArticle = true
  results.withdrawArticle = null
  
  try {
    const result = await articleAPI.withdrawArticle(currentArticleId.value)
    results.withdrawArticle = result
  } catch (error) {
    results.withdrawArticle = { success: false, message: '撤回文章失败: ' + error.message }
  } finally {
    loading.withdrawArticle = false
  }
}

const testSoftDeleteArticle = async () => {
  if (!currentArticleId.value) return
  
  loading.softDeleteArticle = true
  results.softDeleteArticle = null
  
  try {
    const result = await articleAPI.softDeleteArticle(currentArticleId.value)
    results.softDeleteArticle = result
  } catch (error) {
    results.softDeleteArticle = { success: false, message: '软删除文章失败: ' + error.message }
  } finally {
    loading.softDeleteArticle = false
  }
}

const testRestoreArticle = async () => {
  if (!currentArticleId.value) return
  
  loading.restoreArticle = true
  results.restoreArticle = null
  
  try {
    const result = await articleAPI.restoreArticle(currentArticleId.value)
    results.restoreArticle = result
  } catch (error) {
    results.restoreArticle = { success: false, message: '恢复文章失败: ' + error.message }
  } finally {
    loading.restoreArticle = false
  }
}

const testHardDeleteArticle = async () => {
  if (!currentArticleId.value) return
  
  loading.hardDeleteArticle = true
  results.hardDeleteArticle = null
  
  try {
    const result = await articleAPI.hardDeleteArticle(currentArticleId.value)
    results.hardDeleteArticle = result
  } catch (error) {
    results.hardDeleteArticle = { success: false, message: '彻底删除文章失败: ' + error.message }
  } finally {
    loading.hardDeleteArticle = false
  }
}

const testReviewArticlePass = async () => {
  if (!pendingArticleId.value) return
  
  loading.reviewArticlePass = true
  results.reviewArticlePass = null
  
  try {
    const result = await articleAPI.reviewArticle(pendingArticleId.value, true, '')
    results.reviewArticlePass = result
  } catch (error) {
    results.reviewArticlePass = { success: false, message: '审核通过失败: ' + error.message }
  } finally {
    loading.reviewArticlePass = false
  }
}

const testReviewArticleReject = async () => {
  if (!pendingArticleId.value) return
  
  loading.reviewArticleReject = true
  results.reviewArticleReject = null
  
  try {
    const result = await articleAPI.reviewArticle(pendingArticleId.value, false, '内容需要进一步完善')
    results.reviewArticleReject = result
  } catch (error) {
    results.reviewArticleReject = { success: false, message: '审核驳回失败: ' + error.message }
  } finally {
    loading.reviewArticleReject = false
  }
}

const testUploadImage = async () => {
  if (!selectedFile.value) return
  
  loading.uploadImage = true
  results.uploadImage = null
  
  try {
    const result = await articleAPI.uploadImage(selectedFile.value)
    if (result.success) {
      uploadedImageUrl.value = result.data.url
    }
    results.uploadImage = result
  } catch (error) {
    results.uploadImage = { success: false, message: '上传图片失败: ' + error.message }
  } finally {
    loading.uploadImage = false
  }
}

const testDeleteImage = async () => {
  if (!uploadedImageUrl.value) return
  
  // 从URL中提取文件名
  const filename = uploadedImageUrl.value.split('/').pop()
  
  loading.deleteImage = true
  results.deleteImage = null
  
  try {
    const result = await articleAPI.deleteImage(filename)
    if (result.success) {
      uploadedImageUrl.value = null
    }
    results.deleteImage = result
  } catch (error) {
    results.deleteImage = { success: false, message: '删除图片失败: ' + error.message }
  } finally {
    loading.deleteImage = false
  }
}

const testGetCategories = async () => {
  loading.getCategories = true
  results.getCategories = null
  
  try {
    const result = await metaAPI.getCategories()
    results.getCategories = result
  } catch (error) {
    results.getCategories = { success: false, message: '获取分类列表失败: ' + error.message }
  } finally {
    loading.getCategories = false
  }
}

const testCreateCategory = async () => {
  if (!newCategoryName.value) return
  
  loading.createCategory = true
  results.createCategory = null
  
  try {
    const result = await metaAPI.createCategory(newCategoryName.value)
    results.createCategory = result
    if (result.success) {
      newCategoryName.value = ''
    }
  } catch (error) {
    results.createCategory = { success: false, message: '创建分类失败: ' + error.message }
  } finally {
    loading.createCategory = false
  }
}

const testGetTags = async () => {
  loading.getTags = true
  results.getTags = null
  
  try {
    const result = await metaAPI.getTags()
    results.getTags = result
  } catch (error) {
    results.getTags = { success: false, message: '获取标签列表失败: ' + error.message }
  } finally {
    loading.getTags = false
  }
}

const testCreateTag = async () => {
  if (!newTagName.value) return
  
  loading.createTag = true
  results.createTag = null
  
  try {
    const result = await metaAPI.createTag(newTagName.value)
    results.createTag = result
    if (result.success) {
      newTagName.value = ''
    }
  } catch (error) {
    results.createTag = { success: false, message: '创建标签失败: ' + error.message }
  } finally {
    loading.createTag = false
  }
}

const testGetComments = async () => {
  if (!commentArticleId.value) return
  
  loading.getComments = true
  results.getComments = null
  
  try {
    const result = await commentAPI.getComments(commentArticleId.value)
    results.getComments = result
  } catch (error) {
    results.getComments = { success: false, message: '获取评论失败: ' + error.message }
  } finally {
    loading.getComments = false
  }
}

const testPostComment = async () => {
  if (!commentArticleId.value || !newCommentContent.value) return
  
  loading.postComment = true
  results.postComment = null
  
  try {
    const result = await commentAPI.postComment(commentArticleId.value, newCommentContent.value)
    if (result.success) {
      currentCommentId.value = result.data.id
      newCommentContent.value = ''
    }
    results.postComment = result
  } catch (error) {
    results.postComment = { success: false, message: '发表评论失败: ' + error.message }
  } finally {
    loading.postComment = false
  }
}

const testDeleteComment = async () => {
  if (!currentCommentId.value) return
  
  loading.deleteComment = true
  results.deleteComment = null
  
  try {
    const result = await commentAPI.deleteComment(currentCommentId.value)
    results.deleteComment = result
  } catch (error) {
    results.deleteComment = { success: false, message: '删除评论失败: ' + error.message }
  } finally {
    loading.deleteComment = false
  }
}

const testReportComment = async () => {
  if (!currentCommentId.value || !reportReason.value) return
  
  loading.reportComment = true
  results.reportComment = null
  
  try {
    const result = await commentAPI.reportComment(currentCommentId.value, reportReason.value)
    if (result.success) {
      currentReportId.value = result.data.id
      reportReason.value = ''
    }
    results.reportComment = result
  } catch (error) {
    results.reportComment = { success: false, message: '举报评论失败: ' + error.message }
  } finally {
    loading.reportComment = false
  }
}

const testGetReports = async () => {
  loading.getReports = true
  results.getReports = null
  
  try {
    const result = await commentAPI.getReports()
    results.getReports = result
  } catch (error) {
    results.getReports = { success: false, message: '获取举报列表失败: ' + error.message }
  } finally {
    loading.getReports = false
  }
}

const testResolveReport = async () => {
  if (!currentReportId.value) return
  
  loading.resolveReport = true
  results.resolveReport = null
  
  try {
    const result = await commentAPI.resolveReport(currentReportId.value)
    results.resolveReport = result
  } catch (error) {
    results.resolveReport = { success: false, message: '处理举报失败: ' + error.message }
  } finally {
    loading.resolveReport = false
  }
}

const testGetAdminAllComments = async () => {
  loading.getAdminAllComments = true
  results.getAdminAllComments = null
  
  try {
    const result = await commentAPI.getAdminAllComments(1, 5)
    results.getAdminAllComments = result
  } catch (error) {
    results.getAdminAllComments = { success: false, message: '获取全站评论失败: ' + error.message }
  } finally {
    loading.getAdminAllComments = false
  }
}

const testToggleCommentLike = async () => {
  if (!currentCommentId.value) return
  
  loading.toggleCommentLike = true
  results.toggleCommentLike = null
  
  try {
    const result = await commentAPI.toggleCommentLike(currentCommentId.value)
    results.toggleCommentLike = result
  } catch (error) {
    results.toggleCommentLike = { success: false, message: '点赞操作失败: ' + error.message }
  } finally {
    loading.toggleCommentLike = false
  }
}

// 批量测试所有接口
const testAllApis = async () => {
  isTestingAll.value = true
  allTestResults.value = null
  
  try {
    // 按顺序测试关键接口
    const tests = [
      () => testGetPublicArticles(),
      () => testGetCategories(),
      () => testGetTags(),
      () => testGetComments(1) // 默认测试文章ID为1的评论
    ]
    
    // 如果已登录，测试更多接口
    if (userStore.user) {
      tests.push(
        () => testGetMyArticles(),
        () => testAutoSaveArticle()
      )
      
      // 如果是管理员，测试管理员接口
      if (userStore.user.role === 'admin') {
        tests.push(
          () => testGetPendingArticles(),
          () => testGetAdminAllArticles(),
          () => testGetReports(),
          () => testGetAdminAllComments()
        )
      }
    }
    
    // 执行所有测试
    for (const test of tests) {
      await test()
      // 添加小延迟避免请求过于频繁
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    allTestResults.value = { success: true, message: '批量测试完成！请查看各接口的详细结果。' }
  } catch (error) {
    allTestResults.value = { success: false, message: '批量测试失败: ' + error.message }
  } finally {
    isTestingAll.value = false
  }
}
</script>

<style scoped>
.api-test-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #f9f9f9;
  min-height: 100vh;
}

.api-test-container h1 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.description {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 14px;
}

.test-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.test-section h2 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #444;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.test-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.test-group button,
.test-group input[type="file"],
.test-group input,
.test-group textarea {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.test-group input,
.test-group textarea {
  cursor: text;
  padding: 8px;
}

.test-group button:hover:not(:disabled),
.test-group input[type="file"]:hover {
  background: #f5f5f5;
}

.test-group button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result {
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  word-break: break-all;
  max-height: 150px;
  overflow-y: auto;
}

.result.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.result.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

@media (max-width: 768px) {
  .api-test-container {
    padding: 10px;
  }
  
  .test-group {
    gap: 5px;
  }
  
  .test-group button,
  .test-group input[type="file"],
  .test-group input,
  .test-group textarea {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>