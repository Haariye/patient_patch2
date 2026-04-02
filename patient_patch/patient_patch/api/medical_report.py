"""
Server-side helpers for the Medical Report feature.

These functions are whitelisted so they can be called from client-side code.
They handle fetching default values from a Patient Encounter and creating
Medical Report documents on behalf of the user. The logic here assumes
that standard fields exist on the Patient Encounter and Patient doctypes
for diagnosis, treatment and practitioner. If a field does not exist,
empty strings are returned for those values.
"""

from __future__ import annotations

import json
from typing import Dict, Any

import frappe
from frappe import _
from frappe.utils import nowdate


def _get_field(doc: frappe.model.document.Document, *fieldnames: str) -> str:
    """Return the first non-empty value from a list of field names on a doc.

    If none of the fields exist or have a truthy value, an empty string is
    returned. This helper is used to extract diagnosis or treatment from
    Patient Encounter which may store this data under different field names
    depending on customisation.
    """
    for field in fieldnames:
        try:
            value = doc.get(field)
        except Exception:
            value = None
        if value:
            return value
    return ""


@frappe.whitelist()
def get_medical_report_defaults(encounter_name: str) -> Dict[str, Any]:
    """Return a dictionary of default values for creating a Medical Report.

    This function pulls data from the specified Patient Encounter and its
    linked Patient record. It attempts to extract diagnosis and treatment
    information from common field names on the encounter. Missing values
    are returned as empty strings to avoid client-side errors.

    Args:
        encounter_name: The name (primary key) of the Patient Encounter.

    Returns:
        A dict containing default values for the Medical Report fields.
    """
    if not encounter_name:
        frappe.throw(_("Encounter name is required"))

    encounter = frappe.get_doc("Patient Encounter", encounter_name)
    patient = frappe.get_doc("Patient", encounter.patient)

    # Extract diagnosis and treatment using common field names.  If your
    # environment stores this information differently, add more fieldnames
    # to the lists below.
    diagnosis = _get_field(
        encounter,
        "diagnosis",
        "primary_diagnosis",
        "assessment",
        "chief_complaint",
    )
    treatment = _get_field(
        encounter,
        "treatment",
        "treatment_plan",
        "management",
    )

    values: Dict[str, Any] = {
        "patient": encounter.patient,
        "patient_name": getattr(patient, "patient_name", encounter.patient),
        "patient_id": encounter.patient,
        "age": getattr(patient, "age", None),
        "sex": getattr(patient, "sex", None),
        "report_date": nowdate(),
        "due_date": None,
        "diagnosis": diagnosis,
        "treatment": treatment,
        "recommendation": "",
        "doctor": getattr(encounter, "practitioner", None),
    }
    return values


@frappe.whitelist()
def create_medical_report(data: Dict[str, Any] | str) -> str:
    """Create and save a Medical Report from provided data.

    The client is expected to supply a dictionary of field values matching
    the Medical Report DocType.  This method will insert a new document
    without any additional permissions checks, and returns the new
    document name.  If `data` is a JSON string it will be parsed.

    Args:
        data: A dict or JSON string containing the fields for the new
            Medical Report.

    Returns:
        The name of the newly created Medical Report document.
    """
    # Parse string input
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            data = {}

    if not isinstance(data, dict):
        frappe.throw(_("Invalid data for Medical Report"))

    # Ensure required fields exist; let DocType validation handle missing
    report = frappe.new_doc("Medical Report")
    # Reference number is required; generate a simple one if not provided
    ref_no = data.get("ref_no")
    if not ref_no:
        # Use doc.name temporarily as ref_no; this will be replaced on
        # insertion because Medical Report uses autoname = field:ref_no
        ref_no = frappe.utils.now_datetime().strftime("MR-%Y%m%d-%H%M%S")
    data.setdefault("ref_no", ref_no)

    report.update(data)
    # Insert ignoring permissions to allow creation via the API
    report.insert(ignore_permissions=True)
    # Submit the report so it appears in print view if necessary
    if getattr(report, "docstatus", 0) == 0 and report.is_submittable:
        report.submit()
    return report.name