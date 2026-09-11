/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { jalaliUtils } from "./date_utils";

// Patch Date Field to support Jalali Display (Read-only)
// The actual Picker is handled by the OWL component injection
patch(registry.category("fields").get("date").prototype, "zarvan_calendar.date_field", {
    get displayedValue() {
        const val = this.props.value;
        if (jalaliUtils.isUserJalaliEnabled() && val) {
            // Request formatted value from server via RPC if needed, 
            // or rely on server-side QWeb rendering for lists/forms
            // For simplicity in this safe version, we let the server handle formatting
            // and just ensure the field doesn't break.
            return val; 
        }
        return val;
    }
});
