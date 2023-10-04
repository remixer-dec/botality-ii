module.exports = {
  darkMode: 'class', // or 'media'
  theme:
  {
    extend: {
      colors: {
        main: '#38b2ac'
      }
    }
  },
  variants: {},
  plugins: [],
  extract: {
    // accepts globs and file paths relative to project root
    include: [
      'src/**/*.{vue,html}',
      'node_modules/formvuelar/src/**/*.{vue,html}'
    ]
  }
}
