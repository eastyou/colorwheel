"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from colorwheel.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class WheelCommandTest(unittest.TestCase):
    def test_stdout(self):
        code, out, _ = run_cli(["wheel"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)
        self.assertIn("12 色相环", out)

    def test_24(self):
        code, out, _ = run_cli(["wheel", "--size", "24"])
        self.assertEqual(code, 0)
        self.assertIn("紫罗兰", out)

    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "wheel.html")
            code, out, _ = run_cli(["wheel", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            with open(target, encoding="utf-8") as handle:
                self.assertIn("色相环", handle.read())

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "a", "b", "wheel.html")
            code, _, _ = run_cli(["wheel", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))

    def test_invalid_size(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["wheel", "--size", "16"])
        self.assertEqual(ctx.exception.code, 2)


class ColorCommandTest(unittest.TestCase):
    def test_red(self):
        code, out, _ = run_cli(["color", "红"])
        self.assertEqual(code, 0)
        self.assertIn("#ff0000", out)
        self.assertIn("互补色", out)
        self.assertIn("青", out)

    def test_triadic_line(self):
        code, out, _ = run_cli(["color", "红"])
        self.assertEqual(code, 0)
        self.assertIn("三角配色", out)
        self.assertIn("绿", out)
        self.assertIn("靛", out)

    def test_analogous_line(self):
        code, out, _ = run_cli(["color", "红"])
        self.assertEqual(code, 0)
        self.assertIn("邻近色", out)
        self.assertIn("橙", out)

    def test_24_only_color(self):
        code, out, _ = run_cli(["color", "紫罗兰", "--size", "24"])
        self.assertEqual(code, 0)
        self.assertIn("紫罗兰", out)

    def test_24_color_in_12_wheel(self):
        code, _, err = run_cli(["color", "紫罗兰"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_unknown_color(self):
        code, _, err = run_cli(["color", "天蓝"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class SheetCommandTest(unittest.TestCase):
    def test_stdout(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_card_count(self):
        code, out, _ = run_cli(["sheet", "--count", "7", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="item"'), 7)

    def test_answers(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--seed", "3", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "4", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            self.assertTrue(os.path.exists(target))

    def test_custom_title(self):
        code, out, _ = run_cli(["sheet", "--count", "1", "--title", "色环小测"])
        self.assertEqual(code, 0)
        self.assertIn("色环小测", out)

    def test_invalid_count(self):
        code, _, err = run_cli(["sheet", "--count", "0"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_seed_reproducible(self):
        _, first, _ = run_cli(["sheet", "--count", "4", "--seed", "9"])
        _, second, _ = run_cli(["sheet", "--count", "4", "--seed", "9"])
        self.assertEqual(first, second)

    def test_24_wheel(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--size", "24", "--seed", "5"])
        self.assertEqual(code, 0)
        self.assertIn("色相环练习", out)


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
