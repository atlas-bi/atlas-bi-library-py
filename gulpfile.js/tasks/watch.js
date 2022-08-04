const gulp = require('gulp');
require('./font');
require('./styles');
require('./scripts');
require('./build');
/*
Style changes > run styles
font changes > run font > styles
js changes > run js, styles
c# changes > run dotnet
html changes > run styles, dotnet
*/

gulp.task(
  'start',
  gulp.series(gulp.series('build'), function (cb) {
    gulp.watch(
      [
        'atlas/static/**/*.scss',
        'atlas/static/**/*.sass',
        'atlas/**/*.html',
        'atlas/**/*.html.dj',
      ],
      gulp.series('styles'),
    );

    // Utility
    gulp.watch(
      [
        'atlas/static/js/utility/tabs.js',
        'atlas/static/js/utility/collapse.js',
        'atlas/static/js/utility/carousel.js',
        'atlas/static/js/utility/table.js',
        'atlas/static/js/utility/drag.js',
        'atlas/static/js/utility/reorder.js',
        'atlas/static/js/utility/charts.js',
        'atlas/static/js/utility/modal.js',
        'atlas/static/js/utility/lazyload.js',
        'atlas/static/js/utility/crumbs.js',
        'atlas/static/js/page.js',
        'atlas/static/js/hyperspace.js',
        'atlas/static/js/favorites.js',
        'atlas/static/js/ajax-content.js',
        'atlas/static/js/notification.js',
        'atlas/static/js/mail.js',
        'atlas/static/js/utility/hamburger.js',
        'atlas/static/js/mini.js',
        'atlas/static/js/dropdown.js',
        'node_modules/chart.js/dist/chart.js',
      ],
      gulp.parallel('js:utility', 'styles'),
    );
    // Analytics
    gulp.watch(
      ['atlas/static/js/analytics.js'],
      gulp.parallel('js:analytics', 'styles'),
    );
    // Polyfill
    gulp.watch(
      [
        'atlas/static/js/polyfill/classlist.js',
        'atlas/static/js/polyfill/events.js',
        'atlas/static/js/polyfill/focus-within.js',
        'atlas/static/js/polyfill/foreach.js',
        'atlas/static/js/polyfill/insert-after.js',
        'atlas/static/js/polyfill/isinstance.js',
        'atlas/static/js/polyfill/matches_closest.js',
        'atlas/static/js/polyfill/sticky.js',
        'atlas/static/js/polyfill/remove.js',
        'atlas/static/js/polyfill/includes.js',
        'atlas/static/js/polyfill/trunc.js',
      ],
      gulp.parallel('js:polyfill', 'styles'),
    );

    // Tracker
    gulp.watch(
      ['atlas/static/js/tracker.js'],
      gulp.parallel('js:tracker', 'styles'),
    );

    // Highlighter
    gulp.watch(
      ['atlas/static/lib/highlight/highlight.js'],
      gulp.parallel('js:highlighter', 'styles'),
    );

    // Shared
    gulp.watch(
      ['atlas/static/js/shared.js'],
      gulp.parallel('js:shared', 'styles'),
    );

    // Search
    gulp.watch(
      ['atlas/static/js/search.js', 'atlas/static/js/error.js'],
      gulp.parallel('js:search', 'styles'),
    );

    // Profile
    gulp.watch(
      'atlas/static/js/profile.js',
      gulp.parallel('js:profile', 'styles'),
    );

    // User settings
    gulp.watch(
      'atlas/static/js/user-settings.js',
      gulp.parallel('js:userSettings', 'styles'),
    );

    // Settings
    gulp.watch(
      ['atlas/static/js/settings.js', 'atlas/static/js/access.js'],
      gulp.parallel('js:settings', 'styles'),
    );

    // Editor
    gulp.watch(
      [
        'atlas/static/js/editor.js',
        'atlas/static/js/utility/checkbox.js',
        'atlas/static/js/report-editor.js',
      ],
      gulp.parallel('js:editor', 'styles'),
    );

    gulp.watch(
      ['atlas/**/*.html', 'atlas/**/*.html.dj'],
      gulp.series('styles'),
    );
    gulp.watch(
      'atlas/static/font/fontawesome/**/*.scss',
      gulp.series('fonts', 'styles'),
    );
  }),
);

gulp.task(
  'watch',
  gulp.series('build', function (cb) {
    gulp.watch(
      ['atlas/static/**/*.scss', 'atlas/static/**/*.sass'],
      gulp.series('styles'),
    );
    gulp.watch(
      [
        'atlas/static/**/*.js',
        '!atlas/static/**/*.min.js',
        '!atlas/static/**/*.build.js',
      ],
      gulp.parallel('scripts', 'styles'),
    );
    gulp.watch(
      ['atlas/**/*.html', 'atlas/**/*.html.dj'],
      gulp.series('styles'),
    );
    gulp.watch(
      'atlas/static/font/fontawesome/**/*.scss',
      gulp.series('fonts', 'styles'),
    );
    cb();
  }),
);
