/*
 * run from atlas root::
 *
 * node scripts/fontawesome.js
 */

const fontawesomeSubset = require('fontawesome-subset');

fontawesomeSubset({
    regular:['envelope'],
    solid: ['wrench',  'user', 'list-ul', 'chevron-left', 'chevron-right', 'search']
        }, 'atlas/static/font/fontawesome/webfonts');
