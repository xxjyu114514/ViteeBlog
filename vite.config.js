import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // 统一使用 @ 符号引用 src 下的文件 
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})