<template>
  <div class="front-layout">
    <header class="navbar">
      <div class="container">
        <h1 class="logo">个人博客</h1> 
        <nav class="nav-links">
          <router-link to="/">首页</router-link>
          <router-link to="/about">关于我</router-link>
          <router-link to="/message">留言板</router-link> 
        </nav>
      </div>
    </header>

    <main>
      <router-view />
    </main>

    <footer class="footer">
      <p>© 2024 个人博客系统. 版权所有.</p>
    </footer>
  </div>
</template>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.navbar {
  height: 64px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid $border-color-light;
  position: sticky;
  top: 0;
  background: $bg-surface;
  backdrop-filter: blur(10px);
  z-index: 100;

  .container {
    max-width: 1100px;
    margin: 0 auto;
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
  }

  .nav-links a {
    margin-left: 25px;
    font-weight: 500;
    transition: color 0.3s;
    color: $text-secondary;
    &:hover { color: $color-primary; }
    &.router-link-active { color: $color-primary; }
  }
}
</style>