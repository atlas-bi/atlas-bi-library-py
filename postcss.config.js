// postcss.config.js
module.exports = cfg => {
  stats: {warnings:false}
  const
    dev = cfg.env === 'development',
    scss = cfg.file.extname === '.scss',
    purgecss = require('@fullhuman/postcss-purgecss');

  return {

    map: dev ? { inline: false } : false,
    parser:  scss ? 'postcss-scss' : false,

    plugins: [
      require('@csstools/postcss-sass')(),
      require('postcss-advanced-variables')(),
      require('postcss-import'),
      require('postcss-nested'),
      require('postcss-sort-media-queries')(),
      purgecss({
        content: ['./**/*.html.dj'],
        safelist: {
          deep: [/breadcrumb/],
        }
      }),
      require('autoprefixer')(),
      require('cssnano')()
    ]

  };
};
