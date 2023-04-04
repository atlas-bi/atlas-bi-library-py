const concat = require('gulp-concat');
const uglify = require('gulp-uglify');
const gulp = require('gulp');
const rollup = require('rollup-stream-gulp');
const { nodeResolve } = require('@rollup/plugin-node-resolve');
const commonjs = require('@rollup/plugin-commonjs');
const { babel } = require('@rollup/plugin-babel');
const json = require('@rollup/plugin-json');
var addsrc = require('gulp-add-src');
const swc = require('gulp-swc');

const swcOptions = {
  minify: true,
  module: {
    type: 'commonjs',
  },

  jsc: {
    target: 'es5',
    loose: true,
    minify: {
      mangle: true,
      compress: true,
    },
    parser: {
      dynamicImport: true,
    },
  },
};

const rollupConfig = {
  output: { format: 'iife', name: 'module' },
  plugins: [
    nodeResolve({ browser: true, preferBuiltins: false }),
    commonjs({ sourceMap: false }),
    // babel({
    //   babelHelpers: 'bundled',
    // }),
    swc(swcOptions),
    json(),
  ],
};

const swcOptionsNoModule = {
  minify: true,
  isModule: false,
  jsc: {
    target: 'es5',
    minify: {
      mangle: true,
      compress: true,
    },
  },
};

const uglifyConfig = {
  ie: true,
  v8: true,
  webkit: true,
};
gulp.task('js:polyfill', function () {
  return (
    gulp
      .src([
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
      ])
      .pipe(concat('polyfill.min.js'))
      // .pipe(uglify(uglifyConfig))
      .pipe(swc(swcOptionsNoModule))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task('js:utility', function () {
  return (
    gulp
      .src([
        'atlas/static/js/utility/tabs.js',
        'atlas/static/js/utility/collapse.js',
        'atlas/static/js/utility/carousel.js',
        'atlas/static/js/utility/table.js',
        'atlas/static/js/utility/drag.js',
        'atlas/static/js/utility/reorder.js',
        'atlas/static/js/utility/modal.js',
        'atlas/static/js/utility/lazyload.js',
        'atlas/static/js/utility/crumbs.js',
        'atlas/static/js/hyperspace.js',
        'atlas/static/js/favorites.js',
        'atlas/static/js/ajax-content.js',
        'atlas/static/js/notification.js',
        'atlas/static/js/mail.js',
        'atlas/static/js/utility/hamburger.js',
        'atlas/static/js/mini.js',
        'atlas/static/js/dropdown.js',
        'node_modules/chart.js/dist/Chart.js',
      ])
      // .pipe(rollup(rollupConfig))
      .pipe(concat('utility.min.js'))
      // .pipe(uglify(uglifyConfig))
      .pipe(swc(swcOptions))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task('js:analytics', function () {
  return (
    gulp
      .src(['atlas/static/js/analytics.js'])
      .pipe(rollup(rollupConfig))
      .pipe(concat('analytics.min.js'))
      // .pipe(uglify(uglifyConfig))
      // .pipe(swc(swcOptions))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task('js:profile', function () {
  return (
    gulp
      .src(['atlas/static/js/profile.js'])
      .pipe(rollup(rollupConfig))
      .pipe(concat('profile.min.js'))
      // .pipe(swc(swcOptions))
      // .pipe(uglify(uglifyConfig))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task('js:userSettings', function () {
  return (
    gulp
      .src(['atlas/static/js/user-settings.js'])
      // .pipe(rollup(rollupConfig))
      .pipe(concat('user-settings.min.js'))
      // .pipe(uglify(uglifyConfig))
      .pipe(swc(swcOptions))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task('js:tracker', function () {
  return gulp
    .src(['atlas/static/js/tracker.js'])
    .pipe(rollup(rollupConfig))
    .pipe(addsrc('node_modules/jsnlog/jsnlog.js'))
    .pipe(concat('alive.min.js'))
    .pipe(gulp.dest('atlas/static/js/'));
});

gulp.task('js:highlighter', () => {
  return (
    gulp
      .src('atlas/static/lib/highlight/highlight.js')
      // .pipe(rollup(rollupConfig))
      .pipe(concat('highlight.min.js'))
      // .pipe(uglify(uglifyConfig))
      .pipe(swc(swcOptions))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task('js:shared', function () {
  // Shared functions should be imported as needed.
  return (
    gulp
      .src(['atlas/static/js/shared.js'])
      .pipe(concat('shared.min.js'))
      // .pipe(uglify(uglifyConfig))
      .pipe(swc(swcOptionsNoModule))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task('js:search', function () {
  return (
    gulp
      .src(['atlas/static/js/search.js', 'atlas/static/js/error.js'])
      // .pipe(rollup(rollupConfig))
      .pipe(concat('search.min.js'))
      // .pipe(uglify(uglifyConfig))
      .pipe(swc(swcOptions))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task('js:settings', function () {
  return (
    gulp
      .src(['atlas/static/js/settings.js', 'atlas/static/js/access.js'])
      // .pipe(rollup(rollupConfig))
      .pipe(concat('settings.min.js'))
      // .pipe(uglify(uglifyConfig))
      .pipe(swc(swcOptions))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task('js:editor', function () {
  return (
    gulp
      .src([
        'atlas/static/js/editor.js',
        'atlas/static/js/utility/checkbox.js',
        'atlas/static/js/report-editor.js',
      ])
      .pipe(rollup(rollupConfig))
      .pipe(concat('editor.min.js'))
      // .pipe(uglify(uglifyConfig))
      // .pipe(swc(swcOptions))
      .pipe(gulp.dest('atlas/static/js/'))
  );
});

gulp.task(
  'scripts',
  gulp.parallel(
    'js:editor',
    'js:polyfill',
    'js:settings',
    'js:search',
    'js:shared',
    'js:utility',
    'js:analytics',
    'js:tracker',
    'js:highlighter',
    'js:profile',
    'js:userSettings',
  ),
);
