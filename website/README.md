# 个人作品官网

这是项目的中文静态展示页面，使用 HTML、CSS 和 JavaScript。无需安装 Node.js、构建工具或后端服务。页面中的流程交互是机制演示，不会连接账户或发送交易请求。

**在线访问：[https://nagnip-xu.github.io/binance-copy-slot-assistant/](https://nagnip-xu.github.io/binance-copy-slot-assistant/)**

## 本地预览

在**项目根目录**的 PowerShell 中运行：

```powershell
.\py\python.exe -I -B -m http.server 4173 --bind 127.0.0.1 --directory website
```

然后打开 <http://127.0.0.1:4173/>。关闭命令窗口或按 `Ctrl+C` 停止预览。如果端口被占用，换一个端口并修改浏览器地址。服务器仅提供 `website` 目录，避免将本地运行配置和日志提供给浏览器。

也可直接打开 `index.html` 查看；文件模式下复制文件名可能受浏览器限制，页面会提示手动复制。

## 文件说明

| 文件 | 用途 |
| --- | --- |
| `index.html` | 中文内容、真实截图、流程演示、启动说明与常见问题 |
| `styles.css` | 配色、字体、布局、响应式和动效 |
| `script.js` | 导航、截图切换与放大、流程状态、播放与复制反馈 |
| `assets/` | 本地截图、字体、图标和来源记录 |
| `../DESIGN.md` | 官网设计规范；不改变桌面软件的界面规范 |

图片来自用户提供的两张真实截图，原图保留在 `../docs/images/`；页面使用压缩后的 WebP。字体全部自托管，许可见 `assets/fonts/*-OFL.txt`。中文字体是 Noto Sans SC 的当前文案子集；加入新的中文文案时应重新生成子集，缺失字形会由系统字体补足。

## 检查范围

已检查 320、390、768、1440 像素宽度的布局与主要交互，包括手机导航、截图标签的方向键操作、放大截图及 Esc 关闭、流程切换与播放、演示分支、剪贴板提示、常见问题和减少动态设置。页面未验证桌面软件的线上交易接口可用性。

## GitHub Pages 部署

官网使用 GitHub Pages 托管，仓库 **Settings → Pages → Source** 设置为 **GitHub Actions**。

- 将 `website/` 或 `.github/workflows/deploy-pages.yml` 的变更推送到 `main` 后，自动部署最新版本。
- 也可在 [Actions 部署页面](https://github.com/Nagnip-xu/binance-copy-slot-assistant/actions/workflows/deploy-pages.yml) 选择 **Run workflow** 手动重新发布。
- 仅发布 `website/`。图片、字体、CSS 和脚本均使用相对路径，适配 `/binance-copy-slot-assistant/` 项目网址。
- `.impeccable/` 中的开发参考图与审阅截图保留在本地；桌面程序、Python 运行库、本地配置与日志不进入网站部署产物。

官网演示中的「每秒10次」为演示参数。桌面软件实际人数读取约每分钟一次；修改官网文案不会改变桌面程序的运行频率。
