# 迪士尼 RAG 助手 — Web 前端界面规范 (UI SPEC)

> 本规范以 `docs/design-a-optimized.html` 为唯一设计基准，所有前端开发必须严格遵循本文档定义的样式、布局和交互。

## 1. 概述

迪士尼 RAG 客服助手的 Web 交互界面，采用"经典迪士尼"风格：酒红+金色暖色调、圆角气泡、梦幻感装饰。提供完整的对话交互、知识库浏览、检索结果展示功能。

## 2. 技术栈

### 2.1 核心框架

| 项目 | 选型 | 说明 |
|------|------|------|
| 框架 | **React 18+** | 组件化开发，Hooks 管理状态 |
| 构建工具 | **Vite 5+** | 快速开发服务器，ESM 打包 |
| 语言 | **TypeScript 5+** | 类型安全，组件 Props/State 约束 |
| 路由 | **React Router v6** | 支持多页面路由和嵌套路由 |
| 样式方案 | **CSS Modules / 原生 CSS** | 保留设计令牌变量，保持与原型一致的 CSS 变量体系 |
| HTTP 客户端 | **fetch / axios** | 调用后端 RAG API |

### 2.2 项目结构

```
disney-web/
├── public/                          # 静态资源
│   └── favicon.ico
├── src/
│   ├── assets/                      # 图片、字体等静态资源
│   ├── components/                  # 通用组件
│   │   ├── TopNav/                  # 顶部导航栏
│   │   ├── Sidebar/                 # 知识库侧边栏
│   │   ├── ChatHeader/              # 聊天头部
│   │   ├── MessageList/             # 消息列表
│   │   ├── MessageBubble/           # 单条消息气泡
│   │   ├── InputBar/                # 输入栏
│   │   ├── WelcomeCard/             # 欢迎卡片
│   │   ├── ResourceTag/             # 资源标签
│   │   ├── TypingIndicator/         # 打字指示器
│   │   └── ChatLayout/              # 主布局容器（Nav + Sidebar + Chat）
│   ├── pages/                       # 页面组件（路由入口）
│   │   ├── ChatPage/                # 智能问答页（主页面）
│   │   ├── KnowledgePage/           # 知识库浏览页
│   │   ├── GuidePage/               # 游园指南页
│   │   └── HelpPage/                # 帮助中心页
│   ├── hooks/                       # 自定义 Hooks
│   │   ├── useChat.ts               # 聊天逻辑（发送/接收/状态）
│   │   └── useSidebar.ts            # 侧边栏状态管理
│   ├── services/                    # API 服务层
│   │   └── ragApi.ts                # RAG 查询 API 封装
│   ├── types/                       # TypeScript 类型定义
│   │   └── index.ts                 # Message, Category, ApiResponse 等
│   ├── styles/                      # 全局样式
│   │   ├── tokens.css               # 设计令牌（CSS 变量）
│   │   ├── animations.css           # 公共动画（fadeInUp, sparkle-float 等）
│   │   └── global.css               # 重置 + 全局样式
│   ├── App.tsx                      # 路由配置 + 根组件
│   └── main.tsx                     # 入口文件
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

### 2.3 路由设计

```
/              → ChatPage（智能问答页，默认首页）
/knowledge     → KnowledgePage（知识库浏览页）
/guide         → GuidePage（游园指南页）
/help          → HelpPage（帮助中心页）
```

- 使用 `react-router-dom` 的 `BrowserRouter` + `Routes` + `Route`
- `ChatLayout` 作为共享布局（顶部导航栏 + 侧边栏），各页面共享同一套导航和侧边栏，仅中间内容区域切换
- 导航链接高亮通过 `useLocation` 判断当前路径实现

### 2.4 状态管理

- 聊天消息列表使用 `useState` + `useRef` 管理
- 侧边栏分类状态使用 `useState`（可后续升级为 `useReducer` 或 Context）
- 全局共享数据（如知识库分类列表）使用 `React.createContext` + `useContext`

### 2.5 开发约定

- 所有组件使用函数式组件 + Hooks
- 组件 Props 使用 TypeScript interface 定义
- CSS 变量统一在 `tokens.css` 中声明，组件内通过 `var(--xxx)` 引用
- 动画类名统一定义在 `animations.css` 中
- 组件文件名使用 PascalCase（如 `MessageBubble.tsx`），样式文件同名（`MessageBubble.module.css` 或 `MessageBubble.css`）

## 3. 设计令牌 (Design Tokens)

### 2.1 颜色

| 令牌 | 值 | 用途 |
|------|-----|------|
| `--burgundy-deep` | `#3d0f1a` | 导航栏深色背景、用户消息渐变起点 |
| `--burgundy` | `#6b1d2a` | 导航栏主色、用户消息渐变终点、侧边栏活跃文字 |
| `--burgundy-light` | `#8a2e40` | 用户消息渐变辅助色 |
| `--gold` | `#d4a843` | 主要强调色：金色分隔线、活跃指示器、按钮 |
| `--gold-light` | `#f0d68a` | 金色文字、hover 高亮、图标渐变终点 |
| `--gold-pale` | `#f9eeb8` | 星星装饰径向渐变 |
| `--cream` | `#fdf6e3` | 页面主背景色 |
| `--cream-warm` | `#fef9ef` | 侧边栏/消息气泡背景 |
| `--cream-dark` | `#f5ebd0` | 键盘快捷键标签背景 |
| `--purple` | `#7b2d8e` | 背景径向渐变装饰点缀 |
| `--brown-dark` | `#3a2a1a` | 主文字色 |
| `--brown` | `#5a4030` | 次要文字色 |
| `--brown-light` | `#8a7060` | 占位符/标签/辅助文字 |
| `--warm-shadow` | `rgba(107,29,42,0.12)` | 常规阴影 |
| `--warm-shadow-lg` | `rgba(107,29,42,0.2)` | 大阴影（导航栏、输入框） |

### 2.2 字体

| 令牌 | 值 | 用途 |
|------|-----|------|
| `--font-display` | `'ZCOOL XiaoWei', 'Noto Serif SC', serif` | 品牌标题、导航文字 |
| `--font-body` | `'Noto Sans SC', sans-serif` | 正文字体、输入框、消息 |
| `--font-serif` | `'Noto Serif SC', serif` | 聊天标题、侧边栏标题、欢迎卡片标题 |

### 2.3 圆角

| 令牌 | 值 | 用途 |
|------|-----|------|
| `--radius-sm` | `8px` | 侧边栏项目、导航链接、小按钮 |
| `--radius-md` | `14px` | 消息气泡 |
| `--radius-lg` | `20px` | 输入框容器、欢迎卡片 |
| `--radius-xl` | `28px` | 保留 |

### 2.4 动画曲线

| 令牌 | 值 |
|------|-----|
| `--transition` | `0.25s cubic-bezier(0.4, 0, 0.2, 1)` |

### 2.5 基准字号

| 元素 | 大小 | 字重 |
|------|------|------|
| `html` 基准 | `15px` | — |
| 导航品牌 | `1.2rem` | — |
| 导航副标题 | `0.62rem` | `400`，`letter-spacing: 0.15em` |
| 导航链接 | `0.88rem` | `400`（活跃时 `500`） |
| 侧边栏标题 | `0.92rem` | `700` |
| 侧边栏分组标签 | `0.65rem` | `600`，大写，`letter-spacing: 0.1em` |
| 侧边栏项目 | `0.82rem` | `400`（活跃时 `600`） |
| 侧边栏角标 | `0.62rem` | `500` |
| 侧边栏底部状态 | `0.72rem` | — |
| 聊天标题 | `1rem` | `700` |
| 聊天副标题 | `0.72rem` | — |
| 消息内容 | `0.85rem` | —，`line-height: 1.7` |
| 消息发送者标签 | `0.68rem` | `600`，`opacity: 0.6` |
| 资源标签 | `0.68rem` | `500` |
| 输入框文字 | `0.88rem` | — |
| 快捷键提示 | `0.65rem` | — |
| 欢迎卡片标题 | `1.1rem` | — |
| 欢迎卡片正文 | `0.82rem` | —，`line-height: 1.6` |
| 建议按钮 | `0.75rem` | — |

## 4. 整体布局

```
┌──────────────────────────────────────────────────────┐
│                    TOP NAVIGATION (64px)              │
│  [Logo + 城堡]  [导航链接]                [通知][头像] │
├────────────┬─────────────────────────────────────────┤
│            │  Chat Header (头像+标题+状态+操作按钮)    │
│  SIDEBAR   ├─────────────────────────────────────────┤
│  (230px)   │                                         │
│            │           MESSAGES AREA                  │
│  [搜索]    │           (flex: 1, scroll)              │
│  [分类1]   │                                         │
│  [分类2]   │                                         │
│  ...       │                                         │
│            ├─────────────────────────────────────────┤
│  [状态栏]  │  INPUT BAR (textarea + 工具 + 发送按钮)   │
└────────────┴─────────────────────────────────────────┘
```

- 页面占满 `100vh`，`overflow: hidden`，禁止页面级滚动
- 仅消息区域 (`messages`) 可滚动
- 侧边栏内部可滚动

### 4.1 响应式断点

| 断点 | 行为 |
|------|------|
| `> 900px` | 完整布局：侧边栏 `230px` + 导航链接可见 |
| `641px – 900px` | 侧边栏缩至 `200px`，导航链接隐藏 |
| `≤ 640px` | 侧边栏完全隐藏，内边距缩减，消息气泡放宽至 `90%` |

## 5. 组件规范

### 5.1 顶部导航栏 (`.top-nav`)

**结构**
```
.top-nav (h: 64px)
  ├─ .logo
  │   ├─ .logo-castle (CSS 城堡图标)
  │   │   ├─ .tower × 5 (5 个塔)
  │   │   ├─ .wall (底部城墙)
  │   │   └─ .flag (中心塔旗帜)
  │   └─ .logo-text
  │       ├─ .brand ("迪士尼魔法助手")
  │       └─ .subtitle ("RAG Knowledge Assistant")
  ├─ .nav-links
  │   └─ li > a (智能问答 / 知识库 / 游园指南 / 帮助中心)
  └─ .nav-user
      ├─ .notification (铃铛 + .badge 红点)
      └─ .avatar (用户首字圆形头像)
```

**样式要点**
- 背景：`linear-gradient(180deg, --burgundy-deep, --burgundy)`
- 底部金线：`::after` 伪元素，`linear-gradient(90deg, transparent, --gold, --gold-light, --gold, transparent)`，高度 `2px`
- 阴影：`0 2px 20px --warm-shadow-lg, 0 1px 4px rgba(0,0,0,0.3)`
- 水平内边距：`0 32px`

**城堡 Logo 细节**
- 5 个塔，宽度各 `6px`，高度依次为 `20/26/32/26/20px`
- 每个塔顶部有三角形尖顶（`::before` 伪元素，`border` 技巧绘制）
- 中心塔尖顶更大（边框 `5px`，高度 `9px`）
- 底部城墙 `42px × 8px`，底部圆角 `4px`
- 中心塔顶有旗帜（`clip-path: polygon(0 0, 100% 30%, 0 100%)`）

**交互**
- 导航链接 `a`：hover 时 `color: --cream`，`background: rgba(255,255,255,0.06)`
- 活跃链接：`color: --gold-light`，`font-weight: 500`，底部 `20px` 宽金色下划线（`::after`）
- 通知铃铛 hover：`background: rgba(255,255,255,0.12)`
- 头像：金色渐变背景，金色边框 `2px rgba(240,214,138,0.3)`

### 5.2 侧边栏 (`.sidebar`)

**结构**
```
.sidebar (w: 230px)
  ├─ .sidebar-header
  │   └─ h3 > .icon + "知识分类"
  ├─ .sidebar-search
  │   └─ .sidebar-search-wrapper > input (placeholder: "搜索分类...")
  ├─ .sidebar-list (可滚动)
  │   ├─ .sidebar-group-label ("园区服务")
  │   ├─ .sidebar-item × N (含 .item-icon + 文字 + .item-badge)
  │   ├─ .sidebar-group-label ("实用信息")
  │   └─ .sidebar-item × N
  └─ .sidebar-footer
      └─ .status-dot + "知识库已更新 · 346 条记录"
```

**样式要点**
- 背景：`linear-gradient(180deg, --cream-warm, --cream)`
- 右边框：`1px solid rgba(212,168,67,0.2)`
- 右侧阴影：`2px 0 12px --warm-shadow`
- 顶部内边距：`20px 20px 14px`
- 标题底部虚线分隔：`1px dashed rgba(212,168,67,0.3)`

**搜索框**
- 搜索图标：`::before`（圆环 `13px`）+ `::after`（手柄 `4px × 1.5px`，旋转 45°）
- 输入框：`padding: 8px 12px 8px 32px`
- 焦点状态：`border-color: --gold`，`box-shadow: 0 0 0 3px rgba(212,168,67,0.12)`

**分类项目**
- 基础：`padding: 9px 12px`，`border-radius: --radius-sm`
- 图标 `.item-icon`：`20px × 20px`，`border-radius: 6px`，背景 `rgba(212,168,67,0.15)`
- Hover：`background: rgba(212,168,67,0.1)`，图标 `transform: scale(1.1)`
- 活跃状态：
  - 左侧金色竖线 `::before`：`width: 3px`，`border-radius: 0 2px 2px 0`，背景 `--gold`
  - 背景渐变：`linear-gradient(135deg, rgba(212,168,67,0.18), rgba(212,168,67,0.08))`
  - 文字：`color: --burgundy`，`font-weight: 600`
  - 图标：`background: linear-gradient(135deg, --gold, --gold-light)`，文字 `--burgundy-deep`
  - 角标：`background: --burgundy`，`color: --cream`

**角标 `.item-badge`**
- `padding: 1px 7px`，`border-radius: 10px`
- 默认：`background: rgba(212,168,67,0.12)`，`color: --brown-light`

**底部状态**
- 顶部虚线分隔：`1px dashed rgba(212,168,67,0.3)`
- 绿色状态点：`7px × 7px`，`border-radius: 50%`，`background: #4ade80`，`box-shadow: 0 0 6px rgba(74,222,128,0.4)`

**分类列表（共 9 项）**

| 分组 | 分类 | 图标文字 | 角标数 |
|------|------|---------|--------|
| 园区服务 | 园区门票 | 票 | 32 |
| | 酒店住宿 | 宿 | 18 |
| | 餐饮美食 | 餐 | 24 |
| | 巡游演出 | 演 | 45 |
| 实用信息 | 快速通行证 | 快 | 12 |
| | 季节活动 | 节 | 38 |
| | 交通指南 | 行 | 15 |
| | 购物推荐 | 购 | 21 |
| | 游客服务 | 务 | 28 |

### 5.3 聊天头部 (`.chat-header`)

**结构**
```
.chat-header
  ├─ .chat-header-left
  │   ├─ .chat-header-avatar
  │   │   ├─ .mini-castle ("✦")
  │   │   └─ .online-dot (绿色在线状态)
  │   └─ .chat-header-info
  │       ├─ h2 ("迪士尼魔法客服助手")
  │       └─ p ("基于 346 条知识库记录 · 支持文本/图片/视频检索")
  └─ .chat-header-actions
      └─ .chat-header-btn × 2 (清除对话 / 设置)
```

**样式要点**
- `padding: 16px 28px`
- 背景：`rgba(253,246,227,0.8)` + `backdrop-filter: blur(12px)`
- 底部边框：`1px solid rgba(212,168,67,0.15)`
- 头像：`40px × 40px`，`border-radius: 50%`，背景 `linear-gradient(135deg, --burgundy, --burgundy-deep)`
- 在线状态点：`10px × 10px`，`border: 2px solid --cream`
- 操作按钮：`34px × 34px`，`border-radius: 50%`，`border: 1.5px solid rgba(212,168,67,0.2)`
- 按钮 hover：`border-color: --gold`，`background: rgba(212,168,67,0.08)`

### 5.4 消息区域 (`.messages`)

**结构**
```
.messages (flex: 1, overflow-y: auto, scroll-behavior: smooth)
  ├─ .welcome-card (初始显示)
  │   ├─ .welcome-icon ("✦")
  │   ├─ h3
  │   ├─ p
  │   └─ .welcome-suggestions
  │       └─ .welcome-suggestion × 4
  └─ .message (用户发送后追加)
      ├─ .message-avatar
      └─ .message-bubble
          ├─ .sender
          ├─ .text
          └─ .resource-tag × N (仅 Bot 消息)
```

**欢迎卡片**
- 居中：`align-self: center`，`max-width: 480px`，`text-align: center`
- `padding: 28px 40px`
- 背景：`linear-gradient(135deg, rgba(212,168,67,0.08), rgba(212,168,67,0.02))`
- 边框：`1px solid rgba(212,168,67,0.15)`
- `border-radius: --radius-lg`
- 入场动画：`fadeInUp 0.6s ease-out`

**建议按钮**
- `padding: 7px 14px`，`border-radius: 20px`
- 边框：`1.5px solid rgba(212,168,67,0.3)`
- Hover：`border-color: --gold`，`background: rgba(212,168,67,0.1)`，`color: --burgundy`

**消息气泡**
- 最大宽度：`75%`
- `gap: 12px`（头像与气泡间距）
- 入场动画：`fadeInUp 0.35s ease-out`

| 类型 | 头像背景 | 气泡背景 | 边框 | 文字色 | 圆角特征 |
|------|---------|---------|------|-------|---------|
| Bot | `linear-gradient(135deg, --burgundy, --burgundy-deep)`，金色文字 `✦` | `--cream-warm`，`border: 1px solid rgba(212,168,67,0.18)` | `border-left: 3px solid --gold` | `--brown-dark` | `border-top-left-radius: 4px` |
| User | `linear-gradient(135deg, --gold, --gold-light)`，酒红文字 `游` | `linear-gradient(135deg, --burgundy, --burgundy-light)` | 无 | `--cream` | `border-bottom-right-radius: 4px` |

**资源标签 `.resource-tag`**
- `display: inline-flex`，`gap: 5px`，`margin-top: 10px`
- `padding: 4px 12px`，`border-radius: 12px`
- `font-size: 0.68rem`，`font-weight: 500`
- 背景：`linear-gradient(135deg, rgba(212,168,67,0.15), rgba(212,168,67,0.05))`
- 边框：`1px solid rgba(212,168,67,0.2)`
- 图标 `.tag-icon`：`14px × 14px`，`border-radius: 4px`，背景 `--gold`，文字 `--burgundy-deep`
- Hover：`background: linear-gradient(..., 0.25, 0.1)`，`transform: translateY(-1px)`

**打字指示器 `.typing-indicator`**
- 3 个圆点：`6px × 6px`，`border-radius: 50%`，背景 `--gold`
- 动画 `typing-bounce 1.2s ease-in-out infinite`，延迟分别为 `0s`、`0.15s`、`0.3s`
- 弹跳效果：`0%, 60%, 100% { translateY(0); opacity: 0.4 }`，`30% { translateY(-6px); opacity: 1 }`

### 5.5 输入栏 (`.input-bar`)

**结构**
```
.input-bar
  ├─ .input-wrapper
  │   ├─ textarea (id="chatInput", rows="1", placeholder="描述您的问题...")
  │   ├─ .input-tools
  │   │   ├─ .input-tool (上传图片 "▤")
  │   │   └─ .input-tool (语音输入 "◉")
  │   └─ .send-btn ("➤")
  └─ .input-footer
      ├─ .shortcut-hint ("<kbd>Enter</kbd> 发送 · <kbd>Shift+Enter</kbd> 换行")
      └─ "知识库索引 v2.1"
```

**样式要点**
- `padding: 16px 28px 20px`
- 背景：`linear-gradient(180deg, rgba(253,246,227,0.9), --cream-warm)`
- 顶部边框：`1px solid rgba(212,168,67,0.15)`

**输入容器 `.input-wrapper`**
- `display: flex`，`align-items: flex-end`，`gap: 12px`
- `padding: 8px 8px 8px 20px`
- 背景：`--cream-warm`
- 边框：`2px solid rgba(212,168,67,0.25)`
- `border-radius: --radius-lg`
- 阴影：`0 2px 8px --warm-shadow`
- 焦点状态：`border-color: --gold`，`box-shadow: 0 2px 16px --warm-shadow-lg, 0 0 0 4px rgba(212,168,67,0.1)`

**Textarea**
- 无边框、无背景、`outline: none`
- `font-size: 0.88rem`，`line-height: 1.5`
- `max-height: 80px`，自动调整高度（JS 监听 `input` 事件）
- 占位符颜色：`--brown-light`

**工具按钮 `.input-tool`**
- `36px × 36px`，`border-radius: 50%`，无边框，透明背景
- Hover：`background: rgba(212,168,67,0.12)`，`color: --burgundy`

**发送按钮 `.send-btn`**
- `42px × 42px`，`border-radius: 50%`
- 背景：`linear-gradient(135deg, --gold, --gold-light)`
- 文字：`--burgundy-deep`，`font-size: 1.1rem`
- 阴影：`0 2px 8px rgba(212,168,67,0.3)`
- Hover：`transform: scale(1.05)`，`box-shadow: 0 4px 16px rgba(212,168,67,0.4)`
- Active：`transform: scale(0.95)`

**底部提示 `.input-footer`**
- `margin-top: 8px`，`padding: 0 4px`
- `font-size: 0.65rem`，`color: --brown-light`
- `<kbd>` 元素：`padding: 1px 5px`，`border-radius: 3px`，`border: 1px solid rgba(90,64,48,0.2)`，`background: --cream-dark`

## 6. 装饰元素

### 6.1 背景纹理

- `body::before`：SVG `feTurbulence` 噪声纹理，`opacity: 0.018`，`position: fixed`，`pointer-events: none`

### 6.2 浮动星星 (`.sparkle-field`)

- 10 个 `.sparkle` 元素，`position: fixed`，分布在页面各处
- 每个星星：`4px × 4px`，圆形，背景 `--gold-light`
- `::after` 伪元素产生径向渐变光晕
- 动画 `sparkle-float 8s ease-in-out infinite`，各元素有不同 `animation-delay`（0-4.5s）和 `animation-duration`（7-11s）
- 动画轨迹：`translateY(0) scale(0.5), opacity 0` → `translateY(-120px) scale(1.2), opacity 0`

### 6.3 聊天区域背景渐变

```css
background:
  radial-gradient(ellipse at 20% 80%, rgba(212,168,67,0.04) 0%, transparent 50%),
  radial-gradient(ellipse at 80% 20%, rgba(123,45,142,0.03) 0%, transparent 50%),
  --cream;
```

## 7. 交互行为

### 7.1 消息发送

| 触发 | 行为 |
|------|------|
| 点击 `.send-btn` | 发送消息 |
| `Enter`（无 Shift） | 发送消息 |
| `Shift+Enter` | 输入框内换行 |
| 输入为空 | 不发送 |

**发送流程**
1. 读取输入框文本并 trim
2. 创建用户消息气泡（右侧，酒红渐变）
3. 清空输入框，重置高度
4. 移除欢迎卡片（首次发送时）
5. 显示打字指示器
6. 延迟 800-1600ms 后移除指示器
7. 创建 Bot 回复消息（左侧，金色左边框）

### 7.2 快捷问题

4 个预置建议，点击后自动填入对应文本并发送：

| 按钮文字 | 发送内容 |
|---------|---------|
| 万圣节有什么活动？ | 万圣节有什么特别活动？ |
| 邮轮价格查询 | 迪士尼邮轮的价格是多少？ |
| 快速通行证怎么用 | 园区快速通行证怎么用？ |
| 巡游演出时间 | 最近的巡游演出时间表 |

### 7.3 侧边栏切换

- 点击任意 `.sidebar-item`：移除其他项目的 `active` 类，为当前项目添加 `active` 类
- 默认活跃项：「园区门票」

### 7.4 导航链接切换

- 点击任意 `.nav-links a`：移除其他链接的 `active` 类，为当前链接添加 `active` 类
- 默认活跃项：「智能问答」

## 8. Bot 回复映射

| 用户输入 | 回复文本 | 资源标签 |
|---------|---------|---------|
| 万圣节有什么特别活动？ | 万圣节期间活动列表（巡游时间/美食/工坊） | `图 · 相关图片：2-万圣节.jpeg` |
| 迪士尼邮轮的价格是多少？ | 航线和舱位价格说明 | `图 · 迪士尼邮轮价格1.jpeg`、`图 · 迪士尼邮轮价格2.jpeg`、`图 · +7 张价格表` |
| 园区快速通行证怎么用？ | FastPass 三步使用流程 | `文 · 快速通行证完整指南 · 12条记录` |
| 最近的巡游演出时间表 | 日间/夜间巡游时间安排 | `文 · 巡游演出 · 45条记录` |
| 其他任意输入 | 通用匹配回复 | `文 · 匹配 3 条相关记录` |

## 9. 滚动条样式

| 区域 | 宽度 | 轨道 | 滑块 |
|------|------|------|------|
| `.sidebar-list` | `4px` | transparent | `rgba(212,168,67,0.2)`，`border-radius: 2px` |
| `.messages` | `5px` | transparent | `rgba(212,168,67,0.2)`，`border-radius: 3px` |

## 10. 字体加载

```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;600;700&family=ZCOOL+XiaoWei&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
```

实际使用的字体：`ZCOOL XiaoWei`（品牌/导航）、`Noto Serif SC`（标题/正文强调）、`Noto Sans SC`（正文/输入框）。`Playfair Display` 已加载但未使用，保留以备英文场景。

## 11. 文件引用

- 设计原型：`docs/design-a-optimized.html`
- 对比方案：`docs/page-designs.html`（方案 A 为基准）
- 后端索引：`4-disney_build_index.py`、`5-disney_query.py`
- 知识库数据：346 条记录（334 文本 + 11 图片 + 1 视频）
