/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { jalaliUtils } from "../../js/date_utils";

export class JalaliDatePicker extends Component {
    setup() {
        super.setup();
        // Placeholder for future OWL picker implementation
        // For now, we rely on standard Odoo picker + server formatting
    }
}

JalaliDatePicker.template = "zarvan_calendar.JalaliDatePicker";
registry.category("components").add("JalaliDatePicker", JalaliDatePicker);
