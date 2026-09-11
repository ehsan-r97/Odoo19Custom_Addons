/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * JalaaliField Component - Reusable OWL component for Jalali date input
 * 
 * Features:
 * - Accepts both Jalali and Gregorian input (hybrid)
 * - Real-time validation
 * - Auto-conversion on blur
 * - ARIA accessibility support
 * 
 * Usage in XML:
 *   <JalaaliField value="record.my_date" onChange="this.onDateChange.bind(this)" />
 */

export class JalaaliField extends Component {
    setup() {
        this.jalaali = useService("jalaali");
        this.orm = useService("orm");
        
        this.state = {
            value: this.props.value || '',
            isInvalid: false,
            errorMessage: '',
            isEditing: false,
        };
        
        // Store original Gregorian value
        this.gregorianValue = null;
    }

    /**
     * Handle input change
     * Accepts formats: YYYY-MM-DD, YYYY/MM/DD (both Jalali and Gregorian detected automatically)
     */
    onInput(ev) {
        const inputValue = ev.target.value;
        this.state.value = inputValue;
        this.state.isInvalid = false;
        this.state.errorMessage = '';
        
        // Detect if input looks like Jalali (year > 1300)
        const yearMatch = inputValue.match(/^(\d{4})[-/]/);
        if (yearMatch && parseInt(yearMatch[1]) > 1300) {
            // Likely Jalali input
            if (this.jalaali.isValid(inputValue)) {
                const gregorianDate = this.jalaali.toGregorian(inputValue);
                if (gregorianDate) {
                    this.gregorianValue = gregorianDate.toISOString().split('T')[0];
                }
            } else {
                this.state.isInvalid = true;
                this.state.errorMessage = 'تاریخ شمسی نامعتبر است'; // Invalid Jalali date
            }
        } else {
            // Gregorian or incomplete input
            this.gregorianValue = inputValue;
        }
        
        if (this.props.onChange) {
            this.props.onChange(this.gregorianValue, inputValue);
        }
    }

    /**
     * Handle blur - finalize validation
     */
    onBlur(ev) {
        this.state.isEditing = false;
        
        if (!this.state.value) {
            return;
        }
        
        // Validate Jalali format if year suggests it
        const yearMatch = this.state.value.match(/^(\d{4})[-/]/);
        if (yearMatch && parseInt(yearMatch[1]) > 1300) {
            if (!this.jalaali.isValid(this.state.value)) {
                this.state.isInvalid = true;
                this.state.errorMessage = 'تاریخ وارد شده معتبر نیست. فرمت صحیح: 1403-01-15';
                
                if (this.props.onError) {
                    this.props.onError(this.state.errorMessage);
                }
            }
        }
    }

    /**
     * Handle focus - show raw value for editing
     */
    onFocus(ev) {
        this.state.isEditing = true;
        
        // If we have a Gregorian value and user prefers Jalali, show Jalali
        if (this.gregorianValue && this.jalaali.isJalaliEnabled()) {
            const gDate = new Date(this.gregorianValue);
            if (!isNaN(gDate.getTime())) {
                this.state.value = this.jalaali.toJalali(gDate);
            }
        }
    }

    /**
     * Get CSS classes based on state
     */
    get classes() {
        return {
            'jalaali-field': true,
            'is-invalid': this.state.isInvalid,
            'is-editing': this.state.isEditing,
        };
    }

    /**
     * Render placeholder text based on language
     */
    get placeholder() {
        return this.jalaali.isJalaliEnabled() 
            ? '۱۴۰۳-۰۱-۱۵' 
            : '2024-03-20';
    }
}

JalaaliField.template = "jalaali_pro.JalaaliField";
JalaaliField.props = {
    value: { type: String, optional: true },
    onChange: { type: Function, optional: true },
    onError: { type: Function, optional: true },
    readonly: { type: Boolean, optional: true },
    required: { type: Boolean, optional: true },
};

// Register component
registry.category("components").add("JalaaliField", JalaaliField);
