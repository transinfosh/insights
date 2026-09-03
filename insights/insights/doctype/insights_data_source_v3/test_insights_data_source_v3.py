# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from insights.insights.doctype.insights_data_source_v3.data_warehouse import (
    WarehouseTable,
    WarehouseTableImporter,
)


class TestInsightsDataSourcev3(FrappeTestCase):
    def test_import_in_progress_handles_unset_datetime_on_postgres(self):
        data_source = "test-import-in-progress"
        table_name = "test_table"
        log = frappe.get_doc(
            {
                "doctype": "Insights Table Import Log",
                "data_source": data_source,
                "table_name": table_name,
                "status": "In Progress",
            }
        ).insert(ignore_permissions=True)
        self.addCleanup(frappe.delete_doc, log.doctype, log.name, force=True)

        importer = WarehouseTableImporter(WarehouseTable(data_source, table_name))

        self.assertTrue(importer.import_in_progress())
