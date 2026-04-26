<template>
  <div 
    class="posts-immersive-wrapper" 
    @wheel="handleWheel"
  >
    <div class="hero-window">
      <div class="header-content">
        <h1 class="page-title">精选文章</h1>
      </div>
    </div>

    <div class="light-immersive-panel">
      <div class="responsive-container">
        
        <div class="list-section">
          <div class="glass-main-card">
            
            <div class="items-stack">
              <div 
                class="glass-sub-card" 
                v-for="i in 3" 
                :key="i"
              >
                <div class="card-internal">
                  <div class="text-info">
                    <span class="item-index">0{{ i }}</span>
                    <span class="item-title">文章标题预览内容 {{ i }}</span>
                  </div>
                  <div class="static-arrow">→</div>
                </div>
              </div>
            </div>

            <div class="more-trigger-area" @click.stop="navToSubList">
              <div class="more-content">
                <span class="more-text">了解更多</span>
                <span class="more-arrow">→</span>
              </div>
            </div>

          </div>
        </div>

        <div class="auth-section">
          <div class="glass-login-card">
            <div class="login-header">
              <div class="user-avatar-glass"></div>
              <span class="login-title">LOGIN</span>
            </div>
            <div class="login-body">
              <button class="action-btn">立即登录</button>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel';

const router = useRouter();

// 注册项目标准的滚轮逻辑，参数需与 pageOrder 一致
const { handleWheel } = usePrimaryPageWheel('posts-immersive');

// 点击“了解更多”跳转至二级列表页
const navToSubList = () => {
  router.push('/posts'); 
};
</script>

<style lang="scss" scoped>
/* 定义 image_6.png 的渐变色作为全局变量，方便复用 */
$gradient-start: rgba(235, 245, 230, 0.85); // 类似左侧浅绿
$gradient-end: rgba(255, 220, 180, 0.85);   // 类似右侧浅橙
$blur-intensity: 12px;                      // 毛玻璃模糊度

@font-face {
  font-family: 'PingFang SC Heavy';
  src: url('@/assets/Font/PingFang SC Heavy.ttf') format('truetype');
  font-weight: 900;
}

.posts-immersive-wrapper {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  /* 基础背景色，作为毛玻璃衬底 */
  background: radial-gradient(circle at center, #ffffff 0%, #f0f0f0 100%);
  overflow: hidden; /* 严禁溢出确保滚轮信号穿透 */
}

/* 顶部背景区域 */
.hero-window {
  height: 32vh;
  min-height: 250px;
  width: 100%;
  background: #111 url('../assets/hero-bg.webp') center 10% / cover no-repeat;
  position: relative;
  flex-shrink: 0;

  .header-content {
    position: absolute;
    left: 6vw;
    bottom: 2.5vh;
    .page-title {
      font-family: 'PingFang SC Heavy', sans-serif;
      font-size: clamp(1.8rem, 3vw, 2.5rem);
      color: white;
      margin: 0;
      letter-spacing: 2px;
      text-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
  }
}

/* 底部沉浸式功能面板 (吸取图片质感的核心) */
.light-immersive-panel {
  flex: 1;
  width: 100%;
  padding: 3vh 6vw;
  box-sizing: border-box;
  display: flex;
  align-items: center; /* 垂直居中，留出上下边距凸显沉浸感 */
}

.responsive-container {
  display: flex;
  width: 100%;
  max-width: 1300px;
  margin: 0 auto;
  gap: 3.5vw;
}

/* 左侧：卡片式列表 (吸取图片质感核心) */
.list-section {
  flex: 1.6;

  /* 大外框：大圆角，微透明，柔和投影 */
  .glass-main-card {
    background: #ffffff; // 兜底白色，hover时启用毛玻璃和渐变
    border-radius: 28px; // 类似图片的大圆角
    border: 1px solid rgba(0,0,0,0.03); // 极细的微边框增加精致感
    display: flex;
    flex-direction: column;
    padding: 25px 25px 15px 25px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.04); // 极淡的投影模拟沉浸
    transition: all 0.4s ease;

    /* 模拟沉浸模式：hover触发毛玻璃和渐变色 */
    &:hover {
      background: linear-gradient(135deg, $gradient-start 0%, $gradient-end 100%);
      backdrop-filter: blur($blur-intensity);
      -webkit-backdrop-filter: blur($blur-intensity);
      border-color: rgba(255,255,255,0.2); // 沉浸模式下边框变白
      box-shadow: 0 15px 50px rgba(0,0,0,0.08); // 投影略微增强
    }
  }

  .items-stack {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }

  /* 独立子卡片：轻量级毛玻璃与微投影 */
  .glass-sub-card {
    background: rgba(255, 255, 255, 0.9); // 微透明白
    border-radius: 18px;
    padding: 18px 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02); // 微投影凸显层次
    transition: all 0.3s;

    .card-internal {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .text-info {
        display: flex;
        align-items: center;
        gap: 15px;
        .item-index {
          font-family: 'PingFang SC Heavy';
          color: rgba(0,0,0,0.15); // 半透明色编号，体现层次感
          font-size: 1.2rem;
        }
        .item-title {
          font-weight: 700;
          font-size: 1.05rem;
          color: #1a1a1a;
          letter-spacing: 0.5px;
        }
      }
      .static-arrow {
        font-size: 1.2rem;
        color: rgba(0,0,0,0.3); // 类似图片质感的箭头色
      }
    }

    &:hover {
      background: rgba(255, 255, 255, 1);
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(0,0,0,0.05);
    }
  }

  /* 了解更多触发区 */
  .more-trigger-area {
    display: flex;
    justify-content: flex-end;
    padding-top: 10px;
    cursor: pointer;

    .more-content {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 18px;
      border-radius: 80px; // 胶囊型，更现代化
      transition: background 0.2s;

      .more-text {
        font-family: 'PingFang SC Heavy';
        font-size: 0.95rem;
        color: rgba(0,0,0,0.7); // 增加呼吸感文字色
      }
      .more-arrow {
        font-size: 1rem;
        color: rgba(0,0,0,0.5);
      }

      &:hover {
        background: rgba(255, 255, 255, 0.4);
      }
    }
  }
}

/* 右侧：登录区应用同套逻辑 */
.auth-section {
  flex: 1;
  display: flex;
  justify-content: flex-end;

  .glass-login-card {
    width: 100%;
    max-width: 380px;
    background: #ffffff;
    border-radius: 28px;
    border: 1px solid rgba(0,0,0,0.03);
    padding: 30px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.04);
    height: fit-content;
    transition: all 0.4s ease;

    &:hover {
      background: linear-gradient(135deg, $gradient-start 0%, $gradient-end 100%);
      backdrop-filter: blur($blur-intensity);
      -webkit-backdrop-filter: blur($blur-intensity);
      border-color: rgba(255,255,255,0.2);
      box-shadow: 0 15px 50px rgba(0,0,0,0.08);
    }

    .login-header {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 25px;
      
      /* 头像也应用轻毛玻璃和微透明色 */
      .user-avatar-glass {
        width: 48px; height: 48px;
        background: rgba(0, 0, 0, 0.05);
        border: 2px solid rgba(255,255,255,0.2);
        border-radius: 50%;
        backdrop-filter: blur(5px);
      }
      .login-title {
        font-family: 'PingFang SC Heavy';
        font-size: 1.2rem;
        color: #1a1a1a;
      }
    }

    .action-btn {
      width: 100%;
      padding: 16px;
      /* 按钮换用图片上的现代化深色质感 */
      background: linear-gradient(135deg, #2c3e50 0%, #000000 100%);
      color: #fff;
      border: none;
      border-radius: 12px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
      transition: opacity 0.2s;
      &:hover { opacity: 0.85; }
    }
  }
}

/* 适配：针对小屏幕防止内容溢出显示器 */
@media (max-height: 850px) {
  .hero-window { height: 26vh; }
  .light-immersive-panel { padding: 1.5vh 6vw; }
  .glass-main-card { padding: 15px 15px 10px 15px; }
  .glass-sub-card { padding: 12px 20px; }
  .responsive-container { gap: 2vw; }
}
</style>