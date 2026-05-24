# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestInsightsSemanticModel(FrappeTestCase):
	def test_sync_fields_from_columns_preserves_metadata_and_removes_stale_fields(self):
		model = frappe.new_doc("Insights Semantic Model")
		model.title = "Sales Orders"
		model.model_name = "sales_orders"
		model.append(
			"fields",
			{
				"fieldname": "customer",
				"label": "Customer",
				"data_type": "String",
				"semantic_type": "Dimension",
				"description": "Manually curated description",
			},
		)
		model.append(
			"fields",
			{
				"fieldname": "old_field",
				"label": "Old Field",
				"data_type": "String",
				"semantic_type": "Dimension",
			},
		)

		model.sync_fields_from_columns(
			[
				{"name": "customer", "type": "String"},
				{"name": "amount", "type": "Decimal"},
				{"name": "order_date", "type": "Date"},
			]
		)

		fields = {field.fieldname: field for field in model.fields}
		self.assertEqual(set(fields), {"customer", "amount", "order_date"})
		self.assertEqual(fields["customer"].label, "Customer")
		self.assertEqual(fields["customer"].description, "Manually curated description")
		self.assertEqual(fields["amount"].semantic_type, "Measure")
		self.assertEqual(fields["order_date"].semantic_type, "Time")
