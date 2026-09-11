/**
 * Jalaali (Persian) Calendar Utilities for OWL Components
 * High-performance conversion library
 */

export const jalaali = {
    /**
     * Convert Gregorian date to Jalaali
     * @param {number} gy - Gregorian year
     * @param {number} gm - Gregorian month (1-12)
     * @param {number} gd - Gregorian day (1-31)
     * @returns {{jy: number, jm: number, jd: number}}
     */
    toJalaali(gy, gm, gd) {
        const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        let jy = (gy <= 1600) ? 0 : 979;
        gy -= (gy <= 1600) ? 621 : 1600;
        
        let gy2 = (gm > 2) ? (gy + 1) : gy;
        let days = (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100) 
                   + Math.floor((gy2 + 399) / 400) - 80 + gd + g_d_m[gm - 1];
        
        jy += 33 * Math.floor(days / 12053);
        days %= 12053;
        jy += 4 * Math.floor(days / 1461);
        days %= 1461;
        
        if (days > 365) {
            jy += Math.floor((days - 1) / 365);
            days = (days - 1) % 365;
        }
        
        let jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
        let jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
        
        return { jy, jm, jd };
    },

    /**
     * Convert Jalaali date to Gregorian
     * @param {number} jy - Jalaali year
     * @param {number} jm - Jalaali month (1-12)
     * @param {number} jd - Jalaali day (1-31)
     * @returns {{gy: number, gm: number, gd: number}}
     */
    toGregorian(jy, jm, jd) {
        let gy = (jy <= 979) ? 621 : 1600;
        jy -= (jy <= 979) ? 0 : 979;
        
        let days = (365 * jy) + (Math.floor(jy / 33) * 8) + Math.floor(((jy % 33) + 3) / 4) 
                   + 78 + jd + ((jm < 7) ? (jm - 1) * 31 : ((jm - 7) * 30) + 186);
        
        gy += 400 * Math.floor(days / 146097);
        days %= 146097;
        
        if (days > 36524) {
            gy += 100 * Math.floor(--days / 36524);
            days %= 36524;
            if (days >= 365) days++;
        }
        
        gy += 4 * Math.floor(days / 1461);
        days %= 1461;
        
        if (days > 365) {
            gy += Math.floor((days - 1) / 365);
            days = (days - 1) % 365;
        }
        
        let gd = days + 1;
        const sal_a = [0, 31, ((gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        
        let gm;
        for (gm = 0; gm < 13 && gd > sal_a[gm]; gm++) {
            gd -= sal_a[gm];
        }
        
        return { gy, gm, gd };
    },

    /**
     * Check if a Jalaali year is a leap year
     * @param {number} jy - Jalaali year
     * @returns {boolean}
     */
    isLeapJalaali(jy) {
        const r = jy % 33;
        return r === 1 || r === 5 || r === 9 || r === 13 || r === 17 || r === 22 || r === 26 || r === 30;
    },

    /**
     * Format Jalaali date as string
     * @param {number} jy - Jalaali year
     * @param {number} jm - Jalaali month
     * @param {number} jd - Jalaali day
     * @param {string} format - Format pattern (default: 'YYYY-MM-DD')
     * @returns {string}
     */
    formatDate(jy, jm, jd, format = 'YYYY-MM-DD') {
        const pad = (n) => n.toString().padStart(2, '0');
        return format
            .replace('YYYY', jy.toString())
            .replace('MM', pad(jm))
            .replace('DD', pad(jd));
    },

    /**
     * Parse Jalaali date string
     * @param {string} dateStr - Date string in YYYY-MM-DD format
     * @returns {{jy: number, jm: number, jd: number}|null}
     */
    parseDate(dateStr) {
        const match = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (!match) return null;
        
        const [, jy, jm, jd] = match.map(Number);
        
        // Validate ranges
        if (jy < 1300 || jy > 1500) return null;
        if (jm < 1 || jm > 12) return null;
        if (jd < 1 || jd > 31) return null;
        
        // Validate day for month
        const maxDay = (jm <= 6) ? 31 : (jm <= 11) ? 30 : (this.isLeapJalaali(jy) ? 30 : 29);
        if (jd > maxDay) return null;
        
        return { jy, jm, jd };
    }
};

// Month names in Persian
export const jalaaliMonths = [
    'Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar',
    'Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand'
];

// Day names in Persian
export const jalaaliDays = [
    'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'
];
