
const { task, series, parallel, src, dest } = require('gulp');
var fontawesomeSubset = require('fontawesome-subset');
var replace = require('gulp-replace');
var del = require('del');

task('packages:handlebars', function() {
    return src('node_modules/handlebars/dist/handlebars.min.js').pipe(dest('atlas/static/vendor/handlebars/'));
});

task('packages:inter_font', function() {
  return src('node_modules/@fontsource/inter/**/*').pipe(replace(/\.\/files\//g, '/static/font/inter/files/')).pipe(dest('atlas/static/font/inter'))
});

task('packages:rasa_font', function() {
  return src('node_modules/@fontsource/rasa/**/*').pipe(replace(/\.\/files\//g, '/static/font/rasa/files/')).pipe(dest('atlas/static/font/rasa'))
});


// build fontawesome
/*
 * run from atlas root::
 *
 * node scripts/fontawesome.js
 */

task('packages:fontawesome', function(done) {
    del.sync('atlas/static/font/fontawesome/webfonts', {force:true});
    fontawesomeSubset({
      regular:['envelope', 'thumbs-up', 'play-circle'],
      solid: ['wrench',  'user', 'list-ul', 'chevron-left', 'chevron-right', 'search', 'edit', 'trash', 'star', 'share', 'plus', 'chart-bar', 'universal-access']
          }, 'atlas/static/font/fontawesome/webfonts')

    done();
});

task('packages', parallel('packages:fontawesome', 'packages:handlebars', 'packages:inter_font', 'packages:rasa_font'));

