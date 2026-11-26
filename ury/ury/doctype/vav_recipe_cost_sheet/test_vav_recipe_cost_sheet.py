from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import frappe

from ury.ury.doctype.vav_recipe_cost_sheet.vav_recipe_cost_sheet import VAVRecipeCostSheet


class TestRecipeCostSheet(TestCase):
    def setUp(self):
        self.chicken = SimpleNamespace(idx=1, pack_cost=18, pack_size=1, yield_percent=80, usable_qty=2.5)
        self.rice = SimpleNamespace(idx=2, pack_cost=42, pack_size=5, yield_percent=100, usable_qty=1.5)
        self.sheet = SimpleNamespace(company="Example", portions=10, selling_price=25,
                                    ingredients=[self.chicken, self.rice])
        self.currency = patch.object(frappe, "get_cached_value", return_value="AED")
        self.currency.start()
        self.addCleanup(self.currency.stop)

    def test_yield_and_pack_conversion(self):
        VAVRecipeCostSheet.validate(self.sheet)
        self.assertEqual(self.sheet.currency, "AED")
        self.assertAlmostEqual(self.chicken.line_cost, 56.25)
        self.assertAlmostEqual(self.rice.line_cost, 12.60)
        self.assertAlmostEqual(self.sheet.batch_cost, 68.85)
        self.assertAlmostEqual(self.sheet.portion_cost, 6.885)
        self.assertAlmostEqual(self.sheet.food_cost_percent, 27.54)

    def test_missing_or_invalid_inputs(self):
        for obj, key, bad in [
            (self.chicken, "pack_cost", None), (self.chicken, "pack_size", 0),
            (self.chicken, "usable_qty", -1), (self.chicken, "yield_percent", 101),
            (self.chicken, "yield_percent", 0), (self.sheet, "portions", 0),
            (self.sheet, "selling_price", 0), (self.sheet, "ingredients", []),
        ]:
            with self.subTest(key=key, value=bad), patch.object(obj, key, bad):
                with self.assertRaises(frappe.ValidationError):
                    VAVRecipeCostSheet.validate(self.sheet)

    def test_recalculation_after_portion_change(self):
        VAVRecipeCostSheet.validate(self.sheet)
        self.sheet.portions = 5
        VAVRecipeCostSheet.validate(self.sheet)
        self.assertAlmostEqual(self.sheet.portion_cost, 13.77)
        self.assertAlmostEqual(self.sheet.food_cost_percent, 55.08)
