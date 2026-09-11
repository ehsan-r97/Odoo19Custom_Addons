/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { jalaliUtils } from "./date_utils";

// Patch Filter Logic to handle Persian NLP inputs safely
// When user types "شنبه آینده" in filter, we send it to server for parsing
patch(Object.getPrototypeOf(window.odoo?.web?.SearchView || {}), "zarvan_calendar.filter_patch", {
    // This is a conceptual patch. Actual implementation relies on Odoo 19 specific Filter API
    // The heavy lifting of NLP is done server-side in the mixin _parse_persian_nlp
});
