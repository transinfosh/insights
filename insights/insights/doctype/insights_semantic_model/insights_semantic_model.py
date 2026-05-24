# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InsightsSemanticModel(Document):
	def validate(self):
		if not self.model_name and self.title:
			self.model_name = frappe.scrub(self.title)

	@frappe.whitelist()
	def sync_fields_from_query(self):
		if not self.query:
			frappe.throw("Select an Insights Query v3 before syncing fields.")

		query = frappe.get_doc("Insights Query v3", self.query)
		columns = query.get_columns_for_selection()
		self.sync_fields_from_columns(columns)
		self.save()
		return self

	def sync_fields_from_columns(self, columns: list[dict]) -> None:
		existing_fields = {field.fieldname: field.as_dict() for field in self.fields}
		self.set("fields", [])

		for column in columns:
			fieldname = column.get("name")
			if not fieldname:
				continue

			data_type = column.get("type") or "Unknown"
			existing = existing_fields.get(fieldname, {})
			self.append(
				"fields",
				{
					"fieldname": fieldname,
					"label": existing.get("label") or fieldname.replace("_", " ").title(),
					"data_type": data_type,
					"semantic_type": existing.get("semantic_type") or get_default_semantic_type(data_type),
					"is_sensitive": existing.get("is_sensitive", 0),
					"is_filterable": existing.get("is_filterable", 1),
					"is_groupable": existing.get("is_groupable", is_groupable_by_default(data_type)),
					"synonyms": existing.get("synonyms"),
					"description": existing.get("description"),
				},
			)


def get_default_semantic_type(data_type: str) -> str:
	if data_type in {"Date", "Datetime", "Time"}:
		return "Time"
	if data_type in {"Integer", "Long Int", "Decimal"}:
		return "Measure"
	return "Dimension"


def is_groupable_by_default(data_type: str) -> int:
	return 0 if get_default_semantic_type(data_type) == "Measure" else 1


@frappe.whitelist()
def get_or_create_for_query(query: str):
	if not query:
		frappe.throw("Query is required.")

	query_doc = frappe.get_doc("Insights Query v3", query)
	model_name = frappe.db.get_value("Insights Semantic Model", {"query": query}, "name")

	if model_name:
		model = frappe.get_doc("Insights Semantic Model", model_name)
	else:
		model = frappe.new_doc("Insights Semantic Model")
		model.title = query_doc.title or query_doc.name
		model.model_name = make_unique_model_name(frappe.scrub(model.title or query_doc.name))
		model.workbook = query_doc.workbook
		model.query = query_doc.name
		model.insert()

	model.sync_fields_from_query()
	return model.as_dict()


def make_unique_model_name(base_name: str) -> str:
	base_name = base_name or "semantic_model"
	model_name = base_name
	index = 2
	while frappe.db.exists("Insights Semantic Model", {"model_name": model_name}):
		model_name = f"{base_name}_{index}"
		index += 1
	return model_name
