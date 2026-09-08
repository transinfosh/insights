from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from insights.insights.doctype.insights_data_source_v3.connectors.frappe_db import (
    get_primary_data_source,
)


class TestSiteDatabase(FrappeTestCase):
    def test_fixture_probe_uses_site_driver_and_preserves_transaction(self):
        if frappe.conf.db_type != "postgres":
            self.skipTest("PostgreSQL site regression")
        doc = frappe.get_doc("Insights Data Source", "Site DB")
        self.assertEqual(doc._db.engine.dialect.name, "postgresql")
        frappe.db.sql("CREATE TEMP TABLE insights_probe_marker (value integer) ON COMMIT DROP")
        frappe.db.sql("INSERT INTO insights_probe_marker VALUES (7)")
        connection = frappe.db._conn
        try:
            doc.before_save()
            self.assertEqual(doc.status, "Active")
            self.assertIs(frappe.db._conn, connection)
            self.assertEqual(frappe.db.sql("SELECT value FROM insights_probe_marker"), ((7,),))
        finally:
            doc._db.engine.dispose()
            frappe.db.sql("DROP TABLE insights_probe_marker")

    def test_v3_fixture_type_cannot_override_site_database_type(self):
        if frappe.conf.db_type != "postgres":
            self.skipTest("PostgreSQL site regression")
        doc = frappe.get_doc("Insights Data Source v3", "Site DB")
        doc.database_type = "MariaDB"
        with patch("frappe.get_doc", return_value=doc):
            self.assertEqual(get_primary_data_source().database_type, "PostgreSQL")
