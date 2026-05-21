<template>
  <div class="demo-container">
    <!-- ==================== 导航栏 ==================== -->
    <nav class="industrial-nav">
      <div class="logo-section">
        <span class="logo-text">SYS.TERMINAL</span>
        <span class="logo-badge">v2.4.1</span>
      </div>

      <div class="nav-menu">
        <div
          v-for="(item, index) in navItems"
          :key="index"
          class="nav-item"
          :class="{ active: activeNav === index }"
          @click="activeNav = index"
        >
          {{ item }}
        </div>
      </div>

      <div class="nav-actions">
        <button class="btn-outline-sm">EXPORT</button>
        <button class="btn-primary-sm">CONNECT</button>
      </div>
    </nav>

    <!-- ==================== 英雄区 ==================== -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-line"></span>
          SYSTEM STATUS: OPERATIONAL
        </div>
        <h1 class="hero-title">
          Modular Infrastructure<br>
          <span class="hero-accent">Real-time Monitor</span>
        </h1>
        <p class="hero-desc">
          High-density data visualization with tactical-grade precision.
          Monitor system metrics, track anomalies, and deploy countermeasures in milliseconds.
        </p>
        <div class="hero-actions">
          <button class="btn-primary">INITIALIZE SCAN</button>
          <button class="btn-outline">VIEW DOCS</button>
        </div>
      </div>

      <div class="hero-stats">
        <div class="stat-block">
          <div class="stat-number">2,847</div>
          <div class="stat-label">Active Nodes</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-block">
          <div class="stat-number">99.7%</div>
          <div class="stat-label">Uptime</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-block">
          <div class="stat-number">1.2ms</div>
          <div class="stat-label">Latency</div>
        </div>
      </div>
    </section>

    <!-- ==================== 颜色系统 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Color Palette</h2>
        <div class="section-line"></div>
        <p class="section-sub">8-color tactical system with functional semantics</p>
      </div>

      <div class="color-grid">
        <div class="color-swatch" v-for="color in colors" :key="color.name">
          <div class="color-box" :class="color.class"></div>
          <div class="color-label">{{ color.hex }}</div>
          <div class="color-name">{{ color.name }}</div>
        </div>
      </div>
    </section>

    <!-- ==================== 文字排版 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Typography</h2>
        <div class="section-line"></div>
        <p class="section-sub">Structured type system for rapid scanning</p>
      </div>

      <div class="two-col-layout">
        <div class="card-ghost">
          <div class="subsection-header-sm">
            <span class="indicator-line-sm"></span>
            <h4>Headings & Body</h4>
          </div>
          <div class="type-demo">
            <div class="type-item">
              <span class="type-tag">H1</span>
              <span class="text-h1">Heading One</span>
            </div>
            <div class="type-item">
              <span class="type-tag">H2</span>
              <span class="text-h2">Heading Two</span>
            </div>
            <div class="type-item">
              <span class="type-tag">H3</span>
              <span class="text-h3">Heading Three</span>
            </div>
            <div class="type-item">
              <span class="type-tag">BODY</span>
              <span class="text-body">Body text for paragraphs</span>
            </div>
            <div class="type-item">
              <span class="type-tag">CAPT</span>
              <span class="text-caption">Caption and small text</span>
            </div>
          </div>
        </div>

        <div class="card-ghost">
          <div class="subsection-header-sm">
            <span class="indicator-line-sm"></span>
            <h4>Data Panel</h4>
          </div>
          <div class="type-demo">
            <div class="type-item">
              <span class="type-tag">LABEL</span>
              <span class="text-label">Temperature</span>
            </div>
            <div class="type-item">
              <span class="type-tag">METRIC</span>
              <span class="text-metric">36.5</span>
            </div>
            <div class="type-item">
              <span class="type-tag">UNIT</span>
              <span class="text-unit">°C</span>
            </div>
            <div class="type-item">
              <span class="type-tag">S-MET</span>
              <span class="text-metric-sm">1,024</span>
            </div>
            <div class="type-item">
              <span class="type-tag">B-SM</span>
              <span class="text-body-sm">Secondary body text with moderate emphasis</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 按钮系统 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Button System</h2>
        <div class="section-line"></div>
        <p class="section-sub">Electronic feedback with 0.08s response time</p>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <span class="indicator-line"></span>
          <h3>Solid Buttons</h3>
        </div>
        <div class="button-demo">
          <button class="btn-primary">PRIMARY</button>
          <button class="btn-secondary">SECONDARY</button>
          <button class="btn-success">SUCCESS</button>
          <button class="btn-warning">WARNING</button>
          <button class="btn-error">ERROR</button>
        </div>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <span class="indicator-line"></span>
          <h3>Size Variants</h3>
        </div>
        <div class="button-demo">
          <button class="btn-primary">DEFAULT</button>
          <button class="btn-primary-sm">COMPACT</button>
          <button class="btn-outline">OUTLINE</button>
          <button class="btn-outline-sm">OUTLINE SM</button>
        </div>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <span class="indicator-line"></span>
          <h3>Ghost & Block</h3>
        </div>
        <div class="button-demo">
          <button class="btn-ghost">GHOST</button>
          <button class="btn-ghost-sm">GHOST SM</button>
          <button class="btn-error-block">CRITICAL ACTION</button>
        </div>
      </div>
    </section>

    <!-- ==================== 输入框系统 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Input System</h2>
        <div class="section-line"></div>
        <p class="section-sub">Box-shadow focus ring with zero layout shift</p>
      </div>

      <div class="two-col-layout">
        <div class="demo-card">
          <div class="subsection-header-sm">
            <span class="indicator-line-sm"></span>
            <h4>Text Inputs</h4>
          </div>
          <div class="input-demo" style="flex-direction: column; align-items: flex-start;">
            <input type="text" class="input-industrial" placeholder="Enter node ID...">
            <input type="text" class="input-industrial" placeholder="Disabled input" disabled>
            <div class="input-tip">FOCUS: box-shadow ring, no reflow</div>
          </div>
        </div>

        <div class="demo-card">
          <div class="subsection-header-sm">
            <span class="indicator-line-sm"></span>
            <h4>Search Box</h4>
          </div>
          <div class="search-box-industrial">
            <input type="text" placeholder="Search modules...">
            <button>SCAN</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 分子组件 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Molecular Components</h2>
        <div class="section-line"></div>
        <p class="section-sub">Composable UI units</p>
      </div>

      <div class="two-col-layout">
        <div class="demo-card">
          <div class="subsection-header-sm">
            <span class="indicator-line-sm"></span>
            <h4>User Card</h4>
          </div>
          <div class="user-card-industrial" v-for="user in users" :key="user.name" style="margin-bottom: 12px;">
            <div class="avatar-industrial"></div>
            <div class="user-info">
              <div class="user-name">{{ user.name }}</div>
              <div class="user-role">{{ user.role }}</div>
            </div>
            <button class="follow-btn">TRACK</button>
          </div>
        </div>

        <div class="demo-card">
          <div class="subsection-header-sm">
            <span class="indicator-line-sm"></span>
            <h4>Rating</h4>
          </div>
          <div class="rating-industrial" style="margin-bottom: 20px;">
            <div class="stars">
              <span v-for="i in 5" :key="i" class="star" :class="{ active: i <= rating }" @click="rating = i">◆</span>
            </div>
            <div class="rating-text">{{ rating }} / 5 — Threat Level {{ threatLevel }}</div>
          </div>

          <div class="subsection-header-sm" style="margin-top: 24px;">
            <span class="indicator-line-sm"></span>
            <h4>Menu</h4>
          </div>
          <div class="menu-industrial">
            <div class="menu-item-industrial" :class="{ active: activeMenu === 0 }" @click="activeMenu = 0">
              <span class="menu-icon">◈</span>
              System Overview
              <span class="menu-arrow">→</span>
            </div>
            <div class="menu-item-industrial" :class="{ active: activeMenu === 1 }" @click="activeMenu = 1">
              <span class="menu-icon">◇</span>
              Network Graph
              <span class="menu-arrow">→</span>
            </div>
            <div class="menu-item-industrial" :class="{ active: activeMenu === 2 }" @click="activeMenu = 2">
              <span class="menu-icon">◆</span>
              Security Logs
              <span class="menu-arrow">→</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 文章列表 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Article List</h2>
        <div class="section-line"></div>
        <p class="section-sub">High-density information scanning pattern</p>
      </div>

      <div class="article-list-industrial">
        <div class="article-item-industrial" v-for="(article, index) in articles" :key="index">
          <div class="article-rank">{{ String(index + 1).padStart(2, '0') }}</div>
          <div class="article-content">
            <div class="article-title">{{ article.title }}</div>
            <div class="article-meta">
              <span>{{ article.author }}</span>
              <span class="meta-divider">|</span>
              <span>{{ article.date }}</span>
              <span class="meta-divider">|</span>
              <span>{{ article.readTime }}</span>
            </div>
            <div class="article-summary">{{ article.summary }}</div>
          </div>
          <div class="article-link">READ →</div>
        </div>
      </div>
    </section>

    <!-- ==================== 表单 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Form System</h2>
        <div class="section-line"></div>
        <p class="section-sub">Validation with tactical feedback</p>
      </div>

      <div class="form-industrial">
        <div class="form-group-industrial">
          <label>Node Identifier <span class="required">*</span></label>
          <input type="text" placeholder="e.g., NODE-0421">
          <div class="helper-text">Alphanumeric, 8-16 characters</div>
        </div>

        <div class="form-group-industrial">
          <label>Access Key <span class="required">*</span></label>
          <input type="text" placeholder="Enter encryption key">
          <div class="helper-text">256-bit key required</div>
        </div>

        <div class="form-group-industrial error">
          <label>Port Number <span class="required">*</span></label>
          <input type="text" value="99999">
          <div class="error-text">Invalid port range (1-65535)</div>
        </div>
      </div>
    </section>

    <!-- ==================== 模板布局 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Template Layouts</h2>
        <div class="section-line"></div>
        <p class="section-sub">Modular page structures</p>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <span class="indicator-line"></span>
          <h3>Two-Column with Sidebar</h3>
        </div>
        <div class="layout-two-col-industrial">
          <div class="sidebar-industrial">
            <div class="sidebar-menu-item active">Dashboard</div>
            <div class="sidebar-menu-item">Analytics</div>
            <div class="sidebar-menu-item">Nodes</div>
            <div class="sidebar-divider"></div>
            <div class="sidebar-menu-item">Settings</div>
            <div class="sidebar-menu-item">Logs</div>
          </div>
          <div class="main-content-industrial">
            <div class="content-card">
              <div class="text-label">System Load</div>
              <div class="text-metric-sm">47%</div>
            </div>
            <div class="content-card">
              <div class="text-label">Active Threads</div>
              <div class="text-metric-sm">128</div>
            </div>
          </div>
        </div>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <span class="indicator-line"></span>
          <h3>3-Column Mini Cards</h3>
        </div>
        <div class="grid-3-col">
          <div class="mini-card">
            CPU
            <span class="mini-num">23%</span>
          </div>
          <div class="mini-card">
            MEMORY
            <span class="mini-num">8.2GB</span>
          </div>
          <div class="mini-card">
            DISK IO
            <span class="mini-num">340MB/s</span>
          </div>
        </div>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <span class="indicator-line"></span>
          <h3>Feature Grid</h3>
        </div>
        <div class="grid-3-col-industrial">
          <div class="grid-card" v-for="feature in features" :key="feature.title">
            <div class="grid-icon">{{ feature.icon }}</div>
            <div class="grid-title">{{ feature.title }}</div>
            <div class="grid-desc">{{ feature.desc }}</div>
            <div class="grid-link">CONFIGURE →</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 仪表盘页面 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Dashboard Page</h2>
        <div class="section-line"></div>
        <div class="section-sub" style="display: flex; align-items: center;">
          Real-time monitoring panel
          <button class="demo-focus-btn" @click="showOverlay = !showOverlay">
            {{ showOverlay ? 'CLOSE FOCUS' : 'TRIGGER FOCUS' }}
          </button>
        </div>
      </div>

      <div class="dashboard-industrial" :class="{ 'has-overlay': showOverlay }">
        <div class="focus-overlay-demo" v-if="showOverlay">
          <div class="focus-content">
            <div class="focus-close" @click="showOverlay = false">✕</div>
            <div class="focus-title">CRITICAL ALERT</div>
            <div class="focus-desc">
              Anomaly detected in Node Cluster 7. Traffic spike of 340% above baseline.
              Immediate investigation required.
            </div>
            <button class="btn-primary" @click="showOverlay = false">ACKNOWLEDGE</button>
            <button class="btn-ghost" style="margin-left: 8px;" @click="showOverlay = false">DISMISS</button>
          </div>
        </div>

        <div class="stats-grid-industrial">
          <div class="stat-card-industrial" v-for="stat in dashboardStats" :key="stat.label">
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-trend">{{ stat.trend }}</div>
          </div>
        </div>

        <div class="activity-industrial">
          <div class="activity-header">
            <span>SYSTEM ACTIVITY</span>
            <span class="text-caption">Last 24 hours</span>
          </div>
          <div class="activity-list">
            <div class="activity-item" v-for="(activity, index) in activities" :key="index">
              <span class="activity-dot"></span>
              <span>{{ activity.event }}</span>
              <span class="activity-time">{{ activity.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 设置页面 ==================== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Settings Page</h2>
        <div class="section-line"></div>
        <p class="section-sub">Tactical configuration panel</p>
      </div>

      <div class="settings-industrial">
        <div class="settings-group">
          <div class="settings-title">// NOTIFICATIONS</div>
          <div class="setting-row">
            <span>Alert Sounds</span>
            <div class="setting-control">
              <span class="toggle-on">ENABLED</span>
              <span class="setting-hint">WAV</span>
            </div>
          </div>
          <div class="setting-row">
            <span>Desktop Push</span>
            <div class="setting-control">
              <span class="toggle-on">ENABLED</span>
              <span class="setting-hint">HTTPS</span>
            </div>
          </div>
          <div class="setting-row">
            <span>Email Digest</span>
            <div class="setting-control">
              <span class="toggle-off">DISABLED</span>
            </div>
          </div>
        </div>

        <div class="settings-group">
          <div class="settings-title">// SECURITY</div>
          <div class="setting-row">
            <span>2FA Authentication</span>
            <div class="setting-control">
              <span class="toggle-on">ACTIVE</span>
              <span class="setting-hint">TOTP</span>
            </div>
          </div>
          <div class="setting-row">
            <span>Session Timeout</span>
            <div class="setting-control">
              <span class="setting-hint">15 min</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 页脚 ==================== -->
    <footer class="system-footer">
      <div class="footer-line"></div>
      <div class="footer-content">
        <div>
          <div class="footer-logo">SYS.TERMINAL</div>
          <div class="footer-desc">
            Modular infrastructure monitoring platform. Designed for high-density data operations.
          </div>
        </div>
        <div class="footer-buttons">
          <button class="btn-outline-sm">DOCS</button>
          <button class="btn-primary-sm">UPGRADE</button>
        </div>
      </div>
      <div class="footer-copyright">
        <span>SYS.TERMINAL v2.4.1</span>
        <span>BUILD: 2026-05-21-0421</span>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'DesignSystemDemo',
  data() {
    return {
      activeNav: 1,
      activeMenu: 0,
      rating: 4,
      showOverlay: false,

      navItems: ['TERMINAL', 'MONITOR', 'ANALYTICS', 'SECURITY'],

      colors: [
        { name: 'Primary', class: 'primary', hex: '#53b0ff' },
        { name: 'Primary Deep', class: 'primary-deep', hex: '#000eff' },
        { name: 'Secondary', class: 'secondary', hex: '#7200ff' },
        { name: 'Accent', class: 'accent', hex: '#f86eff' },
        { name: 'Warning', class: 'warning', hex: '#ffec7b' },
        { name: 'Success', class: 'success', hex: '#51ffd6' },
        { name: 'Error', class: 'error', hex: '#ff0072' },
      ],

      users: [
        { name: 'K. Reeves', role: 'SysAdmin' },
        { name: 'M. ONeill', role: 'SecOps' },
      ],

      articles: [
        {
          title: 'Protocol Hardening: Mitigating Side-Channel Attacks',
          author: 'C. Voss',
          date: '2026-05-18',
          readTime: '8 min',
          summary: 'Analysis of recent attack vectors targeting unencrypted metadata in distributed node networks and countermeasure deployment strategies.'
        },
        {
          title: 'Grid Topology Optimization for Sub-2ms Latency',
          author: 'J. Chen',
          date: '2026-05-15',
          readTime: '12 min',
          summary: 'Refactored routing algorithms reduce inter-node latency by 34% in mesh configurations exceeding 500 active endpoints.'
        },
        {
          title: 'Firmware v4.2.0: Changelog and Migration Guide',
          author: 'Ops Team',
          date: '2026-05-10',
          readTime: '6 min',
          summary: 'New encryption handshake protocol, improved failover logic, and deprecated API endpoint removal schedule.'
        },
      ],

      features: [
        {
          icon: '◈',
          title: 'Real-time Metrics',
          desc: 'Sub-second data pipeline with configurable polling intervals. Zero interpolation artifacts.'
        },
        {
          icon: '◆',
          title: 'Threat Detection',
          desc: 'Behavioral anomaly engine with 97.3% detection rate. False positive suppression via ML filtering.'
        },
        {
          icon: '◇',
          title: 'Auto-scaling',
          desc: 'Dynamic node allocation based on load prediction models. Scale from 10 to 10,000 nodes in under 60s.'
        },
      ],

      dashboardStats: [
        { label: 'Active Nodes', value: '2,847', trend: '↑ 12.4%' },
        { label: 'Throughput', value: '340MB/s', trend: '↑ 8.1%' },
        { label: 'Error Rate', value: '0.03%', trend: '↓ 0.01%' },
        { label: 'Response Time', value: '1.2ms', trend: '↓ 3.2%' },
      ],

      activities: [
        { event: 'Node CLUSTER-7 auto-scaled to 48 instances', time: '14:32:05' },
        { event: 'Security scan completed: 0 vulnerabilities', time: '14:28:11' },
        { event: 'Firmware update staged for CLUSTER-3', time: '14:15:44' },
        { event: 'Anomaly detected: Traffic spike +340%', time: '13:58:02' },
        { event: 'Backup completed: 2.4TB in 18.3s', time: '13:45:00' },
      ],
    }
  },
  computed: {
    threatLevel() {
      const levels = ['NONE', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL']
      return levels[this.rating - 1] || 'NONE'
    }
  }
}
</script>




<style lang="scss" scoped>
// 请确保此处的引入路径与你的项目结构一致（如果 tokens 在同级目录，可改为 ./design-tokens.scss）
@import './test_scss.scss';
</style>