import { ref } from 'vue'

// ★ 全局样式切换开关
// true  = 新样式（Navbar Oswald/2rem + PostPage PanelNews 沉浸页）
// false = 老样式（Navbar 原始数值 + PostPage 卡片列表）
export const useNavV2 = ref(false)
