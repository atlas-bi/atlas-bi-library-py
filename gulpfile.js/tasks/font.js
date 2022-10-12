const gulp = require('gulp');
const replace = require('gulp-replace');
const { fontawesomeSubset } = require('fontawesome-subset');
const Font = require('fonteditor-core').Font;
const fs = require('fs');
const woff2 = require('fonteditor-core').woff2;

gulp.task('font:inter', () => {
  return gulp
    .src('node_modules/@fontsource/inter/**/*')
    .pipe(replace(/\.\/files\//g, '/font/inter/files/'))
    .pipe(gulp.dest('atlas/static/font/inter'));
});

gulp.task('font:rasa', () => {
  return gulp
    .src('node_modules/@fontsource/rasa/**/*')
    .pipe(replace(/\.\/files\//g, '/font/rasa/files/'))
    .pipe(gulp.dest('atlas/static/font/rasa'));
});

// write a rasa woff font to ttf for python pillow user icons
gulp.task('font:rasa_to_ttf', function (cb) {
  // woff2.init().then(() => {
  //  // read
  //  let buffer = fs.readFileSync(
  //    'node_modules/@fontsource/rasa/files/rasa-latin-600-normal.woff2',
  //  );
  // console.log(buffer);
  // let font = Font.create(buffer, {
  //   type: 'woff2',
  // });
  // // write
  // fs.writeFileSync(
  //   'atlas/static/font/rasa/files/rasa-latin-600-normal.ttf',
  //   font.write({ type: 'ttf' }),
  // );
  // });

  cb();
});

gulp.task('font:source', () => {
  return gulp
    .src('node_modules/@fontsource/source-code-pro/**/*')
    .pipe(replace(/\.\/files\//g, '/font/source-code-pro/files/'))
    .pipe(gulp.dest('atlas/static/font/source-code-pro'));
});

gulp.task('font:fontawesome', (done) => {
  fontawesomeSubset(
    {
      regular: [
        'envelope',
        'thumbs-up',
        'circle-play',
        'star',
        'paper-plane',
        'image',
        'copy',
      ],
      solid: [
        'envelope',
        'circle-plus',
        'circle-minus',
        'gears',
        'arrow-up-right-from-square',
        'code',
        'quote-left',
        'reply',
        'reply-all',
        'paper-plane',
        'heading',
        'xmark',
        'folder',
        'check',
        'play',
        'star',
        'folder-plus',
        'file-arrow-up',
        'floppy-disk',
        'angle-down',
        'sort',
        'folder-open',
        'link',
        'grip-lines',
        'sliders',
        'wrench',
        'italic',
        'user',
        'list-ol',
        'list-ul',
        'chevron-left',
        'chevron-right',
        'chevron-down',
        'chevron-up',
        'bold',
        'magnifying-glass',
        'pen-to-square',
        'trash',
        'star',
        'share',
        'plus',
        'chart-bar',
        'universal-access',
        'trash-can',
        'circle-notch',
        'left-long',
        'right-long',
        'eye',
        'eye-slash',
        'palette',
        'database',
        'message',
        'info',
        'paperclip',
        'user-lock',
        'lock',
        'image',
        'up-down-left-right',
        'circle',
        'book-open',
        'circle-check',
        'certificate',
        'filter',
        'users',
        'book',
        'lightbulb',
        'diagram-project',
        'caret-up',
        'caret-down',
        'caret-right',
        'caret-left',
        'toggle-on',
      ],
    },
    'atlas/static/font/fontawesome/webfonts',
  );
  done();
});

gulp.task(
  'fonts',
  gulp.parallel(
    'font:inter',
    gulp.series('font:rasa', 'font:rasa_to_ttf'),
    'font:fontawesome',
    'font:source',
  ),
);
