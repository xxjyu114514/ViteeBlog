---

# ViteeBlog CSS/SCSS 开发规范 (Style Guide)

本手册旨在指导项目样式的后续开发，确保在代码规模增长时，样式依然保持**可维护性、一致性**且**不冗余**。

---

## 一、 核心架构说明

项目采用分层 SCSS 架构，各层级职责明确：

1.  **`_variables.scss` (变量层)**：存储全局色值、间距、圆角、阴影等。**禁止**在业务代码中使用硬编码的颜色（如 `#ffffff`），必须引用变量。
2.  **`_mixins.scss` (工具层)**：存储复用逻辑，如玻璃拟态效果、Markdown 排版、居中对齐、动画定义。
3.  **`_base.scss` (公共组件层)**：存放全站通用的 UI 组件样式，如 `btn-primary`、`modal-overlay`、`form-group`。
4.  **`views.scss` (业务层)**：按照视图模块组织的页面样式。

---

## 二、 命名规范 (Naming)

采用 **BEM (Block Element Modifier)** 的简化思路或**语义化类名**：

* **容器/块 (Block)**：描述功能或页面。例如：`.article-card`、`.login-page`。
* **元素 (Element)**：块内部的组成部分。使用单个短横线连接。例如：`.article-title`、`.login-form`。
* **修饰符 (Modifier)**：描述状态或变体。例如：`.btn-primary`、`.tag-item.active`、`.back-button.light`。

---

## 三、 代码书写顺序 (Declaration Order)

为了提高代码可读性，建议按照“从外向内”的逻辑排序属性：

1.  **定位属性**：`position`, `top`, `left`, `z-index`, `display`, `float`
2.  **尺寸与盒模型**：`width`, `height`, `margin`, `padding`, `border`, `border-radius`
3.  **排版样式**：`font-size`, `font-weight`, `line-height`, `color`, `text-align`
4.  **视觉效果**：`background`, `box-shadow`, `opacity`, `filter`
5.  **其他**：`transition`, `cursor`, `pointer-events`

---

## 四、 如何添加新样式 (Workflow)

### 1. 添加一个新页面样式
如果新增了 `FriendLink.vue` 页面：
1. 在 `views.scss` 中添加注释块 `/* FriendLink 友情链接 */`。
2. 以最外层容器 `.friend-link-wrapper` 包裹所有代码，限制作用域。
3. **优先检查**：新页面的按钮或输入框是否可以直接使用 `_base.scss` 里的通用类。

### 2. 添加一个新的全局组件
如果新增了一个通用的通知栏组件：
1. 在 `_base.scss` 中编写类名 `.notice-bar`。
2. 确保它不依赖于任何特定页面的层级结构。

### 3. 定义新的颜色或常量
1. 在 `_variables.scss` 中定义 `$color-brand-new: #xxxxxx;`。
2. 在业务代码中使用：`background: $color-brand-new;`。

---

## 五、 样式复用与优化 (Best Practices)

### 1. 玻璃拟态 (Glassmorphism)
如果需要给文字添加你标志性的玻璃透明渐变效果，请直接调用：
```scss
.my-new-title {
  @include glass-text-effect(2rem, 600);
}
```

### 2. Markdown 内容渲染
如果你在新的页面需要显示 Markdown 渲染的内容，请务必嵌套该 mixin 以保证排版统一：
```scss
.new-content-area {
  @include markdown-typography;
}
```

### 3. 避免过深嵌套
SCSS 的嵌套**严禁超过 3 层**（除非是处理复杂的第三方库结构）。
* ❌ **错误**：`.view > .container > .list > .item > .link > span`
* ✅ **正确**：`.view-list { ... } .list-item-link { ... }`

---

## 六、 常用变量速查

* **主色调**：`$color-primary` (#3b82f6)
* **危险色**：`$color-danger` (#ef4444)
* **成功色**：`$color-success` (#10b981)
* **深色背景**：`$bg-dark` (#111)
* **浅灰色文字**：`$text-muted` (#6b7280)

---

**保持代码整洁，就是对项目未来的自己负责。**