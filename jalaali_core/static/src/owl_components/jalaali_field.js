/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { jalaali } from "../lib/jalaali.js";

export class JalaaliField extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.jalaliValue = this.props.value ? this._toJalali(this.props.value) : '';
    }

    _toJalali(gregorianDate) {
        if (!gregorianDate) return '';
        
        const [year, month, day] = gregorianDate.split('-').map(Number);
        const { jy, jm, jd } = jalaali.toJalaali(year, month, day);
        return jalaali.formatDate(jy, jm, jd);
    }

    _toGregorian(jalaliDate) {
        if (!jalaliDate) return '';
        
        const parsed = jalaali.parseDate(jalaliDate);
        if (!parsed) {
            this.notification.add("Invalid Jalali date format", { type: "danger" });
            return null;
        }
        
        const { gy, gm, gd } = jalaali.toGregorian(parsed.jy, parsed.jm, parsed.jd);
        return jalaali.formatDate(gy, gm, gd);
    }

    async onChange(ev) {
        const jalaliDate = ev.target.value;
        const gregorianDate = this._toGregorian(jalaliDate);
        
        if (gregorianDate) {
            this.props.update(gregorianDate);
        }
    }

    renderJalaliInput() {
        return `
            <input 
                type="text" 
                class="form-control" 
                value="${this.jalaliValue}" 
                onchange="(ev) => this.onChange(ev)"
                placeholder="YYYY-MM-DD (Jalali)"
            />
        `;
    }
}

JalaaliField.template = "jalaali_core.JalaaliField";
JalaaliField.props = ['value', 'update'];
