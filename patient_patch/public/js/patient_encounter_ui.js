frappe.ui.form.on('Patient Encounter', {
    onload(frm) {
        style_sections();
    },
    refresh(frm) {
        style_sections();
        add_floating_save_submit_button(frm);
        add_create_medical_report_button(frm);
    }
});

function style_sections() {
    setTimeout(() => {
        $('.section-head').each(function () {
            const sectionText = $(this).text().trim().toLowerCase();
            let bgColor = "#f5f5f5";

            if (sectionText.includes("encounter")) bgColor = "#e6f7ff";
            else if (sectionText.includes("medical")) bgColor = "#f0f0f0";
			else if (sectionText.includes("heading")) bgColor = "#d1f7c4";
			else if (sectionText.includes("history")) bgColor = "#B2D8D8";
            else if (sectionText.includes("medication")) bgColor = "#fde2e2";
            else if (sectionText.includes("investigations")) bgColor = "#e2f0cb";
            else if (sectionText.includes("procedure")) bgColor = "#e8daef";
            else if (sectionText.includes("rehabilitation")) bgColor = "#d1f2eb";
            else if (sectionText.includes("ref")) bgColor = "#f8c471";
            else if (sectionText.includes("note")) bgColor = "#f6ddcc";
			else if (sectionText.includes("lab")) bgColor = "#DCEEF2";
            else if (sectionText.includes("maging")) bgColor = "#E9EEF5";

            $(this).css({
                "background-color": bgColor,
                "padding": "8px 12px",
                "border-radius": "4px",
                "font-weight": "bold",
                "margin-top": "12px"
            });
        });
    }, 300);
}

function add_floating_save_submit_button(frm) {
    setTimeout(() => {
        if (frm.doc.docstatus !== 0 || $('#floating-submit-btn').length) return;

        const btn = $(`
            <button id="floating-submit-btn" class="btn btn-success btn-md">
                Save and Submit
            </button>
        `).css({
            position: "fixed",
            bottom: "20px",
            right: "30px",
            "z-index": 9999,
            "box-shadow": "0 4px 8px rgba(0,0,0,0.2)"
        });

        btn.on("click", () => {
            frm.save().then(() => {
                if (frm.doc.docstatus === 0) frm.savesubmit();
            });
        });

        $('body').append(btn);
    }, 500);
}

/**
 * Add a "Create Medical Report" button under the Create menu on the Patient Encounter
 * form.  When clicked, a dialog will open allowing the user to review and edit
 * the Medical Report fields.  Upon submission the report will be saved and
 * the user will be taken to its print view.
 *
 * This button only appears on saved Patient Encounter documents that are not
 * cancelled.
 */
function add_create_medical_report_button(frm) {
    // Only show for existing encounters
    if (!frm.doc || frm.is_new() || frm.doc.docstatus === 2) {
        return;
    }
    // Avoid adding multiple buttons
    if (frm.custom_create_medical_report_added) {
        return;
    }
    frm.add_custom_button(__('Medical Report'), function () {
        show_medical_report_dialog(frm);
    }, __('Create'));
    frm.custom_create_medical_report_added = true;
}

/**
 * Fetch default values from the server and display a dialog for creating
 * a Medical Report.  Fields are pre-filled with information from the
 * Patient Encounter and can be edited before saving.
 *
 * @param {Object} frm - The current Patient Encounter form
 */
function show_medical_report_dialog(frm) {
    frappe.call({
        method: 'patient_patch.patient_patch.api.medical_report.get_medical_report_defaults',
        args: { encounter_name: frm.doc.name },
        callback: function (r) {
            if (r.message) {
                const defaults = r.message;
                const dialog = new frappe.ui.Dialog({
                    title: __('Create Medical Report'),
                    fields: [
                        { label: __('Reference No'), fieldname: 'ref_no', fieldtype: 'Data', reqd: 1, default: defaults.ref_no || '' },
                        { label: __('Patient'), fieldname: 'patient', fieldtype: 'Link', options: 'Patient', reqd: 1, read_only: 1, default: defaults.patient },
                        { label: __('Patient Name'), fieldname: 'patient_name', fieldtype: 'Data', read_only: 1, default: defaults.patient_name },
                        { label: __('Patient ID'), fieldname: 'patient_id', fieldtype: 'Data', read_only: 1, default: defaults.patient_id },
                        { label: __('Age'), fieldname: 'age', fieldtype: 'Int', read_only: 1, default: defaults.age },
                        { label: __('Sex'), fieldname: 'sex', fieldtype: 'Data', read_only: 1, default: defaults.sex },
                        { label: __('Report Date'), fieldname: 'report_date', fieldtype: 'Date', reqd: 1, default: defaults.report_date },
                        { label: __('Due Date'), fieldname: 'due_date', fieldtype: 'Date', default: defaults.due_date },
                        { label: __('Diagnosis'), fieldname: 'diagnosis', fieldtype: 'Small Text', default: defaults.diagnosis },
                        { label: __('Treatment'), fieldname: 'treatment', fieldtype: 'Small Text', default: defaults.treatment },
                        { label: __('Recommendations'), fieldname: 'recommendation', fieldtype: 'Small Text', default: defaults.recommendation },
                        { label: __('Doctor'), fieldname: 'doctor', fieldtype: 'Link', options: 'Healthcare Practitioner', default: defaults.doctor }
                    ],
                    primary_action_label: __('Save & Print'),
                    primary_action(values) {
                        dialog.get_primary_btn().prop('disabled', true);
                        frappe.call({
                            method: 'patient_patch.patient_patch.api.medical_report.create_medical_report',
                            args: { data: values },
                            callback: function (res) {
                                dialog.get_primary_btn().prop('disabled', false);
                                if (!res.exc) {
                                    const name = res.message;
                                    dialog.hide();
                                    // Navigate to the print view of the new Medical Report
                                    frappe.set_route('print', 'Medical Report', name);
                                }
                            }
                        });
                    }
                });
                dialog.show();
            }
        }
    });
}

// Global route change watcher to remove button always
frappe.router.on('change', () => {
    $('#floating-submit-btn').remove();
});
