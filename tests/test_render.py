"""色相环页面渲染测试。"""

import unittest

from colorwheel.model import Color, WorksheetItem
from colorwheel.render import render_wheel_page, render_wheel_svg, render_worksheet


class WheelSvgTest(unittest.TestCase):
    def test_slice_count_12(self):
        svg = render_wheel_svg(12)
        self.assertEqual(svg.count("<path"), 12)

    def test_slice_count_24(self):
        svg = render_wheel_svg(24)
        self.assertEqual(svg.count("<path"), 24)

    def test_contains_red(self):
        svg = render_wheel_svg(12)
        self.assertIn("#ff0000", svg)
        self.assertIn("红", svg)

    def test_aria_label(self):
        self.assertIn('aria-label="12 色色相环"', render_wheel_svg(12))

    def test_center_caption(self):
        self.assertIn("12 色相环", render_wheel_svg(12))
        self.assertIn("24 色相环", render_wheel_svg(24))

    def test_text_labels_count(self):
        svg = render_wheel_svg(12)
        self.assertEqual(svg.count("<text"), 13)


class WheelPageTest(unittest.TestCase):
    def test_doctype(self):
        page = render_wheel_page(12)
        self.assertTrue(page.startswith("<!DOCTYPE html>"))

    def test_language(self):
        self.assertIn('lang="zh-CN"', render_wheel_page(12))

    def test_default_title(self):
        self.assertIn("12 色相环与配色关系", render_wheel_page(12))

    def test_custom_title_escaped(self):
        page = render_wheel_page(12, title="<配色> & 色环")
        self.assertIn("&lt;配色&gt; &amp; 色环", page)
        self.assertNotIn("<配色>", page)

    def test_table_rows(self):
        page = render_wheel_page(12)
        self.assertEqual(page.count("<tr><td>"), 12)

    def test_headers(self):
        page = render_wheel_page(12)
        for header in ("颜色", "色值", "互补色", "三角配色", "邻近色"):
            self.assertIn(header, page)

    def test_24_names(self):
        page = render_wheel_page(24)
        self.assertIn("紫罗兰", page)
        self.assertEqual(page.count("<tr><td>"), 24)


class WorksheetRenderTest(unittest.TestCase):
    def setUp(self):
        self.items = [
            WorksheetItem("complement", Color(0, "红")),
            WorksheetItem("triadic", Color(120, "绿")),
        ]

    def test_doctype(self):
        self.assertTrue(render_worksheet(self.items).startswith("<!DOCTYPE html>"))

    def test_card_count(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="item"'), 2)

    def test_swatch_count(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="swatch"'), 2)

    def test_prompt_contains_color(self):
        page = render_worksheet(self.items)
        self.assertIn("「红」", page)
        self.assertIn("「绿」", page)

    def test_name_kind_hides_name(self):
        page = render_worksheet([WorksheetItem("name", Color(0, "红"))])
        self.assertNotIn("红", page)
        self.assertIn("写出这个颜色", page)

    def test_no_answers_default(self):
        self.assertNotIn("参考答案", render_worksheet(self.items))

    def test_answers_included(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertIn("参考答案", page)
        self.assertIn("青", page)

    def test_empty_items(self):
        with self.assertRaises(ValueError):
            render_worksheet([])

    def test_custom_title(self):
        page = render_worksheet(self.items, title="配色小测")
        self.assertIn("配色小测", page)

    def test_title_escaped(self):
        page = render_worksheet(self.items, title="A&B")
        self.assertIn("A&amp;B", page)


if __name__ == "__main__":
    unittest.main()
