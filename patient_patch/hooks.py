app_name = "patient_patch"
app_title = "Patient Patch"
app_publisher = "Dagaar"
app_description = "Patient Patch"
app_email = "info.dagaar@gmail.com"
app_license = "mit"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/patient_patch/css/patient_patch.css"
app_include_js = ["/assets/patient_patch/js/patient_quickentry_patch.js"]

# include js, css files in header of web template
# web_include_css = "/assets/patient_patch/css/patient_patch.css"
# web_include_js = "/assets/patient_patch/js/patient_patch.js"

# include js in doctype views
doctype_js = {
    "Patient Appointment": ["public/js/patient_appointment_ui.js", "public/js/visit_detail.js"],
    "Patient Encounter": "public/js/patient_encounter_ui.js"
}

doc_events = {
    "Patient Encounter": {
        "on_submit": "patient_patch.patient_patch.prescription_invoice.on_submit_patient_encounter",
        "on_update_after_submit": "patient_patch.patient_patch.prescription_invoice.on_update_after_submit_patient_encounter",
        "on_cancel": "patient_patch.patient_patch.prescription_invoice.on_cancel_patient_encounter",
    },
    "Sales Invoice": {
        "on_submit": "patient_patch.patient_patch.prescription_invoice.on_submit_sales_invoice",
    }
}

# Ensure our custom Print Format is installed with the app.  Frappe will
# import the document defined in the print_format directory at install time
# when fixtures are specified here.
fixtures = [
    {
        "doctype": "Print Format",
        "filters": [["name", "=", "Medical Report Print"]],
    }
]