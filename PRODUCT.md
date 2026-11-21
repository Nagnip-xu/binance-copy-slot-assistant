# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

用户确认：官网使用纯静态 HTML、CSS 和 JavaScript，位于 `website/`。本地验收后，用户于 2026-11-22 明确授权发布到 GitHub Pages，并更新 README 与 GitHub 仓库。使用 GitHub Actions 仅部署网站目录。

## Users

官网面向查看 Nagnip-xu 个人开发作品的访客。用户明确选择「更偏向个人作品展示」，因此页面首先让访客理解项目、看到真实界面和实现思路，再提供使用说明和源码入口。

## Product Purpose

展示「币安跟单抢位助手 · 独立版」这一桌面自动化作品。软件通过受管理的 Chromium 浏览器及页面登录态读取跟单状态，在用户开启真实提交后尝试申请跟单名额。

## Positioning

Windows Python / Tkinter 桌面工具，通过本机 Chrome DevTools Protocol 与网页内部模块协作，汇集页面监控、人数变化提醒、提交速率控制和成功提醒。

## Operating Context

现有公开仓库为 `https://github.com/Nagnip-xu/binance-copy-slot-assistant`。使用者下载完整项目、解压并双击 `START.cmd`。首次运行真实提交和自动启动默认关闭，后续开关保存在本地。实际任务需要在独立浏览器中登录。

## Capabilities and Constraints

- 官网为项目展示，不连接账户、不执行跟单或资金操作。
- 保留软件现有中文名称、作者账号、真实截图与已核实的功能事实。
- 不编造用户数量、收益、抢位成功率、性能基准、官方合作或保证全天无人值守。
- 软件依赖网页内部模块，存在限流、登录失效、网页升级与浏览器恢复限制。
- 软件当前入口域名未核验归属；使用提示应明确要求核实实际页面来源。
- 官网已通过用户本地验收，授权发布到 `https://nagnip-xu.github.io/binance-copy-slot-assistant/`。

## Brand Commitments

作者：Nagnip-xu。中文官网；重点展示个人项目。用户将视觉选择交由设计者，并要求动态效果与交互。用户随后明确否定绿色系列背景；官网采用冷白底色、石墨黑文字与收尾、钴蓝操作强调、蓝灰辅助色。保留真实截图、可探索流程与作品展示结构。不得重新使用绿色系列页面背景。现有桌面 UI 是产品证据，不是官网必须沿用的品牌规范；真实截图里的原始绿色状态按钮保留。

## Evidence on Hand

- `README.md`：详细功能、安装和使用流程、实际限制。
- `docs/images/app-overview.png`：用户提供的桌面应用原图。
- `docs/images/browser-workflow.png`：用户提供的软件与浏览器联动原图。
- `app.py`、`engine.py`、`browser_control.py`、`cdp.py`：可核实的实现机制。
- 没有已授权公开的个人履历、头像、商业客户、推荐语或统计成绩，不得捏造。

## Product Principles

官网流程演示中的人数读取频率由用户指定为「每秒10次」，属于示意参数；页面说明明确使用「本演示」，不将其作为桌面软件实际频率的陈述。用户要求截图区标题「看见状态，也掌握主动。」在一行显示。

- 用作品本身与真实界面讲清能力。
- 技术机制说明服务于理解，不把官网做成交易执行界面。
- 下载、源码和使用说明应可找到，但以作品展示为主。
- 区分交互演示与真实运行数据。
- 经用户验收与明确授权后发布；后续推送网站变更到 `main` 自动更新官网。
