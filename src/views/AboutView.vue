<template>
  <div class="about-container">
    <section class="about-hero">
      <h1 class="glass-text">About Me</h1>
    </section>

    <div class="about-main">
      <div class="content-card">
        <h2>个人简介</h2>
        <p>这里是你毕业设计展示的个人核心信息...</p>
      </div>
      <div v-for="n in 5" :key="n" class="content-card">
        <h3>经历模块 {{ n }}</h3>
        <p>详细描述你的项目经验、技术栈或观测笔记的内容。</p>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.about-container {
  width: 100%;
  background: #f0f2f5;
}

.about-hero {
  height: 50vh;
  background: #1a1a1a url('@/assets/about-bg.jpg') center/cover;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
}

.about-main {
  max-width: 900px;
  margin: -50px auto 0; // 向上偏移，产生重叠感
  padding: 0 20px 100px;
  position: relative;
  z-index: 2;
}

.content-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
</style>