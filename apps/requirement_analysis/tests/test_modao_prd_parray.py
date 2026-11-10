from django.test import SimpleTestCase

from apps.requirement_analysis.modao_extractor import ModaoExtractor


_PARRAY_HTML = '''<html><body>
<aside class="sidebar"><div class="menu" id="menu">
  <div role="button" data-page="chat">聊天Tab与群聊入口</div>
  <div role="button" data-page="create">创建群聊</div>
</div></aside>
<div id="doc"><h3>只有当前激活页有静态正文</h3></div>
<script>
const ASSETS = {"a.png": ""};
const P=[
 {"id":"chat","name":"聊天Tab与群聊入口",
  "states":[["entry","群聊入口","a.png"],["menu","创建菜单","b.png"]],
  "intro":"概述A",
  "common":["公共规则1"],
  "req":[["entry","群聊入口（修改）",["条目1","条目2"]],
         ["menu","创建菜单（新增）",[]]]},
 {"id":"create","name":"创建群聊","states":[],"intro":"概述B","common":[],
  "req":[["min","成员选择（新增）",["条目3"]]]}
];
</script></body></html>'''


class PrdPArrayFormatTests(SimpleTestCase):
    """编辑器版 PRD 报告页（内联 const P=[...]，如 Lovin1.3.14-PRD.html）。"""

    def test_detect_requires_menu_and_p_array(self):
        self.assertTrue(ModaoExtractor._is_prd_parray_html(_PARRAY_HTML))
        self.assertTrue(ModaoExtractor._is_prd_parray_menu(_PARRAY_HTML))
        # 只有 P 数组、没有页面菜单：不足以判定（`P` 变量名太短，易误判）
        no_menu = _PARRAY_HTML.replace('data-page="chat"', '').replace('data-page="create"', '')
        self.assertFalse(ModaoExtractor._is_prd_parray_html(no_menu))
        self.assertFalse(ModaoExtractor._is_prd_parray_menu(no_menu))

    def test_parse_pages_with_states_common_and_req(self):
        modules = ModaoExtractor._parse_prd_parray(_PARRAY_HTML)
        self.assertEqual(2, len(modules))
        self.assertEqual(['聊天Tab与群聊入口', '创建群聊'],
                         [m['name'] for m in modules])
        first = modules[0]['text']
        self.assertIn('【概述】概述A', first)
        self.assertIn('【公共规则】', first)
        self.assertIn('- 公共规则1', first)
        # state_id → 状态名必须回填，不能只留下 id
        self.assertIn('[状态:群聊入口] 群聊入口（修改）', first)
        self.assertIn('➢ 条目1', first)
        self.assertIn('➢ 条目2', first)
        # 空条目状态也要保留标题，避免状态丢失
        self.assertIn('[状态:创建菜单] 创建菜单（新增）', first)
        self.assertIn('➢ 条目3', modules[1]['text'])
        # states 里没有对应 id 时回落用 id，不能丢状态
        self.assertIn('[状态:min]', modules[1]['text'])

    def test_parse_returns_empty_without_p_array(self):
        self.assertEqual([], ModaoExtractor._parse_prd_parray('<html><body>无数组</body></html>'))

    def test_old_doc_page_format_not_parray(self):
        old = ('<section class="doc-page" data-doc-page="a1">'
               '<h2 class="page-heading">页面一</h2></section>'
               '<section class="doc-page" data-doc-page="a2">'
               '<h2 class="page-heading">页面二</h2></section>')
        self.assertFalse(ModaoExtractor._is_prd_parray_html(old))
        # 旧格式判定不受影响
        self.assertTrue(ModaoExtractor._is_prd_report_html(old))
