# PPT Creator —— 结构化演示文稿生成 Skill

> **Powered by MrSuperOne** · 当前版本 v2.0.0 · MIT License

一个面向 AI Agent 的 PPT 制作技能：与你对话式地规划大纲和内容，按"配色 × 风格"设计系统
用 AI 逐页生成高质量幻灯片图片，最终组装成带演讲者备注的、可直接演示的 PPTX 文件。

兼容所有支持 Agent Skills（SKILL.md）标准的 agent：**Claude Code / Cowork、Codex CLI、
Hermes Agent、OpenClaw** 等。

---

## 它能做什么

- **对话式规划**：不是拿到一句话就开画，而是先和你讨论清楚——给谁看、讲多久、分几个
  部分、每页讲什么，确认后才动手；
- **设计系统**：6 种配色 × 6 种风格自由组合（30+ 种视觉方案），支持公司品牌配色，
  附真实 PPT 抽取的版式参考图，生图时垫图保证还原度；
- **AI 生图页面**：每页是一张 16:9 高清整图（2K/1920×1080），玻璃拟态 3D、杂志排版、
  极简线描、科幻 HUD 等质感均可；
- **演讲者备注**：每页自动写入带时长标注的演讲备注（重点页 5-6 分钟/过渡页 1-2 分钟，
  含互动与转折提示）；
- **工程化流程**：七步流程状态化管理，中断可恢复、换 agent 可接续；产物自动校验、
  自动压缩，成品直接可分发。

## 适用场景

企业技术方案、产品介绍、立项汇报、培训课件、学术报告、销售交流。
对话中说"做个 PPT / 帮我做个汇报 / 生成演示文稿"即可触发。

---

## 七步工作流

| Phase | 做什么 | 产出 |
|:--|:--|:--|
| 1 大纲讨论 | 场景/受众/时长 → 3-5 个主要部分 | 大纲框架 |
| 2 内容方向 | 每部分 2-4 个核心要点，理顺逻辑 | 内容规划 |
| 3 页数分配 | 逐页清单（每页一个核心观点） | `plan.json` |
| 4 设计确定 | 选配色 → 选风格 → 探测生图后端 | 设计组合锁定 |
| 5 框架页 | 封面/目录/过渡/结束页（先出封面定调） | 框架页图片 |
| 6 内容页 | 分批生成 + AI 目检 + 逐批确认 | 全部页面图片 |
| 7 整合输出 | 校验 → 压缩 → 组装 → 注入备注 | 最终 PPTX |

**防跳步机制**：进度写入 `ppt_workspace/plan.json`（唯一事实来源），`plan_tool.py` 对
phase 和页面状态双重把关，`build_ppt.py` 拒绝组装任何未确认的页面——无论在哪个 agent
里运行，七步都不会被压缩成三步。中断后新会话只要读 plan.json 就能原地继续。

---

## 设计系统（配色 × 风格解耦）

配色管颜色，风格管质感与版式，二者自由组合。同一风格可换色，同一配色可换质感。

**配色**（`references/design/palettes/`）：

| 配色 | 主色 | 适合 |
|:--|:--|:--|
| 翰声橙绿 `hansheng-orange-green` | 橙+深青绿 | 公司默认 |
| 联通红 `liantong-red` | 红 | 运营商/热烈商务 |
| 科技蓝 `tech-blue` | 蓝 | 金融/科技 |
| 藏青金 `navy-gold` | 藏青+金 | 高层汇报/稳重 |
| 暖橙 `warm-orange` | 橙 | 温暖叙事 |
| 深空青 `deep-space` | 荧光青(深底) | 唯一深色配色 |

**风格**（`references/design/styles/`，颜色无关，各附 3 张版式参考图）：

| 风格 | 质感 | 信息密度 |
|:--|:--|:--|
| 玻璃拟态3D `glass-3d` | 玻璃卡片、等距分层、渐变徽章 | 高 |
| 平面杂志 `flat-editorial` | 大色块、大数字、留白 | 低中 |
| 极简线描 `lineart-minimal` | 单色细线插画 | 低 |
| 2.5D插画 `illust-2.5d` | 等距插画、几何纹样 | 中低 |
| 现代卡片 `card-modern` | 折页卡、超大数字 | 中 |
| HUD线框 `hud-frame` | 发光线框、扫描框（仅配深色配色） | 中高 |

组合矩阵、推荐搭配、双色 60-30-10 规则见 `references/design/INDEX.md`。
自定义品牌配色：复制最接近的配色文件改 Token 色值即可。

---

## 生图后端

| 后端 | 条件 | 说明 |
|:--|:--|:--|
| **Codex 内置 image_gen** | 在 Codex CLI 中运行本 skill | 直接用 `$imagegen`（gpt-image-2），走 ChatGPT 订阅鉴权 |
| **Gemini API** | `export GEMINI_API_KEY=...` | 默认模型 `gemini-3.1-flash-image-preview`，可用 `GEMINI_IMAGE_MODEL` 覆盖；key 走 header，不入 URL |
| **本地 codex CLI** | 已安装并登录 codex | 在 Claude Code 等环境中通过 `codex exec` 调用 gpt-image-2，**无需 OpenAI API key** |

自动探测顺序：Codex 环境 → Gemini key → 本地 codex CLI。整套 PPT 锁定同一后端。
**key 只通过环境变量提供，禁止粘贴到对话中。**

---

## 安装

```bash
git clone https://github.com/sunfeihu007/ppt-creator.git
pip install -r ppt-creator/requirements.txt   # python-pptx, Pillow
```

放入对应 agent 的 skills 目录：

| Agent | 位置 |
|:--|:--|
| Claude Code | `~/.claude/skills/ppt-creator/` |
| Cowork（Claude 桌面端） | 设置 → Capabilities → 安装 skill（或导入 .skill 包） |
| Codex CLI | 项目 `.codex/skills/` 或全局 skills 目录 |
| Hermes Agent | `~/.hermes/skills/ppt-creator/` |
| OpenClaw | 任一已配置 skills 根目录 |

**Codex 用户建议**在 AGENTS.md 加一句，防止内置生图工具绕过流程：

```
制作PPT必须使用 ppt-creator skill 的七步流程（以 ppt_workspace/plan.json 为准），
禁止绕过流程直接用 image_gen 单发生成幻灯片图片。
```

## 使用

对 agent 说：

> 帮我做一个给投资人看的产品介绍 PPT，15 分钟

然后跟着七步走即可。中断后说"继续做 PPT"，agent 会从 plan.json 恢复进度。

**脚本层直接调用**（调试/自动化）：

```bash
python scripts/plan_tool.py init --file draft_plan.json          # 建立计划
python scripts/plan_tool.py design --palette hansheng-orange-green --style glass-3d --provider codex
python scripts/plan_tool.py status                               # 随时看进度
python scripts/make_prompt.py --page P01 --print                 # 拼装提示词
python scripts/gen_image.py --page P01                           # 生图(重试+16:9裁切)
python scripts/verify_pages.py                                   # 机器校验
python scripts/build_ppt.py                                      # gate→压缩→组装→备注
```

---

## 目录结构

```
ppt-creator/
├── SKILL.md                      # 技能主定义（七步总览+第一原则）
├── references/
│   ├── constraints.md            # 全局约束（自动附加到每条生图提示词）
│   ├── phases/                   # Phase 1-7 详细指令（按需加载）
│   └── design/                   # 设计系统：INDEX + palettes/ + styles/(含参考图)
├── scripts/
│   ├── plan_tool.py              # plan.json 状态管理 + 防跳步 gate
│   ├── make_prompt.py            # 提示词拼装（风格骨架+配色+内容+约束）
│   ├── gen_image.py              # 双后端生图（重试/退避/自动裁切16:9）
│   ├── verify_pages.py           # 产物校验（存在/可打开/比例/分辨率）
│   └── build_ppt.py              # gate→图片压缩→组装→注入演讲备注
└── evals/evals.json              # 8 条行为评测用例
```

## 质量保障

- **提示词脚本化拼装**：风格骨架、配色描述、禁止项全部固定，AI 只填每页的标题/要点，
  从机制上杜绝"越画越跑偏"；
- **全局约束**（`references/constraints.md`）：禁止色值/颜色名入画、禁止占位符与假 logo、
  禁止乱码、禁止风格漂移、软性描述不承诺具体百分比；
- **双重校验**：脚本查比例/分辨率/损坏，AI 目检查乱码/截断/漂移；
- **自动压缩**：>2MB 的页面图组装时转 JPEG，成品体积缩小 5-20 倍，方便邮件/IM 分发。

## 模型使用建议

规划与内容创作：深度内容用顶级模型，常规汇报次顶级足够；提示词环节已脚本化，对模型
档位不敏感；生图选中文渲染准确的图像模型，草稿低档、定稿高档；目检 QA 用便宜的多模态
模型即可。

## Roadmap

- `build_native_ppt.py`：无生图后端时用 python-pptx 原生绘制（首选 flat-editorial 风格）
- 更多配色/风格入库；evals 端到端用例扩充

## License

MIT — see [LICENSE](LICENSE).

---

**Powered by MrSuperOne**
