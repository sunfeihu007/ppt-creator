# Phase 7：整合与输出

1. `python scripts/plan_tool.py sync` —— 根据当前契约和页面内容失效旧 prompt/image；
   如果出现 pending 页面，返回 Phase 5/6 只重做受影响页；
2. `python scripts/verify_pages.py` —— 全部页面自动校验（存在性/可打开/比例/分辨率），
   失败页回到 Phase 5/6 流程重新生成；
3. `python scripts/plan_tool.py lint --ids all` —— 再查必需词、禁止词和证据规则；
4. 有 OCR 文本时运行 `python scripts/verify_semantics.py`；事实敏感且 OCR 可用时加 `--strict`；
5. `python scripts/plan_tool.py sync-check` —— 存在内容/设计/来源与旧产物漂移时拒绝组装；
6. 确认 plan.json 每页 notes 完整（时长标注+内容），缺失的补写并更新 plan.json；
7. `python scripts/build_ppt.py` —— 内置页面状态、语义和同步三重 gate；
   自动解析精确复用页面、压缩图片（>2MB 的 PNG 转 JPEG q85）、按 plan 顺序组装、注入备注；
8. 输出 `ppt_workspace/output/<topic>.pptx`，并自动生成
   `ppt_workspace/final_outline.md` 和 `ppt_workspace/output/artifact_manifest.json`；
9. 不新增例行确认；用户主动要求调整时，只有尚未用完第3个图片确认点才合并展示返工结果，
   达到上限后不得拆分请求；调整页状态退回并重走AI质检流程后重新 build；
10. 全部完成：`plan_tool.py phase --name 7_assembly --status done`，交付 PPTX、自动大纲和清单。

版本管理：重新生成的页面直接覆盖 pages/PXX.png，旧版自动存入 pages/history/（脚本处理）。
当前 `delivery_mode=raster_slide`，页面文字和图形不是 PowerPoint 原生可编辑对象；交付时明确说明。
