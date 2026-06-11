import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => ({
  plugins: [vue()],
  resolve: {
    alias: {
      // 统一使用 @ 符号引用 src 下的文件
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // demo 模式绑定 0.0.0.0 (公网可访问)
    host: mode === 'demo' ? '0.0.0.0' : undefined,
    port: 5173
  }
}))