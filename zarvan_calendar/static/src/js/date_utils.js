/** @odoo-module **/
import { registry } from "@web/core/registry";

export const jalaliUtils = {
    // Simple, safe conversion utilities for client-side fallback
    // In production, we rely on server-side conversion via RPC for accuracy.
    // This file is primarily for UI formatting if needed.
    
    isUserJalaliEnabled() {
        // Check user context (populated by server)
        return odoo.user_context.enable_jalali_display || false;
    },
    
    formatDateString(dateStr) {
        if (!dateStr || !this.isUserJalaliEnabled()) {
            return dateStr;
        }
        // Fallback: Just mark it for server to format properly via QWeb/RPC
        // Actual conversion happens on server to ensure 100% accuracy with jdatetime
        return dateStr; 
    }
};

registry.category("utils").add("jalali_utils", jalaliUtils);
