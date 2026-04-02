"""
Patch to create required custom fields for the Patient Patch application.

This script runs after the model sync step to ensure that referenced custom
fields exist on core doctypes.  Without these fields, some features such
as prescription invoice synchronisation and queue tracking will not work.
The fields are only created if they do not already exist to avoid
overwriting user modifications.

Custom fields added here include:
* Sales Invoice: custom_patient_encounter, custom_is_prescription_invoice,
  custom_prescription_invoice_type, custom_previous_prescription_invoice,
  custom_prescription_sync_hash
* Sales Invoice Item: custom_drug_prescription_row_id, custom_medication_request,
  custom_patient_encounter
* Drug Prescription: custom_is_billed, custom_billed_sales_invoice,
  custom_billed_sales_invoice_item
* Patient Encounter: custom_latest_pharmacy_invoice,
  custom_last_prescription_sync_hash, custom_prescription_invoice_status
* Patient: custom_patient_age
* Patient Appointment: custom_jawaab_queue, custom_position_in_queue

If you extend this application further, add any additional required fields
to the list below.
"""

import frappe


def execute():
    """Create custom fields if they do not already exist."""

    # Helper to insert a custom field if missing
    def ensure_field(dt, fieldname, fieldtype="Data", label=None, **kwargs):
        if not frappe.db.exists("Custom Field", f"{dt}-{fieldname}"):
            cf = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": dt,
                "fieldname": fieldname,
                "fieldtype": fieldtype,
                "label": label or fieldname.replace("_", " ").title(),
                **kwargs,
            })
            cf.insert()

    # Sales Invoice fields
    ensure_field("Sales Invoice", "custom_patient_encounter", "Link", "Patient Encounter", options="Patient Encounter")
    ensure_field("Sales Invoice", "custom_is_prescription_invoice", "Check", "Prescription Invoice")
    ensure_field("Sales Invoice", "custom_prescription_invoice_type", "Select", "Prescription Invoice Type", options="Original\nReplacement")
    ensure_field("Sales Invoice", "custom_previous_prescription_invoice", "Link", "Previous Prescription Invoice", options="Sales Invoice")
    ensure_field("Sales Invoice", "custom_prescription_sync_hash", "Data", "Prescription Sync Hash")

    # Sales Invoice Item fields
    ensure_field("Sales Invoice Item", "custom_drug_prescription_row_id", "Link", "Drug Prescription Row", options="Drug Prescription")
    ensure_field("Sales Invoice Item", "custom_medication_request", "Link", "Medication Request", options="Medication Request")
    ensure_field("Sales Invoice Item", "custom_patient_encounter", "Link", "Patient Encounter", options="Patient Encounter")

    # Drug Prescription fields
    ensure_field("Drug Prescription", "custom_is_billed", "Check", "Is Billed")
    ensure_field("Drug Prescription", "custom_billed_sales_invoice", "Link", "Billed Sales Invoice", options="Sales Invoice")
    ensure_field("Drug Prescription", "custom_billed_sales_invoice_item", "Link", "Billed Sales Invoice Item", options="Sales Invoice Item")

    # Patient Encounter fields
    ensure_field("Patient Encounter", "custom_latest_pharmacy_invoice", "Link", "Latest Pharmacy Invoice", options="Sales Invoice")
    ensure_field("Patient Encounter", "custom_last_prescription_sync_hash", "Data", "Last Prescription Sync Hash")
    ensure_field("Patient Encounter", "custom_prescription_invoice_status", "Data", "Prescription Invoice Status")

    # Additional fields for appointment and patient modules
    ensure_field("Patient", "custom_patient_age", "Int", "Patient Age")
    ensure_field("Patient Appointment", "custom_jawaab_queue", "Int", "Jawaab Queue")
    ensure_field("Patient Appointment", "custom_position_in_queue", "Int", "Position In Queue")