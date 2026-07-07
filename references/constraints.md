# 全局生成约束（CRITICAL CONSTRAINTS）

`make_prompt.py` 会将本文件"提示词附加段"自动追加到每条生图提示词末尾。
人工检查以"检查清单"为准，违反任意一条即重新生成该页。

## 提示词附加段

```
STRICT RULES (violating any rule = regenerate):
1. NEVER render color hex codes (#E60012 etc.) or color names (联通红/科技蓝/深灰 etc.)
   as visible text in the image. Colors are for styling only.
2. NO placeholder text: no [汇报人]/[日期]/[公司名称]/[联系方式], no "内部参考"/"仅供内部",
   no fake logos, no fake phone/website/contact info, no "请联系销售" style calls-to-action.
3. All Chinese text must be real, standard, clearly readable characters (黑体/思源黑体 style).
   NO garbled characters, NO invented words, NO text unrelated to the given content.
4. Keep the SAME color scheme, icon style, background and layout language as specified.
   Do not drift into other styles. No colorful/rainbow icons — single color family only.
5. Align similar elements horizontally; balanced layout; all text fully visible, nothing cut off.
6. Use soft qualitative wording (显著提升/大幅改善); NO specific percentage claims.
7. 16:9 aspect ratio, professional presentation quality.
```

## 检查清单（目检用）

- [ ] 无色值/颜色名出现在画面文字中
- [ ] 无占位符、假logo、假联系方式、"内部参考"类文字
- [ ] 无乱码字、无与大纲无关的捏造词
- [ ] 配色/图标/背景与前序页面一致，无风格漂移
- [ ] 同类元素对齐、布局均衡、文字无截断
- [ ] 无具体百分比承诺
- [ ] 比例16:9、分辨率达标（verify_pages.py 自动查）

## 内容设计原则（DO / DON'T 摘要）

DO：先讨论后生成；页间有逻辑衔接；重点内容多页展开；案例匿名化（"某大型集团"）；
每阶段用户确认；定期更新 plan.json。
DON'T：不假设库已安装；不出现第三方品牌字样；不随意标红（标红必须有含义且备注中有解释）；
不信息平均；非用户明确要求不用深色背景。
