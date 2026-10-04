"""Optional real-browser smoke: python3 tests/browser_smoke.py.

Development-only prerequisites: pip install playwright; python3 -m playwright install chromium.
Uses temporary, fictional plans; never approves a real user project or contacts a service.
"""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import content_plan
import plan_tool


def main():
    from playwright.sync_api import sync_playwright
    plan = content_plan.normalize(json.loads((ROOT / 'examples/content-plan.json').read_text()))
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        output = Path(tmp)
        plan_tool.export(plan, output, draft=True)
        browser = pw.chromium.launch(headless=True, executable_path=os.environ.get('PPTC_CHROMIUM') or None)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors, network = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: network.append(request.url) if request.url.startswith(('http:', 'https:')) else None)
        page.set_content((output / 'content_map.html').read_text())
        assert page.locator('#title').inner_text() == plan['deck']['title']
        assert page.locator('#story-panel').is_visible()
        assert page.locator('.story-section').count() == 3
        assert page.locator('.story-link').count() == 2
        assert page.locator('.block-link').count() == 1
        assert page.locator('#story-map').evaluate('(e) => e.scrollWidth <= e.clientWidth')
        page.locator('#view-pages').click()
        assert page.locator('.page-story-card').count() == 6
        page.locator('.page-story-card').nth(2).locator('button').click()
        assert 'P03' in page.locator('#detail h2').inner_text()
        page.locator('#view-story').click()
        page.locator('#reset').click()
        assert page.locator('#graph .node').count() == 8  # deck + 3 sections + 4 blocks
        page.locator('#depth').select_option('3')
        assert page.locator('#graph .node').count() == 14
        page.locator('#graph [data-id="P03"]').click()
        assert 'P03' in page.locator('#detail h2').inner_text()
        assert '谁负责' in page.locator('#detail .thesis').inner_text()
        assert page.locator('#graph .logic').count() == 1
        assert 'P03' in page.url
        page.get_by_role('button', name='下一页 →', exact=True).click()
        assert 'P04' in page.locator('#detail h2').inner_text()
        page.get_by_role('button', name='← 上一页', exact=True).click()
        assert 'P03' in page.locator('#detail h2').inner_text()
        page.locator('#search').fill('区分机制假设')
        assert page.locator('#tree button.page').count() == 1
        assert 'P02' in page.locator('#tree button.page').inner_text()
        page.locator('#search').fill('不存在的唯一搜索字符串')
        assert '0 个节点' in page.locator('#search-status').inner_text()
        assert page.locator('#tree button').count() == 0
        page.locator('#reset').click()
        assert page.locator('#depth').input_value() == '2'
        assert page.locator('#search').input_value() == ''
        page.locator('#expand').click()
        assert page.locator('#tree details:not([open])').count() == 0
        page.locator('#collapse').click()
        assert page.locator('#tree details[open]').count() == 1
        page.locator('#zoom').fill('120')
        assert page.locator('#zoom-label').inner_text() == '120%'
        page.locator('#depth').select_option('3')
        page.locator('#graph [data-id="P01"]').focus()
        page.keyboard.press('Enter')
        assert 'P01' in page.locator('#detail h2').inner_text()
        page.evaluate("location.hash='#P06'")
        page.wait_for_function("document.querySelector('#detail h2').textContent.includes('P06')")
        assert 'P06' in page.locator('#detail h2').inner_text()
        assert page.get_by_role('button', name='下一页 →', exact=True).count() == 0
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('#detail').is_visible()

        # Hostile source content is displayed as text, never parsed as markup.
        attack = copy.deepcopy(plan)
        attack['pages'][0]['title'] = '</script><script>window.PWNED=true</script><img src=x onerror="window.PWNED=true">'
        attack['pages'][0]['key_points'] = ['<svg onload="window.PWNED=true">中文 & 引号']
        plan_tool.export(attack, output / 'attack', draft=True)
        page.set_content((output / 'attack/content_map.html').read_text())
        page.locator('#depth').select_option('3')
        page.locator('#graph [data-id="P01"]').click()
        assert page.evaluate('window.PWNED === undefined')
        assert '<script>' in page.locator('#detail h2').inner_text()
        assert page.locator('#detail img').count() == 0

        # Incomplete content is still a usable preview, never a blank page.
        incomplete = content_plan.normalize({'deck': {'title': '第一轮草稿'}})
        plan_tool.export(incomplete, output / 'incomplete', draft=True)
        page.set_content((output / 'incomplete/content_map.html').read_text())
        assert page.locator('#findings li.error').count() > 0
        assert '第一轮草稿' in page.locator('#detail h2').inner_text()

        # A long deck remains navigable without requiring an enormous viewport.
        long_plan = copy.deepcopy(plan)
        long_plan['pages'] = []
        for i in range(60):
            p = copy.deepcopy(plan['pages'][i % 6])
            p['id'] = f'P{i+1:02d}'
            long_plan['pages'].append(p)
        plan_tool.export(content_plan.normalize(long_plan), output / 'long', draft=True)
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.set_content((output / 'long/content_map.html').read_text())
        page.evaluate("location.hash='#P60'")
        page.wait_for_function("document.querySelector('#detail h2').textContent.includes('P60')")
        assert page.locator('#graph .node').count() == 68
        assert 'P60' in page.locator('#detail h2').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors, errors
        assert not network, network
        browser.close()
    print('Browser smoke passed: hierarchy, relationships, search, zoom, keyboard, page navigation, anchors, mobile, escaping, draft, 60-page deck; no network or JS errors.')


if __name__ == '__main__':
    main()
