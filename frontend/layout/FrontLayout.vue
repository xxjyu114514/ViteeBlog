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
      <p>© 2024 个人博客系统. 版权所有.</p> [cite: 10]
    </footer>
  </div>
</template>
<script setup>
import "./FrontLayout.scss"
</script>
<style lang="scss" scoped>

</style>