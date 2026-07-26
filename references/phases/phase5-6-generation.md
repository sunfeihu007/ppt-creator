# Phase 5–6：低干预并行页面生成

## 硬性目标

- 图片阶段默认2次、最多3次用户确认，与总页数无关。
- 除明确单页任务外，多页任务保持至少4个子agent并行；不足4页时按剩余页数并行。
- AI逐页质检不能省略，但质检不是用户确认。

## 准备与并行协议

1. Phase 3 已确认的逐页清单视为批量生图授权；先补齐所有页面的 title/points/layout_hint/notes。
2. 执行 `plan_tool.py lint --ids all`。必需词、禁止词、来源或证据规则存在错误时先修正，
   不得靠生图后人工补救。
3. 执行 `verify_design_plan.py`。修复被禁止的组合；检查连续同构版式、重复三卡、
   specialized/legacy 提醒。预检不增加用户确认点。
4. 主agent为待生成页面逐一运行 `make_prompt.py`，禁止子agent自行手写完整提示词。
   `reuse_mode=exact_asset` 的页面不生成 prompt 或图片，由源页面提供同一资产。
5. 按模板复杂度交错分片，建立至少4条持续工作队列；所有worker共享已锁定的
   palette/style/industry/provider/image_transport/image_model、语义色角色、页面类型注册表、
   几何/圆角/阴影锁、全局约束和已确认样张。每个 worker 必须使用该页已登记的 `page_type`；
   单页失败仅重试该页，禁止改用其他风格、行业修饰或后端继续。
6. 子agent只产出分配的图片，不写 plan.json。脚本worker必须用 `gen_image.py --no-state`；
   主agent收集成功结果后统一运行 `plan_tool.py pages --ids ... --status generated`。
7. 主agent逐页目检，检查乱码、截断、风格漂移、比例、文字对比度和颜色约束；同时检查
   圆角/阴影/标题轴是否漂移、是否复制参考图内容、是否跨页重复三卡。明显问题自动重做，
   最多3轮；通过后批量标记 `qa_passed`。只有无法自行消解的内容歧义才询问用户。
8. 宿主有视觉/OCR 能力时，把逐页识别文本写入 `ppt_workspace/qa/ocr/PXX.txt` 并运行
   `verify_semantics.py`。默认缺 OCR 可跳过；事实敏感项目有 OCR 时用 `--strict`。

## 各宿主的生成方式

### AGY 原生（默认于 AGY CLI）

每个 worker 调用原生 `generate_image` 一次：`AspectRatio=16:9`，`ImageName` 必须包含唯一页码
（如 `P01-cover`），Prompt 使用 `make_prompt.py` 生成的全文。AGY 返回图片路径后导入：

```bash
python scripts/gen_image.py --page P01 --provider agy --transport native \
  --import-file /absolute/path/to/agy-output.jpg --no-state
```

AGY 原生工具当前没有独立参考图字段，不得虚构参数；使用完整风格提示词、已确认样张和 QA。

### Codex 原生（默认于 Codex）

每个 worker 调用原生 `image_gen`，按 prompt 生成 16:9 页面并保存到独立文件，再统一导入：

```bash
python scripts/gen_image.py --page P01 --provider codex --transport native \
  --import-file /absolute/path/to/codex-output.png --no-state
```

### 其他客户端

使用已配置的 Gemini API key 和锁定的稳定模型：

```bash
python scripts/gen_image.py --page P01 --provider gemini --transport api --no-state
```

`agy/cli` 与 `codex/cli` 只用于用户明确指定的兼容桥。失败时停止该页并报告，不自动切换。

## 确认点1：设计样张

优先生成一组合并样张：

- 封面页：验证整套品牌识别、主视觉和标题系统；
- 架构图页：验证复杂结构、连接线、模块和行业图解语言；
- 详解页或客户案例页：验证正文密度、图文关系和真实素材处理。

只选择计划中实际存在的页面类型；如果缺少其中某类，用最接近的代表页替代。无论展示 1–3 页，
都必须合并为一次确认，不能拆成多个检查点。确认范围包括语义配色、字体层级、网格、材质、
页面类型差异、行业视觉语气、形状/圆角/阴影锁、文字对比度和后端效果。样张不得复制
参考图中的品牌、文字、指标或界面内容。通过后运行：

```bash
python scripts/plan_tool.py review --type design-sample --ids P01,P05,P08 --result approved
```

该确认授权按同一视觉语言完成所有剩余页面，不再逐页或每2–4页询问。

## Phase 5：框架页

样张通过后并行生成目录、过渡、总结和结束页；逐页AI质检后标记 `qa_passed`。框架页达到
`qa_passed` 即可完成 Phase 5 并进入内容页，不创建额外确认点。

## Phase 6：内容页与确认点2

并行生成全部内容页并完成逐页AI质检。把全部页面制作成按页码排列的总览，一次性向用户请求：

- 全部通过；或
- 一次性列出需要修改的页码与全局意见。

用户修改术语、来源、能力边界或全局设计时，使用 `plan_tool.py contract/page` 更新后运行
`plan_tool.py sync`；只重做被标为 `pending` 的受影响页及其精确复用后代。

全部通过时对所有页面记录一次 full-deck 确认：

```bash
python scripts/plan_tool.py review --type full-deck --ids all --result approved
```

若用户只要求修改部分页面，用一次 full-deck 确认记录这些页；脚本会批准其余已通过AI质检的页面，
只把点名页面退回 `pending`：

```bash
python scripts/plan_tool.py review --type full-deck --ids P03,P11 --result changes-requested
```

## 可选确认点3：合并返工

若确认点2要求修改，只重做指定页或受全局意见影响的页面，AI质检后一次性展示全部返工结果，
记录 `revision` 确认；此前未点名的页面已经由 full-deck 确认批准。达到3次后禁止新增确认点；
剩余意见必须合并处理。Phase 6 只有全部页面
`approved` 后才能完成，最终 build gate 不放宽。
