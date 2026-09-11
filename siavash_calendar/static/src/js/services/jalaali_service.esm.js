/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

/**
 * Jalaali Service - Central service for Jalali calendar operations
 * 
 * This service provides:
 * - Bidirectional conversion between Jalali and Gregorian dates
 * - Validation of Jalali dates
 * - User preference checking
 * - Holiday detection
 */

export const jalaaliService = {
    dependencies: ["localization", "user"],
    
    async start(env, { localization, user }) {
        this.localization = localization;
        this.user = user;
        
        // Check if current user prefers Jalali calendar
        this.isJalaliEnabled = () => {
            return user.userId && localStorage.getItem(`jalaali_enabled_${user.userId}`) === 'true';
        };
        
        /**
         * Convert Gregorian date object to Jalali string
         * @param {Date} gregorianDate - JavaScript Date object
         * @returns {string|null} Jalali date string (YYYY-MM-DD) or null
         */
        this.toJalali = (gregorianDate) => {
            if (!gregorianDate || !(gregorianDate instanceof Date)) {
                return null;
            }
            
            const gy = gregorianDate.getFullYear();
            const gm = gregorianDate.getMonth() + 1;
            const gd = gregorianDate.getDate();
            
            if (typeof jalaali !== 'undefined') {
                const result = jalaali.toJalaali(gy, gm, gd);
                return jalaali.formatDate(result.jy, result.jm, result.jd);
            }
            
            // Fallback: simple approximation (should not happen if library loads)
            console.warn('Jalaali library not loaded');
            return `${gy}-${gm}-${gd}`;
        };
        
        /**
         * Convert Jalali string to Gregorian Date object
         * @param {string} jalaliStr - Jalali date string (YYYY-MM-DD or YYYY/MM/DD)
         * @returns {Date|null} JavaScript Date object or null if invalid
         */
        this.toGregorian = (jalaliStr) => {
            if (!jalaliStr || typeof jalaliStr !== 'string') {
                return null;
            }
            
            if (typeof jalaali !== 'undefined') {
                const result = jalaali.jalaliStringToGregorian(jalaliStr);
                if (result) {
                    return new Date(result.gy, result.gm - 1, result.gd);
                }
            }
            
            console.warn('Failed to convert Jalali date:', jalaliStr);
            return null;
        };
        
        /**
         * Validate a Jalali date string
         * @param {string} jalaliStr - Jalali date string
         * @returns {boolean} True if valid, false otherwise
         */
        this.isValid = (jalaliStr) => {
            if (!jalaliStr || typeof jalaliStr !== 'string') {
                return false;
            }
            
            if (typeof jalaali !== 'undefined') {
                const parsed = jalaali.parseDate(jalaliStr);
                return parsed !== null;
            }
            
            return false;
        };
        
        /**
         * Format a date for display based on user preferences
         * @param {Date} date - JavaScript Date object
         * @param {string} format - 'jalali' or 'gregorian'
         * @returns {string} Formatted date string
         */
        this.formatDate = (date, format = 'auto') => {
            if (!date || !(date instanceof Date)) {
                return '';
            }
            
            const useJalali = format === 'jalali' || (format === 'auto' && this.isJalaliEnabled());
            
            if (useJalali) {
                return this.toJalali(date);
            } else {
                return date.toISOString().split('T')[0];
            }
        };
        
        /**
         * Get Persian month name
         * @param {number} month - Month number (1-12)
         * @returns {string} Persian month name
         */
        this.getMonthName = (month) => {
            const months = [
                '', 'Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar',
                'Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand'
            ];
            return months[month] || '';
        };
        
        /**
         * Get Persian day name
         * @param {number} dayOfWeek - Day of week (0=Saturday, 6=Friday)
         * @returns {string} Persian day name
         */
        this.getDayName = (dayOfWeek) => {
            const days = ['Shanbeh', 'Yekshanbeh', 'Doshanbeh', 'Seshanbeh', 'Chaharshanbeh', 'Panjshanbeh', 'Jomeh'];
            return days[dayOfWeek] || '';
        };
        
        /**
         * Check if a date is a Persian holiday
         * @param {string} jalaliStr - Jalali date string
         * @returns {boolean} True if holiday
         */
        this.isHoliday = (jalaliStr) => {
            // TODO: Implement holiday checking from database
            const parsed = jalaali?.parseDate(jalaliStr);
            if (!parsed) return false;
            
            // Fixed holidays (simplified - should load from DB)
            const fixedHolidays = [
                '01-01', // Nowruz
                '01-02',
                '01-03',
                '01-04',
                '12-29', // Esfand 29 (if leap year)
            ];
            
            const mm = parsed.jm < 10 ? '0' + parsed.jm : parsed.jm;
            const dd = parsed.jd < 10 ? '0' + parsed.jd : parsed.jd;
            const key = `${mm}-${dd}`;
            
            return fixedHolidays.includes(key);
        };
        
        return this;
    },
};

registry.category("services").add("jalaali", jalaaliService);
