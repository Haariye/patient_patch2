from __future__ import annotations

import json
from typing import Any, Dict, List

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, today


def _has_field(doctype: str, fieldname: str) -> bool:
    try:
        return frappe.get_meta(doctype).has_field(fieldname)
    except Exception:
        return False


def _get_value(doc, fieldnames: List[str], default=""):
    for f in fieldnames:
        try:
            if hasattr(doc, "meta") and doc.meta.has_field(f):
                val = doc.get(f)
                if val not in (None, "", []):
                    return val
        except Exception:
            pass
    return default


def _get_patient_age(patient_doc) -> str:
    age = _get_value(patient_doc, ["age"], "")
    if age:
        return str(age)

    dob = _get_value(patient_doc, ["dob"], None)
    if not dob:
        return ""

    dob = getdate(dob)
    t = getdate(today())
    years = t.year - dob.year - ((t.month, t.day) < (dob.month, dob.day))
    return str(years)


def _rows_to_text(rows, candidate_fields: List[str]) -> str:
    out = []
    for row in rows or []:
        parts = []
        for f in candidate_fields:
            try:
                val = row.get(f)
            except Exception:
                val = None
            if val not in (None, ""):
                parts.append(str(val))
        if parts:
            out.append(" - ".join(parts))
    return "\n".join(out)


def _build_diagnosis_text(encounter) -> str:
    blocks = []

    main_diagnosis = _get_value(
        encounter,
        ["diagnosis", "primary_diagnosis", "assessment", "clinical_impression", "diagnosis_note"],
        "",
    )
    if main_diagnosis:
        blocks.append(str(main_diagnosis))

    symptoms = _get_value(encounter, ["symptoms", "chief_complaint"], "")
    if symptoms:
        blocks.append(f"Symptoms: {symptoms}")

    # Try common child tables safely
    child_candidates = [
        ("diagnosis", ["diagnosis", "description", "diagnosis_name"]),
        ("diagnosis_table", ["diagnosis", "description", "diagnosis_name"]),
        ("examination_detail", ["examination", "finding", "description", "remarks"]),
        ("examination_details", ["examination", "finding", "description", "remarks"]),
        ("lab_test_prescription", ["lab_test_name", "test_name", "description"]),
        ("procedure_prescription", ["procedure", "description"]),
    ]

    for table_field, fields in child_candidates:
        if encounter.meta.has_field(table_field):
            txt = _rows_to_text(encounter.get(table_field), fields)
            if txt:
                blocks.append(txt)

    return "\n\n".join([b for b in blocks if b]).strip()


def _build_treatment_text(encounter) -> str:
    blocks = []

    main_treatment = _get_value(
        encounter,
        ["treatment", "treatment_plan", "management", "plan"],
        "",
    )
    if main_treatment:
        blocks.append(str(main_treatment))

    child_candidates = [
        ("drug_prescription", ["drug_name", "drug_code", "dosage", "period", "comment"]),
        ("therapies", ["therapy_type", "description"]),
        ("procedure_prescription", ["procedure", "description"]),
    ]

    for table_field, fields in child_candidates:
        if encounter.meta.has_field(table_field):
            txt = _rows_to_text(encounter.get(table_field), fields)
            if txt:
                blocks.append(txt)

    return "\n\n".join([b for b in blocks if b]).strip()


@frappe.whitelist()
def get_medical_report_defaults(encounter_name: str) -> Dict[str, Any]:
    if not encounter_name:
        frappe.throw(_("Consultation reference is required"))

    encounter = frappe.get_doc("Patient Encounter", encounter_name)
    patient = frappe.get_doc("Patient", encounter.patient)

    patient_name = _get_value(patient, ["patient_name", "first_name"], encounter.patient)
    sex = _get_value(patient, ["sex", "gender"], "")
    age = _get_patient_age(patient)
    practitioner = _get_value(encounter, ["practitioner"], "")

    return {
        "naming_series": "MR-.YYYY.-.#####",
        "patient": encounter.patient,
        "patient_name": patient_name,
        "patient_id": encounter.patient,
        "age": age,
        "sex": sex,
        "report_date": nowdate(),
        "consultation_reference": encounter.name,
        "doctor": practitioner,
        "diagnosis": _build_diagnosis_text(encounter),
        "treatment": _build_treatment_text(encounter),
        "recommendation": ""
    }


@frappe.whitelist()
def create_medical_report(data):
    if isinstance(data, str):
        data = json.loads(data)

    if not isinstance(data, dict):
        frappe.throw(_("Invalid Medical Report data"))

    doc = frappe.new_doc("Medical Report")
    doc.update(data)
    doc.insert(ignore_permissions=True)
    return doc.name