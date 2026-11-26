from decimal import Decimal, InvalidOperation

import frappe
from frappe import _
from frappe.model.document import Document


def positive(value, label):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        number = None
    if number is None or not number.is_finite() or number <= 0:
        frappe.throw(_("{0} must be greater than zero.").format(label))
    return number


class VAVRecipeCostSheet(Document):
    def validate(self):
        portions = positive(self.portions, _("Saleable portions per batch"))
        price = positive(self.selling_price, _("Selling price per portion"))
        if not self.ingredients:
            frappe.throw(_("Add at least one ingredient."))

        self.currency = frappe.get_cached_value("Company", self.company, "default_currency")
        batch_cost = Decimal(0)
        for row in self.ingredients:
            def field_label(label):
                return _("Row {0} · {1}").format(row.idx, label)

            pack_size = positive(row.pack_size, field_label(_("Pack size")))
            pack_cost = positive(row.pack_cost, field_label(_("Pack cost")))
            usable_qty = positive(row.usable_qty, field_label(_("Usable batch quantity")))
            usable_yield = positive(row.yield_percent, field_label(_("Usable yield")))
            if usable_yield > 100:
                frappe.throw(_("Row {0} · Usable yield cannot exceed 100%.").format(row.idx))
            cost = pack_cost * usable_qty * 100 / (pack_size * usable_yield)
            row.line_cost = float(cost)
            batch_cost += cost

        self.batch_cost = float(batch_cost)
        self.portion_cost = float(batch_cost / portions)
        self.food_cost_percent = float(batch_cost / portions / price * 100)
