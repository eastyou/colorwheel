"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    SIZES,
    ColorError,
    build_worksheet,
    find_color,
)
from .render import render_wheel_page, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="colorwheel",
        description="色相环：配色计算、色环图与可打印练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    wheel_parser = subparsers.add_parser("wheel", help="生成色相环与配色关系 HTML")
    wheel_parser.add_argument("--size", type=int, default=12, choices=SIZES, help="格数，默认 12")
    wheel_parser.add_argument("--title", default="", help="页面标题")
    wheel_parser.add_argument("-o", "--output", default=None, help="输出文件")

    color_parser = subparsers.add_parser("color", help="查看单个颜色的配色")
    color_parser.add_argument("name", help="颜色名称，例如 红")
    color_parser.add_argument("--size", type=int, default=12, choices=SIZES, help="格数，默认 12")

    sheet_parser = subparsers.add_parser("sheet", help="生成练习纸 HTML")
    sheet_parser.add_argument("--count", type=int, default=12, help="题目数量，默认 12")
    sheet_parser.add_argument("--size", type=int, default=12, choices=SIZES, help="格数，默认 12")
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet_parser.add_argument("--title", default="色相环练习", help="练习纸标题")
    sheet_parser.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(html_text: str, output: Optional[str]) -> None:
    if not output:
        print(html_text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    print("已写入 %s" % path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "wheel":
            _write_output(render_wheel_page(args.size, args.title), args.output)
            return 0
        if args.command == "color":
            color = find_color(args.name, args.size)
            first, second = color.triadic
            near_first, near_second = color.analogous
            print("%s：%s（色相 %d°）" % (color.name, color.hex, color.hue))
            print(
                "互补色：%s %s"
                % (color.complement.name, color.complement.hex)
            )
            print(
                "三角配色：%s %s、%s %s"
                % (first.name, first.hex, second.name, second.hex)
            )
            print(
                "邻近色：%s %s、%s %s"
                % (near_first.name, near_first.hex, near_second.name, near_second.hex)
            )
            return 0
        items = build_worksheet(args.count, args.size, args.seed, KINDS)
        _write_output(render_worksheet(items, args.title, args.answers), args.output)
        return 0
    except ColorError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
