var gulp = require('gulp');

gulp.task(
  'build',
  gulp.parallel('packages', gulp.series('fonts', 'styles'), 'scripts'),
);
