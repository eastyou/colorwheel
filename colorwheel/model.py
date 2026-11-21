"""色相环、配色关系与练习纸题目。"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

KINDS = ("name", "complement", "analogous", "triadic")
SIZES = (12, 24)

WHEEL_12: Tuple[Tuple[int, str], ...] = (
    (0, "红"),
    (30, "橙"),
    (60, "黄"),
    (90, "黄绿"),
    (120, "绿"),
    (150, "青绿"),
    (180, "青"),
    (210, "蓝"),
    (240, "靛"),
    (270, "紫"),
    (300, "紫红"),
    (330, "品红"),
)

WHEEL_24: Tuple[Tuple[int, str], ...] = (
    (0, "红"),
    (15, "朱红"),
    (30, "橙红"),
    (45, "橙"),
    (60, "橙黄"),
    (75, "金黄"),
    (90, "黄"),
    (105, "黄绿"),
    (120, "草绿"),
    (135, "绿"),
    (150, "青绿"),
    (165, "青"),
    (180, "天青"),
    (195, "湖蓝"),
    (210, "蓝"),
    (225, "宝蓝"),
    (240, "靛"),
    (255, "蓝紫"),
    (270, "紫"),
    (285, "紫罗兰"),
    (300, "紫红"),
    (315, "玫红"),
    (330, "品红"),
    (345, "洋红"),
)

TABLES: Dict[int, Tuple[Tuple[int, str], ...]] = {12: WHEEL_12, 24: WHEEL_24}


class ColorError(ValueError):
    """颜色与色相环相关的输入错误。"""


def _check_int(value: object, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ColorError("%s必须是整数" % name)
    if value < low or value > high:
        raise ColorError("%s需在 %d 到 %d 之间" % (name, low, high))
    return value


def _hue_to_rgb(p: float, q: float, t: float) -> float:
    if t < 0:
        t += 1
    if t > 1:
        t -= 1
    if t < 1 / 6:
        return p + (q - p) * 6 * t
    if t < 1 / 2:
        return q
    if t < 2 / 3:
        return p + (q - p) * (2 / 3 - t) * 6
    return p


def hsl_to_hex(hue: int, saturation: int = 100, lightness: int = 50) -> str:
    """HSL 转十六进制色值，色相 0–359，饱和度与亮度 0–100。"""
    _check_int(hue, "色相", 0, 359)
    _check_int(saturation, "饱和度", 0, 100)
    _check_int(lightness, "亮度", 0, 100)
    h = (hue % 360) / 360.0
    s = saturation / 100.0
    l = lightness / 100.0
    if s == 0:
        red = green = blue = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        red = _hue_to_rgb(p, q, h + 1 / 3)
        green = _hue_to_rgb(p, q, h)
        blue = _hue_to_rgb(p, q, h - 1 / 3)
    return "#%02x%02x%02x" % (
        int(round(red * 255)),
        int(round(green * 255)),
        int(round(blue * 255)),
    )


def _check_size(size: int) -> int:
    if isinstance(size, bool) or not isinstance(size, int):
        raise ColorError("色相环格数必须是整数")
    if size not in TABLES:
        raise ColorError("色相环格数只能是 12 或 24")
    return size


def step_of(size: int) -> int:
    """返回每格对应的色相角度。"""
    _check_size(size)
    return 360 // size


@dataclass(frozen=True)
class Color:
    """色相环上的一个颜色。"""

    hue: int
    name: str
    size: int = 12

    def __post_init__(self) -> None:
        _check_size(self.size)
        _check_int(self.hue, "色相", 0, 359)
        if not isinstance(self.name, str) or not self.name:
            raise ColorError("颜色名称不能为空")

    @property
    def hex(self) -> str:
        return hsl_to_hex(self.hue)

    @property
    def complement(self) -> "Color":
        return nearest_color(self.hue + 180, self.size)

    @property
    def analogous(self) -> Tuple["Color", "Color"]:
        step = step_of(self.size)
        return (
            nearest_color(self.hue - step, self.size),
            nearest_color(self.hue + step, self.size),
        )

    @property
    def triadic(self) -> Tuple["Color", "Color"]:
        return (
            nearest_color(self.hue + 120, self.size),
            nearest_color(self.hue + 240, self.size),
        )


def wheel(size: int = 12) -> List[Color]:
    """返回指定格数的色相环，从红色开始按顺时针排列。"""
    _check_size(size)
    return [Color(hue=hue, name=name, size=size) for hue, name in TABLES[size]]


def nearest_color(hue: int, size: int = 12) -> Color:
    """把任意色相归到色相环上最接近的一格。"""
    _check_size(size)
    if isinstance(hue, bool) or not isinstance(hue, int):
        raise ColorError("色相必须是整数")
    step = step_of(size)
    index = int(round((hue % 360) / step)) % size
    return wheel(size)[index]


def find_color(text: str, size: int = 12) -> Color:
    """按颜色名称查找色相环上的颜色。"""
    _check_size(size)
    if not isinstance(text, str) or not text.strip():
        raise ColorError("请输入颜色名称")
    cleaned = text.strip()
    for color in wheel(size):
        if color.name == cleaned:
            return color
    names = "、".join(color.name for color in wheel(size))
    raise ColorError("「%s」不在此色相环中，可选：%s" % (cleaned, names))


def names(size: int = 12) -> List[str]:
    return [color.name for color in wheel(size)]


def _normalize_answer(text: str) -> List[str]:
    if not isinstance(text, str):
        return []
    parts = re.split(r"[\s,，、;；/和与及]+", text.strip())
    return [part for part in parts if part]


@dataclass(frozen=True)
class WorksheetItem:
    """一道配色练习题。"""

    kind: str
    color: Color

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ColorError("未知题型：%s" % self.kind)

    @property
    def answer_names(self) -> Tuple[str, ...]:
        if self.kind == "name":
            return (self.color.name,)
        if self.kind == "complement":
            return (self.color.complement.name,)
        if self.kind == "analogous":
            first, second = self.color.analogous
            return (first.name, second.name)
        first, second = self.color.triadic
        return (first.name, second.name)

    @property
    def answer_text(self) -> str:
        return "、".join(self.answer_names)

    @property
    def prompt(self) -> str:
        if self.kind == "name":
            return "写出这个颜色在色相环上的名称。"
        if self.kind == "complement":
            return "「%s」的互补色是什么？" % self.color.name
        if self.kind == "analogous":
            return "与「%s」相邻的两个邻近色是什么？" % self.color.name
        return "与「%s」组成三角配色的另外两种颜色是什么？" % self.color.name


def check_answer(item: WorksheetItem, text: str) -> bool:
    """校验答案，忽略顺序与分隔符。"""
    if not isinstance(item, WorksheetItem):
        return False
    given = _normalize_answer(text)
    expected = list(item.answer_names)
    if len(given) != len(expected):
        return False
    return sorted(given) == sorted(expected)


def build_worksheet(
    count: int = 12,
    size: int = 12,
    seed: Optional[int] = None,
    kinds: Sequence[str] = KINDS,
) -> List[WorksheetItem]:
    """随机抽取配色题，同一道题不会重复。"""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ColorError("题目数量必须是正整数")
    _check_size(size)
    if not kinds:
        raise ColorError("至少需要一种题型")
    for kind in kinds:
        if kind not in KINDS:
            raise ColorError("未知题型：%s" % kind)
    candidates = [(kind, color) for kind in kinds for color in wheel(size)]
    if count > len(candidates):
        raise ColorError("可用题目不足 %d 道" % count)
    rng = random.Random(seed)
    chosen = rng.sample(candidates, count)
    return [WorksheetItem(kind=kind, color=color) for kind, color in chosen]
