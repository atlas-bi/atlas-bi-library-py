const rename = require('gulp-rename');
const autoprefexer = require('gulp-autoprefixer');
const sass = require('gulp-sass')(require('sass'));
const postcss = require('gulp-postcss');
const purgecss = require('gulp-purgecss');
const cssnano = require('gulp-cssnano');
const postcssFocusWithin = require('focus-within/postcss');
const gulp = require('gulp');

gulp.task('css:email', function () {
  return gulp
    .src('atlas/static/scss/email_theme.scss')
    .pipe(sass.sync().on('error', sass.logError))
    .pipe(cssnano()) // Running this first to strip comments
    .pipe(
      purgecss({
        content: ['atlas/mail/templates/mail/email.html.dj'],
        safelist: [],
        fontFace: true,
        keyframes: true,
      }),
    )
    .pipe(autoprefexer())
    .pipe(rename('email.min.css'))
    .pipe(gulp.dest('atlas/static/css/'));
});

gulp.task('css:auth', function () {
  const plugins = [postcssFocusWithin];
  return gulp
    .src('atlas/static/scss/auth.scss')
    .pipe(sass.sync().on('error', sass.logError))
    .pipe(
      purgecss({
        content: ['atlas/templates/registration/**/*.html'],
        safelist: [],
      }),
    )
    .pipe(postcss(plugins))
    .pipe(autoprefexer())
    .pipe(cssnano())
    .pipe(rename('auth.min.css'))
    .pipe(gulp.dest('atlas/static/css/'));
});

gulp.task('css:build', function () {
  const plugins = [postcssFocusWithin];
  return gulp
    .src('atlas/static/scss/theme.scss')
    .pipe(sass.sync().on('error', sass.logError))
    .pipe(
      purgecss({
        content: [
          'atlas/**/*.html',
          'atlas/**/*.html.dj',
          'atlas/static/js/**/*.js',
          '!atlas/static/js/**/*build.js',
          '!atlas/static/js/**/*min.js',
          'atlas/static/lib/**/*.js',
        ],
        safelist: [
          'breadcrumb',
          'is-active',
          'editor-liveEditorPrev',
          'analytics-reviewed',
          'epic-released',
          'legacy',
          'high-risk',
          'self-service',
          'analytics-certified',
        ],
      }),
    )
    .pipe(postcss(plugins))
    .pipe(autoprefexer())
    .pipe(cssnano())
    .pipe(rename('site.min.css'))
    .pipe(gulp.dest('atlas/static/css/'));
});

gulp.task('css:rejected', function () {
  return gulp
    .src('atlas/static/scss/theme.scss')
    .pipe(sass.sync().on('error', sass.logError))
    .pipe(
      purgecss({
        content: [
          'atlas/**/*.html',
          'atlas/**/*.html.dj',
          'atlas/static/js/**/*.js',
          '!atlas/static/js/**/*build.js',
          '!atlas/static/js/**/*min.js',
          'atlas/static/lib/**/*.js',
        ],
        safelist: [
          'breadcrumb',
          'is-active',
          'editor-liveEditorPrev',
          'analytics-reviewed',
          'epic-released',
          'legacy',
          'high-risk',
          'self-service',
          'analytics-certified',
        ],
        rejected: true,
      }),
    )
    .pipe(rename('.rejected'))
    .pipe(gulp.dest('atlas/static/css/'));
});

gulp.task('styles', gulp.parallel('css:build', 'css:email', 'css:auth'));
