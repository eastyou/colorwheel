"""色相环页面与练习纸渲染。"""

from __future__ import annotations

import html
import math
from typing import List, Sequence

from .model import Color, WorksheetItem, find_color, step_of, wheel

STYLE = """
@page { size: A4 portrait; margin: 14mm 13mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1f2937;
  font-size: 11pt;
  line-height: 1.65;
}
h1 { font-size: 21pt; margin: 0 0 1.5mm; }
h2 { font-size: 14pt; margin: 6mm 0 3mm; }
.sub { color: #6b7280; font-size: 9.5pt; margin: 0 0 4mm; }
.wheel-wrap { text-align: center; }
.wheel { width: 118mm; height: 118mm; }
table.palette { border-collapse: collapse; width: 100%; font-size: 9pt; margin-top: 3mm; }
table.palette th, table.palette td { border: 0.3pt solid #d7dee6; padding: 1.2mm 1.5mm; text-align: left; }
table.palette th { background: #f1f5f9; color: #475569; font-weight: 600; }
.chip { display: inline-block; width: 4mm; height: 4mm; border-radius: 1mm;
  border: 0.3pt solid #cbd5e1; vertical-align: -0.5mm; margin-right: 1.2mm; }
.mono { font-family: "SFMono-Regular", Consolas, monospace; color: #475569; }
ol.items { margin: 0; padding: 0; list-style: none; display: grid;
  grid-template-columns: 1fr 1fr; gap: 5mm; }
li.item { border: 0.5pt solid #e2e8f0; border-radius: 2mm; padding: 3mm; page-break-inside: avoid; }
.item-head { display: flex; align-items: flex-start; gap: 3mm; }
.swatch { width: 18mm; height: 18mm; border-radius: 50%; flex: 0 0 auto;
  border: 0.5pt solid #cbd5e1; }
.prompt { margin: 0 0 2mm; font-size: 10.5pt; }
.num { color: #b45309; font-weight: 600; }
.line { border-bottom: 0.7pt solid #94a3b8; height: 7mm; }
.answers { page-break-before: always; }
.answers h2 { margin-top: 0; }
.answers ol { margin: 0; padding-left: 7mm; }
.answers li { margin-bottom: 3mm; }
.answers .ans { color: #0f4c81; }
.answers .chip { margin-left: 1.5mm; }
"""


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def _polar(cx: float, cy: float, radius: float, angle: float) -> tuple:
    radians = math.radians(angle)
    return (
        cx + radius * math.sin(radians),
        cy - radius * math.cos(radians),
    )


def _slice_path(cx: float, cy: float, radius: float, start: float, end: float) -> str:
    x1, y1 = _polar(cx, cy, radius, start)
    x2, y2 = _polar(cx, cy, radius, end)
    return (
        "M %.2f %.2f L %.2f %.2f A %.2f %.2f 0 0 1 %.2f %.2f Z"
        % (cx, cy, x1, y1, radius, radius, x2, y2)
    )


def render_wheel_svg(size: int = 12, radius: float = 100.0) -> str:
    """生成色相环 SVG，红色位于正上方，顺时针排列。"""
    colors = wheel(size)
    step = step_of(size)
    center = radius + 16
    box = center * 2
    font = 7.6 if size == 12 else 4.8
    label_radius = radius * 0.68
    parts = [
        '<svg class="wheel" viewBox="0 0 %.1f %.1f" role="img" '
        'aria-label="%d 色色相环">' % (box, box, size)
    ]
    for index, color in enumerate(colors):
        start = index * step
        end = start + step
        parts.append(
            '<path d="%s" fill="%s" stroke="#ffffff" stroke-width="0.8"></path>'
            % (_slice_path(center, center, radius, start, end), color.hex)
        )
        mid = start + step / 2
        x, y = _polar(center, center, label_radius, mid)
        parts.append(
            '<text x="%.2f" y="%.2f" font-size="%.1f" text-anchor="middle" '
            'dominant-baseline="middle" fill="#ffffff" stroke="#00000066" '
            'stroke-width="1.6" paint-order="stroke" '
            'transform="rotate(%.1f %.2f %.2f)">%s</text>'
            % (x, y, font, mid, x, y, _escape(color.name))
        )
    parts.append(
        '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffffff"></circle>'
        % (center, center, radius * 0.2)
    )
    parts.append(
        '<text x="%.1f" y="%.1f" font-size="9" text-anchor="middle" '
        'dominant-baseline="middle" fill="#475569">%d 色相环</text>'
        % (center, center, size)
    )
    parts.append("</svg>")
    return "".join(parts)


def _chip(color: Color) -> str:
    return '<span class="chip" style="background:%s"></span>' % color.hex


def render_wheel_page(size: int = 12, title: str = "") -> str:
    """生成含色相环与配色关系表的页面。"""
    colors = wheel(size)
    heading = title or "%d 色相环与配色关系" % size
    rows: List[str] = []
    for color in colors:
        first, second = color.triadic
        near_first, near_second = color.analogous
        rows.append(
            "<tr><td>%s%s</td><td class=\"mono\">%s</td><td>%s%s</td>"
            "<td>%s%s%s</td><td>%s%s%s</td></tr>"
            % (
                _chip(color),
                _escape(color.name),
                color.hex,
                _chip(color.complement),
                _escape(color.complement.name),
                _chip(first),
                _chip(second),
                _escape("%s、%s" % (first.name, second.name)),
                _chip(near_first),
                _chip(near_second),
                _escape("%s、%s" % (near_first.name, near_second.name)),
            )
        )
    body = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % _escape(heading),
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % _escape(heading),
        '<p class="sub">色相环按 30° 或 15° 等分，红色位于正上方，顺时针递增。</p>',
        '<div class="wheel-wrap">',
        render_wheel_svg(size),
        "</div>",
        "<h2>配色关系</h2>",
        '<table class="palette">',
        "<thead><tr><th>颜色</th><th>色值</th><th>互补色</th>"
        "<th>三角配色</th><th>邻近色</th></tr></thead>",
        "<tbody>",
        "\n".join(rows),
        "</tbody>",
        "</table>",
        "</body>",
        "</html>",
    ]
    return "\n".join(body)


def _item_swatch(item: WorksheetItem) -> str:
    return '<div class="swatch" style="background:%s"></div>' % item.color.hex


def render_worksheet(
    items: Sequence[WorksheetItem],
    title: str = "色相环练习",
    include_answers: bool = False,
) -> str:
    """生成配色练习纸，可选附答案。"""
    if not items:
        raise ValueError("至少需要一道题目")
    cards: List[str] = []
    for index, item in enumerate(items, start=1):
        cards.append(
            '<li class="item"><div class="item-head">%s<div class="body">'
            '<p class="prompt"><span class="num">%d.</span> %s</p>'
            '<div class="line"></div></div></div></li>'
            % (_item_swatch(item), index, _escape(item.prompt))
        )
    body = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % _escape(title),
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % _escape(title),
        '<p class="sub">姓名：__________　班级：__________　日期：__________</p>',
        '<ol class="items">',
        "\n".join(cards),
        "</ol>",
    ]
    if include_answers:
        body.extend(_answer_section(items))
    body.extend(["</body>", "</html>"])
    return "\n".join(body)


def _answer_section(items: Sequence[WorksheetItem]) -> List[str]:
    rows: List[str] = []
    for index, item in enumerate(items, start=1):
        chips = "".join(
            _chip(find_color(name, item.color.size)) for name in item.answer_names
        )
        rows.append(
            '<li><span class="num">%d.</span> <span class="ans">%s</span>%s</li>'
            % (index, _escape(item.answer_text), chips)
        )
    return [
        '<section class="answers">',
        "<h2>参考答案</h2>",
        "<ol>",
        "\n".join(rows),
        "</ol>",
        "</section>",
    ]
