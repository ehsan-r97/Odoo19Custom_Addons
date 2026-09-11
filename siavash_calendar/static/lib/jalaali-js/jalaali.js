/**
 * Jalali (Shamsi) Calendar Conversion Library
 * Based on the algorithm by Kazem M. Nouri
 * 
 * This is a lightweight, dependency-free implementation for Odoo 19
 */

var jalaali = (function() {
    'use strict';

    /* Utility Functions */
    function div(a, b) {
        return ~~(a / b);
    }

    function mod(a, b) {
        return a - ~~(a / b) * b;
    }

    /* Constants */
    var JALAALI_EPOCH = 1948320.5; // Julian date of Farvardin 1, 1 AP
    var GREGORIAN_EPOCH = 1721425.5; // Julian date of January 1, 1 AD

    /* Convert Gregorian date to Julian Day Number */
    function gregorianToJdn(year, month, day) {
        var a = div((14 - month), 12);
        var y = year + 4800 - a;
        var m = month + 12 * a - 3;
        return day + div((153 * m + 2), 5) + 365 * y + div(y, 4) - div(y, 100) + div(y, 400) - 32045;
    }

    /* Convert Julian Day Number to Gregorian date */
    function jdnToGregorian(jdn) {
        var j = 4 * jdn + 139361631;
        j = j + div(div(4 * jdn + 183187720, 146097) * 3, 4) * 4 - 3908;
        var i = div(mod(j, 1461), 4) * 5 + 308;
        var day = div(mod(i, 153), 5) + 1;
        var month = mod(div(i, 153) + 2, 12) + 1;
        var year = div(j - 102, 1461) - 4715;
        return { gy: year, gm: month, gd: day };
    }

    /* Convert Jalali date to Julian Day Number */
    function jalaaliToJdn(year, month, day) {
        var r = div(year - (year >= 0 ? 474 : 473), 2820);
        var jdn = day + (month <= 7 ? (month - 1) * 31 : (month - 1) * 30 + 6) +
            div(((r * 2820) + (year % 2820) + 474) * 682 - 110, 2816) +
            div((r * 2820) + (year % 2820) + 475, 4) * 1461 - 1461 +
            (mod((r * 2820) + (year % 2820) + 474, 4) + 1) * 365 +
            1948320.5 - 1;
        return jdn;
    }

    /* Convert Julian Day Number to Jalali date */
    function jdnToJalaali(jdn) {
        var jy, jm, jd;
        var depoch = jdn - jalaaliToJdn(475, 1, 1);
        var cycle = div(depoch, 1029983);
        var cyear = mod(depoch, 1029983);
        
        if (cyear === 1029982) {
            var ycycle = 2820;
        } else {
            var aux1 = div(cyear + 1, 365);
            var aux2 = mod(cyear + 1, 365);
            var ycycle = div((aux1 * 2134) + (aux2 * 2816) + 2815, 1028522) + aux1 + 1;
        }
        
        jy = ycycle + (2820 * cycle) + 474;
        if (jy <= 0) {
            jy -= 1;
        }
        
        var yday = (jdn - jalaaliToJdn(jy, 1, 1)) + 1;
        jm = (yday <= 186) ? Math.ceil(yday / 31) : Math.ceil((yday - 6) / 30);
        jd = (jdn - jalaaliToJdn(jy, jm, 1)) + 1;
        
        return { jy: jy, jm: jm, jd: jd };
    }

    /* Check if a Jalali year is a leap year */
    function isLeapJalaaliYear(jy) {
        return mod(((jy + 12) * 682) % 2816, 4) === 0;
    }

    /* Validate a Jalali date */
    function isValidJalaaliDate(year, month, day) {
        if (year < 1300 || year > 1500) return false;
        if (month < 1 || month > 12) return false;
        if (day < 1 || day > 31) return false;
        
        // Check days in month
        if (month <= 6 && day > 31) return false;
        if (month > 6 && day > 30) return false;
        if (month === 12 && day > 29 && !isLeapJalaaliYear(year)) return false;
        
        return true;
    }

    /* Format Jalali date as string */
    function formatDate(year, month, day, separator = '-') {
        var mm = month < 10 ? '0' + month : month;
        var dd = day < 10 ? '0' + day : day;
        return year + separator + mm + separator + dd;
    }

    /* Parse Jalali date string */
    function parseDate(dateStr) {
        if (!dateStr) return null;
        var normalized = dateStr.replace(/\//g, '-');
        var parts = normalized.split('-');
        if (parts.length !== 3) return null;
        
        var year = parseInt(parts[0], 10);
        var month = parseInt(parts[1], 10);
        var day = parseInt(parts[2], 10);
        
        if (isNaN(year) || isNaN(month) || isNaN(day)) return null;
        if (!isValidJalaaliDate(year, month, day)) return null;
        
        return { jy: year, jm: month, jd: day };
    }

    /* Public API */
    return {
        toJalaali: function(gy, gm, gd) {
            var jdn = gregorianToJdn(gy, gm, gd);
            return jdnToJalaali(jdn);
        },
        
        toGregorian: function(jy, jm, jd) {
            var jdn = jalaaliToJdn(jy, jm, jd);
            return jdnToGregorian(jdn);
        },
        
        isValidDate: isValidJalaaliDate,
        isLeapYear: isLeapJalaaliYear,
        formatDate: formatDate,
        parseDate: parseDate,
        
        // Convenience methods for string conversion
        jalaliStringToGregorian: function(jalaliStr) {
            var parsed = parseDate(jalaliStr);
            if (!parsed) return null;
            return this.toGregorian(parsed.jy, parsed.jm, parsed.jd);
        },
        
        gregorianStringToJalali: function(gregorianStr) {
            var parts = gregorianStr.split('-');
            if (parts.length !== 3) return null;
            var gy = parseInt(parts[0], 10);
            var gm = parseInt(parts[1], 10);
            var gd = parseInt(parts[2], 10);
            var result = this.toJalaali(gy, gm, gd);
            return this.formatDate(result.jy, result.jm, result.jd);
        }
    };
})();

// Export for Node.js/CommonJS (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = jalaali;
}
