"""色相环与配色模型测试。"""

import unittest
from dataclasses import FrozenInstanceError

from colorwheel.model import (
    KINDS,
    Color,
    ColorError,
    WorksheetItem,
    build_worksheet,
    check_answer,
    find_color,
    hsl_to_hex,
    names,
    nearest_color,
    step_of,
    wheel,
)


class HslToHexTest(unittest.TestCase):
    def test_primaries(self):
        self.assertEqual(hsl_to_hex(0), "#ff0000")
        self.assertEqual(hsl_to_hex(120), "#00ff00")
        self.assertEqual(hsl_to_hex(240), "#0000ff")

    def test_secondaries(self):
        self.assertEqual(hsl_to_hex(60), "#ffff00")
        self.assertEqual(hsl_to_hex(180), "#00ffff")
        self.assertEqual(hsl_to_hex(300), "#ff00ff")

    def test_rejects_out_of_range(self):
        with self.assertRaises(ColorError):
            hsl_to_hex(360)
        with self.assertRaises(ColorError):
            hsl_to_hex(-1)

    def test_gray_when_no_saturation(self):
        self.assertEqual(hsl_to_hex(0, 0, 50), "#808080")

    def test_black_and_white(self):
        self.assertEqual(hsl_to_hex(0, 100, 0), "#000000")
        self.assertEqual(hsl_to_hex(0, 100, 100), "#ffffff")

    def test_invalid_hue(self):
        for bad in (-1, "0", None, True):
            with self.assertRaises(ColorError):
                hsl_to_hex(bad)

    def test_invalid_saturation(self):
        with self.assertRaises(ColorError):
            hsl_to_hex(0, 101)

    def test_invalid_lightness(self):
        with self.assertRaises(ColorError):
            hsl_to_hex(0, 50, -1)


class WheelTest(unittest.TestCase):
    def test_lengths(self):
        self.assertEqual(len(wheel(12)), 12)
        self.assertEqual(len(wheel(24)), 24)

    def test_first_is_red(self):
        self.assertEqual(wheel(12)[0].name, "红")
        self.assertEqual(wheel(12)[0].hue, 0)

    def test_hue_step(self):
        hues = [color.hue for color in wheel(24)]
        self.assertEqual(hues, list(range(0, 360, 15)))

    def test_unique_names(self):
        for size in (12, 24):
            values = [color.name for color in wheel(size)]
            self.assertEqual(len(values), len(set(values)))

    def test_hex_format(self):
        for color in wheel(24):
            self.assertRegex(color.hex, r"^#[0-9a-f]{6}$")

    def test_invalid_size(self):
        for bad in (10, True, "12"):
            with self.assertRaises(ColorError):
                wheel(bad)

    def test_names_helper(self):
        self.assertEqual(len(names(12)), 12)
        self.assertIn("紫罗兰", names(24))
        self.assertNotIn("紫罗兰", names(12))


class StepTest(unittest.TestCase):
    def test_steps(self):
        self.assertEqual(step_of(12), 30)
        self.assertEqual(step_of(24), 15)

    def test_invalid(self):
        with self.assertRaises(ColorError):
            step_of(8)


class ColorTest(unittest.TestCase):
    def test_complement(self):
        self.assertEqual(Color(0, "红").complement.name, "青")
        self.assertEqual(Color(0, "红").complement.hue, 180)

    def test_analogous(self):
        first, second = Color(0, "红").analogous
        self.assertEqual(first.name, "品红")
        self.assertEqual(second.name, "橙")

    def test_analogous_24(self):
        first, second = Color(0, "红", 24).analogous
        self.assertEqual(first.hue, 345)
        self.assertEqual(second.hue, 15)

    def test_triadic(self):
        first, second = Color(0, "红").triadic
        self.assertEqual(first.name, "绿")
        self.assertEqual(second.name, "靛")

    def test_triadic_24(self):
        first, second = Color(0, "红", 24).triadic
        self.assertEqual((first.hue, second.hue), (120, 240))

    def test_invalid_hue(self):
        with self.assertRaises(ColorError):
            Color(400, "红")

    def test_invalid_size(self):
        with self.assertRaises(ColorError):
            Color(0, "红", 16)

    def test_empty_name(self):
        with self.assertRaises(ColorError):
            Color(0, "")

    def test_frozen(self):
        color = Color(0, "红")
        with self.assertRaises(FrozenInstanceError):
            color.hue = 30


class NearestTest(unittest.TestCase):
    def test_round_down(self):
        self.assertEqual(nearest_color(10, 12).name, "红")

    def test_round_up(self):
        self.assertEqual(nearest_color(20, 12).name, "橙")

    def test_wrap(self):
        self.assertEqual(nearest_color(359, 12).name, "红")

    def test_24(self):
        self.assertEqual(nearest_color(8, 24).name, "朱红")

    def test_invalid_hue(self):
        with self.assertRaises(ColorError):
            nearest_color("30")

    def test_invalid_size(self):
        with self.assertRaises(ColorError):
            nearest_color(30, 16)


class FindColorTest(unittest.TestCase):
    def test_found(self):
        self.assertEqual(find_color("红").hue, 0)
        self.assertEqual(find_color(" 紫 ").name, "紫")

    def test_24_only(self):
        self.assertEqual(find_color("紫罗兰", 24).hue, 285)
        with self.assertRaises(ColorError):
            find_color("紫罗兰", 12)

    def test_unknown(self):
        with self.assertRaises(ColorError) as ctx:
            find_color("天蓝")
        self.assertIn("可选", str(ctx.exception))

    def test_empty(self):
        with self.assertRaises(ColorError):
            find_color("   ")

    def test_non_string(self):
        with self.assertRaises(ColorError):
            find_color(None)


class WorksheetItemTest(unittest.TestCase):
    def test_name_answer(self):
        item = WorksheetItem("name", Color(0, "红"))
        self.assertEqual(item.answer_names, ("红",))
        self.assertEqual(item.answer_text, "红")

    def test_complement_answer(self):
        item = WorksheetItem("complement", Color(0, "红"))
        self.assertEqual(item.answer_names, ("青",))

    def test_analogous_answer(self):
        item = WorksheetItem("analogous", Color(0, "红"))
        self.assertEqual(item.answer_names, ("品红", "橙"))

    def test_triadic_answer(self):
        item = WorksheetItem("triadic", Color(0, "红"))
        self.assertEqual(item.answer_names, ("绿", "靛"))

    def test_prompt_contains_name(self):
        for kind in ("complement", "analogous", "triadic"):
            self.assertIn("红", WorksheetItem(kind, Color(0, "红")).prompt)

    def test_name_prompt_hides_name(self):
        self.assertNotIn("红", WorksheetItem("name", Color(0, "红")).prompt)

    def test_invalid_kind(self):
        with self.assertRaises(ColorError):
            WorksheetItem("rainbow", Color(0, "红"))


class CheckAnswerTest(unittest.TestCase):
    def test_single(self):
        item = WorksheetItem("complement", Color(0, "红"))
        self.assertTrue(check_answer(item, "青"))

    def test_two_in_order(self):
        item = WorksheetItem("triadic", Color(0, "红"))
        self.assertTrue(check_answer(item, "绿、靛"))

    def test_two_reversed(self):
        item = WorksheetItem("triadic", Color(0, "红"))
        self.assertTrue(check_answer(item, "靛 绿"))

    def test_wrong(self):
        item = WorksheetItem("complement", Color(0, "红"))
        self.assertFalse(check_answer(item, "紫"))

    def test_too_many(self):
        item = WorksheetItem("complement", Color(0, "红"))
        self.assertFalse(check_answer(item, "青、蓝"))

    def test_empty(self):
        item = WorksheetItem("name", Color(0, "红"))
        self.assertFalse(check_answer(item, ""))

    def test_non_item(self):
        self.assertFalse(check_answer(None, "红"))


class BuildWorksheetTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(build_worksheet(9, 12, seed=1)), 9)

    def test_unique_items(self):
        items = build_worksheet(12, 12, seed=2)
        keys = {(item.kind, item.color.name) for item in items}
        self.assertEqual(len(keys), 12)

    def test_deterministic(self):
        first = build_worksheet(6, 24, seed=3)
        second = build_worksheet(6, 24, seed=3)
        self.assertEqual(
            [(item.kind, item.color.name) for item in first],
            [(item.kind, item.color.name) for item in second],
        )

    def test_all_kinds(self):
        items = build_worksheet(8, 12, seed=4)
        for item in items:
            self.assertIn(item.kind, KINDS)

    def test_custom_kinds(self):
        items = build_worksheet(5, 12, seed=5, kinds=("complement",))
        self.assertTrue(all(item.kind == "complement" for item in items))

    def test_invalid_count(self):
        for bad in (0, -2, True, "6"):
            with self.assertRaises(ColorError):
                build_worksheet(bad)

    def test_invalid_size(self):
        with self.assertRaises(ColorError):
            build_worksheet(3, 16)

    def test_invalid_kind(self):
        with self.assertRaises(ColorError):
            build_worksheet(3, 12, kinds=("rainbow",))

    def test_empty_kinds(self):
        with self.assertRaises(ColorError):
            build_worksheet(3, 12, kinds=())

    def test_too_many(self):
        with self.assertRaises(ColorError):
            build_worksheet(100, 12)


if __name__ == "__main__":
    unittest.main()
