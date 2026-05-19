/**
 * 通用工具函数
 */
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

// ============================================================
// XSS 防护：所有 Markdown 渲染输出都经过 DOMPurify 过滤
// ============================================================

const purify = (html) => DOMPurify.sanitize(html)

// ============================================================
// 日期格式化
// ============================================================

export const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

export const formatDateTime = (dateString) => {
  if (!dateString) return '未知时间'
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// ============================================================
// Markdown 渲染（单例 + XSS 防护）
// ============================================================

/** 用于渲染标题和内联文本 */
const mdInline = new MarkdownIt({ html: false, linkify: true })

/** 用于渲染全文 */
const mdFull = new MarkdownIt({ html: true, linkify: true, typographer: true })

/** 用于渲染预览（带代码高亮） */
let mdPreview = null

const getMdPreview = async () => {
  if (mdPreview) return mdPreview
  const hljs = (await import('highlight.js')).default
  mdPreview = new MarkdownIt({
    html: true,
    linkify: true,
    highlight: (str, lang) => {
      if (lang && hljs.getLanguage(lang)) return hljs.highlight(str, { language: lang }).value
      return ''
    },
  })
  return mdPreview
}

/** 渲染内联文本（标题等），已防 XSS */
export const renderInline = (text) => {
  if (!text) return ''
  return purify(mdInline.renderInline(text))
}

/** 渲染完整 Markdown，已防 XSS */
export const renderMarkdown = (content) => {
  if (!content) return ''
  return purify(mdFull.render(content))
}

/** 渲染带代码高亮的 Markdown，已防 XSS */
export const renderHighlightedMarkdown = async (content) => {
  if (!content) return ''
  const md = await getMdPreview()
  return purify(md.render(content))
}

// ============================================================
// 其他工具
// ============================================================

export const debounce = (fn, delay = 300) => {
  let timer = null
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

export const getBackendFileUrl = (contentPath) => {
  if (!contentPath) return null
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  const backendBase = baseUrl.replace('/api/v1', '')
  let normalized = contentPath.replace(/\\/g, '/')
  if (!normalized.startsWith('/')) normalized = '/' + normalized
  return `${backendBase}${normalized}`
}
