---
name: "Nagnip-xu 作品官网"
description: "冷白展台：以真实界面与可探索的线路展示个人开发作品。"
colors:
  canvas: "#f4f5f7"
  accent: "#3d5fe0"
  signal: "#b3c6ff"
  ink: "#242730"
  paper: "#ffffff"
  white: "#fff"
  accent-ink: "#2b439d"
  body-copy: "#555b69"
  muted: "#626978"
  line: "#dce0e8"
  dark-line: "#505767"
  focus: "#1461ac"
  connection: "#e6ebf9"
  gallery-surface: "#edf0f5"
  gallery-caption: "#e2e7f0"
  console: "#303645"
  console-top: "#3c455a"
  console-copy: "#cdd3df"
typography:
  display:
    fontFamily: "Manrope, 'Showcase SC', 'Microsoft YaHei', sans-serif"
    fontSize: "clamp(44px, 4.65vw, 72px)"
    fontWeight: 750
    lineHeight: 1.28
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Manrope, 'Showcase SC', 'Microsoft YaHei', sans-serif"
    fontSize: "clamp(36px, 4.2vw, 60px)"
    fontWeight: 700
    lineHeight: 1.22
    letterSpacing: "-0.035em"
  title:
    fontFamily: "Manrope, 'Showcase SC', 'Microsoft YaHei', sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.22
  body:
    fontFamily: "Manrope, 'Showcase SC', 'Microsoft YaHei', sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "Manrope, 'Showcase SC', 'Microsoft YaHei', sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.7
rounded:
  image: "7px"
  control: "10px"
  window: "12px"
  mobile-button: "14px"
  console: "16px"
  button: "17px"
  tablet-nav: "18px"
  gallery: "20px"
  nav: "22px"
  pill: "30px"
  slab-mobile: "30px"
  slab-tablet: "36px"
  slab: "48px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  section-heading: "48px"
  panel-gap: "64px"
  slab-block: "90px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
    rounded: "{rounded.button}"
    padding: "10px 12px 10px 26px"
    height: "66px"
  button-inverse:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.button}"
    padding: "10px 12px 10px 26px"
    height: "66px"
  navigation:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.nav}"
    padding: "16px 24px"
    height: "76px"
  connection-chip:
    backgroundColor: "{colors.connection}"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.pill}"
    padding: "10px 16px"
  gallery-tab:
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "10px 24px"
  gallery-tab-selected:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
    rounded: "{rounded.pill}"
    padding: "10px 24px"
  next-step:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.white}"
    rounded: "{rounded.pill}"
    padding: "12px 18px"
    height: "46px"
  demo-console:
    backgroundColor: "{colors.console}"
    textColor: "{colors.white}"
    rounded: "{rounded.console}"
  file-copy:
    backgroundColor: "#e7ebf3"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
    height: "46px"
---

# Design System: Nagnip-xu 作品官网

## Overview

**Creative North Star: "冷白展台"**

本系统只约束 `website/` 的静态中文作品官网；Python / Tkinter 桌面应用及其截图内部样式均在边界之外。它将冷白底色、石墨大字、白色浮动导航和纯白内容板组合成清晰、克制的作品展台。钴蓝只承担动作、线路和选择反馈，真实窗口是视觉证据。

页面以宽留白和大尺度圆角区分阅读段落，以石墨色区域承载可操作的机制说明及收尾。动态围绕箭头、线路和明确状态展开，默认内容始终可见。用户已明确否定绿色系列背景，因此原 `sd-seedbed-lobes` 只保留为结构来源的历史记录，不再是颜色权威；此文档记录替换配色后的实际 HTML、CSS 和 JavaScript。

**Key Characteristics:**

- 冷白底色、石墨文字、纯白内容面与克制钴蓝。
- 中文无衬线大字与 Manrope 拉丁字符共用一套层级。
- 真实软件截图、细线路、圆形节点与圆形箭头。
- 状态可点击、可用键盘操作，并尊重减少动态偏好。

## Colors

中性色承担整块背景与阅读结构，蓝色承担动作和状态，具体值以 frontmatter 为准。

### Primary

- **钴蓝**（`accent`）：箭头圆盘、选中流程节点、下一步、开启的开关、步骤数字底与封面移动线路。
- **浅蓝信号**（`signal`）：深色区的进度线、选中标签文字、状态重点与可见焦点。
- **深钴蓝**（`accent-ink`）：浅蓝连接标记内的文字与状态点。
- **雾蓝托片**（`connection`）：静态连接标记的浅色底。

### Neutral

- **冷白画布**（`canvas`）：封面与工程说明的页面底色。
- **石墨**（`ink`）：正文、大标题、封面主动作、机制区、页尾及选中截图标签。
- **展览白**（`paper`）：作品图集、启动说明与灯箱。
- **动作白**（`white`）：导航、页尾动作与深色区重点文字；与展览白保留 CSS 源中各自的角色命名。
- **石板正文 / 蓝灰说明**（`body-copy` / `muted`）：浅色面上的解释与辅助说明。
- **纸面分隔线 / 石墨面分隔线**（`line` / `dark-line`）：问答、步骤与机制区的细分隔。
- **图集底 / 图注底**（`gallery-surface` / `gallery-caption`）：截图周围的两层低对比托底。
- **控制台底 / 顶栏 / 深色区说明**（`console` / `console-top` / `console-copy`）：深色示意控制台与机制区的层次。

蓝色 `focus` 承担默认键盘焦点；深色机制区、页尾与演示开关使用浅蓝信号焦点。

**The Cobalt Signal Rule.** 大背景保持冷白、纯白或石墨；钴蓝用于动作与选中，浅蓝用于深色面的细线、状态文字和焦点。不得重新引入绿色系列页面背景。

## Typography

**Display Font:** Manrope；中文由本地 `Showcase SC` 承接，后备为 Microsoft YaHei 与 sans-serif。

**Body Font:** 与展示字体相同。没有单独的等宽字体；文件名采用相同字体加粗。

**Character:** 中文字面简洁而紧凑，拉丁字符保留 Manrope 的几何感；大标题较紧，解释文字保留充足行高。

### Hierarchy

- **Display**：封面标题使用 frontmatter 的 display；桌面按视口缩放，移动端切换为 `clamp(32px, 8.4vw, 53px)`、行高 `1.35`。两行标题由实际内容决定。
- **Headline**：段落标题使用 headline；机制标题与页尾另有对应的流式尺寸，小屏主要段落标题为 `34px`。
- **Title**：默认小标题使用 title；流程解释和项目叙述使用更大的局部层级，不把所有标题强制拉齐。
- **Body**：全局基准使用 body；长解释常用 `15px`、行高 `1.9`，手机正文根据区域落在 `12–13px`。短说明由实际容器限制宽度，未建立通用 ch 行长令牌。
- **Label**：状态、图注与索引以 label 为基准，常用 `11–13px`；计数使用等宽数字排布。

**The Shared Voice Rule.** 标题、正文和文件名维持同一套自托管无衬线关系，以字号、字重和行距区分层级。

字体以 `font-display: swap` 自托管：实际加载 `assets/fonts/manrope-latin.woff2` 与 `assets/fonts/showcase-sc.woff2`。后者来自 Google Fonts 的 Noto Sans SC 可变字体（字重 `100–900`），以 `Showcase SC` 为 CSS 别名，按当前 HTML 与 JavaScript 的 504 个不同字符制作子集；新增中文文案时应重新生成子集，缺失字符会使用后备字体。同目录保留 Manrope 与 Noto Sans SC 的 SIL Open Font License 1.1 文本；分发字体时保留对应许可。`manrope-latin-ext.woff2` 已附带，但当前 CSS 未加载。

## Layout

默认页面边距为 `clamp(24px, 6.25vw, 104px)`。封面、项目叙述、机制详情和工程说明采用两栏；机制路线保留四等分节点；启动步骤采用三栏。内容板外侧露出窄幅冷白画布，内部用宽留白组织层级；常见间距以 frontmatter 的 spacing 为准，并非强制单一等比刻度。

桌面封面默认最小高度 `790px`、顶部内边距 `156px`；截图装置内边距 `44px 8px 28px`，封面底部信息外边距 `24px 0 22px`。这些值服务于已验证首屏中作品与下一节的衔接，是本页构图参数。

- **宽屏 ≥1600px**：页面边距变为 `max(104px, calc((100vw - 1370px) / 2))`，封面最小高度 `870px`，主截图区最大宽 `650px`，图集视窗高 `620px`。
- **≤1150px**：收紧导航与栏间距、缩小封面文字，图集视窗高 `510px`，整体两栏保留。
- **≤900px**：页面边距 `32px`，内容板圆角切换为 tablet 值；导航和文字进一步收紧，内容板垂直内边距 `64px`，演示开关与说明转为上下排列。
- **≤650px**：页面边距 `24px`；封面、项目叙述、机制详情、工程说明和启动步骤改为单列。内容板外边距 `8px`、内边距 `50px 16px`，图集视窗高 `310px`。导航改为菜单按钮与可展开的白色链接行。四个流程节点仍并排，节点缩至 `49px`，详情和控制台上下排列。

导航位于封面顶部的绝对定位层，并未做滚动吸顶。桌面页内链接预留 `112px` 滚动距离，小屏改为 `32px`。不把页面高度、截图固定尺寸或本页段落次序当成所有未来页面的通用模板。

## Elevation & Depth

大多数内容面保持平面，以整块颜色、相邻圆角板和细线表达层次。截图与临时消息有柔和阴影；灯箱使用接近不透明的蓝黑遮罩。没有背景模糊、玻璃材质或全局卡片阴影。

### Shadow Vocabulary

- **倾斜主窗口**：`0 28px 40px -26px #242c4580`，用于封面的真实截图。
- **图集截图**：`0 14px 26px -16px #292d3580`，使截图与托底分开。
- **短消息**：`0 8px 22px -10px #17244160`，用于悬浮 toast。

**The Evidence Lift Rule.** 目前阴影用于截图证据与临时反馈；内容板本身用色面建立结构。

## Shapes

大面使用柔和连续的圆角，导航和动作使用更小圆角，状态与方向使用圆形。内容板圆角从桌面到手机依次使用 slab、slab-tablet、slab-mobile。导航使用 nav，主动作使用 button，控制台使用 console；小屏主动作采用 mobile-button。胶囊使用 pill；圆盘、状态点和开关滑块使用 `50%` 圆角。

截图只做包含式展示，不裁切关键界面。封面截图默认轻微逆时针倾斜（桌面 `-3deg`、手机 `-2deg`）；图集与灯箱保持正向。线性图标来自内联 SVG，常规尺寸 `24px`、描边 `1.7`，不同控件按用途缩放。

## Components

### Buttons

主动作是有圆形箭头的圆角块，石墨底白字用于冷白封面，白底石墨字用于深色页尾；箭头圆盘为钴蓝、图标为白色。共享样式使用最小高度而非截断内容的固定高度，frontmatter 的 height 表示对应基准。桌面文字 `17px / 600`，手机 `14px`；手机最小高度 `56px`。

悬停时圆形箭头在 `0.5s` 内转动 `-35deg`；源码入口的外链圆盘转动 `45deg / 0.4s`。行内链接的外链图标向右上移动 `3px / 0.35s`；下一步图标向右移动 `4px / 0.3s`。共用缓动为 `cubic-bezier(.16,1,.3,1)`。

所有可聚焦动作使用可见焦点：默认轮廓 `3px`、外偏移 `6px`；深色机制区与页尾的动作改用浅蓝信号轮廓。普通按钮禁用时透明度 `.6` 且显示等待光标；当前已渲染页面没有禁用动作或错误字段状态。

### Chips / Tabs

连接标记为雾蓝胶囊、深钴蓝文字和圆点、SVG 箭头，轻微顺时针旋转。它是静态说明，不伪装实时连接。

截图切换由两个标签按钮组成：蓝灰胶囊托底，选中项为石墨底白字，未选中项透明，悬停获得较深蓝灰色面；颜色过渡 `0.25s`。支持左右方向键、Home、End，非选中项退出 Tab 顺序；切换时同步图片、图注、计数和面板关联。

### Cards / Containers

图集使用包含式图片、独立图注与计数，真实截图比例完整保留。封面和图集点击均可进入原生 dialog 灯箱；支持 Esc、关闭按钮和背景点击，关闭后焦点返回触发入口，打开时锁定页面滚动。灯箱宽度上限 `1280px / 96vw`，高度上限 `94dvh`。

示意控制台采用深蓝灰底、较亮顶栏与三行描述列表。桌面内边距主要为 `16px 20px`，手机改为 `18px 16px`；文字与第三行浅蓝状态强调同步随流程更新。这里显示的是示意数据。

### Inputs / Fields

现有唯一输入是原生 checkbox 驱动的演示开关，没有文本输入框、表单校验或错误态。开关轨道 `42×26px`，滑块 `18px`；开启时底色变为钴蓝、白色滑块向右移动 `16px`。焦点显示在可见轨道上，使用浅蓝信号 `3px` 轮廓、`5px` 外偏移。开关仅切换机制说明分支。

### Navigation

桌面白色圆角导航包含作者标记与三个页内链接，源码入口独立为白色块，两者使用细蓝灰描边。链接悬停与键盘聚焦时展开底部细线（`0.3s`）。未实现滚动追踪当前节，不应描述为存在 active 导航态。

手机菜单使用可点击的 `44×44px` 圆按钮；展开后两条横线变为叉形，链接行显示在导航下方。点击页内链接、Esc 或进入桌面断点时收起；Esc 后焦点回到菜单按钮。另有可聚焦的“跳到主要内容”入口。

### Interactive Route

四个圆形节点与浅蓝进度细线构成核心流程。当前节点为钴蓝底白色图标、浅蓝标签并放大至 `1.08`，未选中节点为石墨底细描边；悬停未选中节点上移 `4px`。进度宽度采用 `0.8s` 共用缓动。点击节点、下一步或开关会暂停播放；方向键与 Home / End 支持节点间切换。

播放由用户主动开启，每步间隔 `3200ms`，最后一步自动停止；离开机制区或页面进入后台也停止。播放中状态点以 `1.5s` 脉冲变化。封面线路持续描边周期为 `16s`，滚动仅在首段触发，最大上移 `29.75px`。截图悬停在 `0.8s` 内回正。

**减少动态**：`prefers-reduced-motion: reduce` 关闭所有 CSS 过渡、关键帧和滚动平滑，移除封面与节点变形；JavaScript 不再更新滚动位移。用户主动播放仍会按时间切换文字状态，各按钮和分支保持可用。

### Disclosure / Feedback

问答使用原生 details / summary：细分隔、宽点击行，展开时加号旋转 `45deg / 0.4s`。复制文件按钮为低对比浅蓝灰块，悬停变深；复制成功或不可用均通过 `role=status` 的短消息反馈，消息显示 `3500ms` 后消失。消息不阻断当前操作。启动步骤的数字使用钴蓝圆底与白色文字。

## Do's and Don'ts

### Do:

- **Do** 将本系统只应用于 `website/`，把桌面截图视为内容证据。
- **Do** 维持冷白画布、纯白内容、石墨深色面与钴蓝动作之间的既有角色关系。
- **Do** 为状态变化同步文字、视觉高亮与可访问名称；让默认内容直接可见。
- **Do** 保留完整截图比例、自托管字体许可、可见焦点及减少动态支持。
- **Do** 以圆形节点、细线路与圆形箭头延续已经实现的形态语言。

### Don't:

- **Don't** 把本官网的 token 推广为 Python / Tkinter 桌面应用的规范。
- **Don't** 使用绿色系列页面背景；真实产品截图中的原始绿色状态保持原样。
- **Don't** 把交互演示、状态圆点或真实截图中的历史状态描述为实时连接或效果保证。
- **Don't** 用装饰性裁切隐藏真实截图中的关键界面。
- **Don't** 为尚不存在的输入表单、弹窗流程或滚动 active 导航补写虚构规范。
- **Don't** 将本页专用的段落顺序和首屏构图升级为所有页面的固定模板。
