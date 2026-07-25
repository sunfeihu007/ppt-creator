# Phase 7：整合与输出

1. `python scripts/verify_pages.py` —— 全部页面自动校验（存在性/可打开/比例/分辨率），
   失败页回到 Phase 5/6 流程重新生成；
2. 确认 plan.json 每页 notes 完整（时长标注+内容），缺失的补写并更新 plan.json；
3. `python scripts/build_ppt.py` —— 内置 gate：存在非 approved 页面会拒绝执行；
   自动压缩图片（>2MB 的 PNG 转 JPEG q85）、按 plan 顺序组装、注入备注；
4. 输出 `ppt_workspace/output/<topic>.pptx`，报告文件大小与页数；
5. 不新增例行确认；用户主动要求调整时，只有尚未用完第3个图片确认点才合并展示返工结果，
   达到上限后不得拆分请求；调整页状态退回并重走AI质检流程后重新 build；
6. 全部完成：`plan_tool.py phase --name 7_assembly --status done`，交付文件。

版本管理：重新生成的页面直接覆盖 pages/PXX.png，旧版自动存入 pages/history/（脚本处理）。
