# colorwheel

[![CI](https://github.com/eastyou/colorwheel/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/colorwheel/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

色相环：12 / 24 色配色计算、SVG 色环图与可打印练习纸。

## 特性

- 12 色与 24 色两套色相环，红色在正上方，顺时针排列
- 自动计算互补色、邻近色与三角配色
- HSL 转十六进制，色值与名称一一对应
- 生成含色环与配色关系表的 A4 页面
- 练习纸涵盖认色、互补色、邻近色、三角配色四类题
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

```bash
colorwheel wheel
colorwheel wheel --size 24 -o wheel.html
colorwheel color 红
colorwheel color 紫罗兰 --size 24
colorwheel sheet --count 12 --seed 3 --answers -o sheet.html
```

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--size` | 色相环格数，可选 12 或 24 | 12 |
| `--count` | 练习题数量 | 12 |
| `--seed` | 随机种子 | 无 |
| `--answers` | 追加参考答案 | 关闭 |

## 配色关系

- 互补色：色相相差 180°
- 三角配色：色相相差 120° 与 240°
- 邻近色：色相环上左右相邻的两格

## 示例

- [examples/colorwheel.html](examples/colorwheel.html)：24 色相环与配色关系表
- [examples/colorwheel-sheet.html](examples/colorwheel-sheet.html)：12 道配色练习，带答案

## 测试

```bash
python -m unittest discover -s tests -v
```

## 说明

色值由 HSL（饱和度 100%、亮度 50%）计算，用于教学演示与版面配色参考。印刷前请以设计软件的色值为准。

## 协议

MIT © 2026 eastyou
