module.exports = {
  plugins: {
    // Process @import statements first
    "postcss-import": {},
    
    // Process Tailwind-specific nesting
    "tailwindcss/nesting": {},
    
    // Process Tailwind directives
    "tailwindcss": {},
    
    // Add vendor prefixes for browser compatibility
    "autoprefixer": {
      // Target browsers that need prefixing
      overrideBrowserslist: [
        '>0.3%',
        'last 2 versions',
        'not dead',
        'not op_mini all'
      ]
    },
    
    // Process CSS variables
    "postcss-simple-vars": {},
    
    // Process nested CSS selectors
    "postcss-nested": {},
    
    // Use in production only: minify CSS
    ...process.env.NODE_ENV === 'production' ? {
      "cssnano": {
        preset: ['default', {
          discardComments: {
            removeAll: false, // Keep content-type comments
          },
          // Other minification options
          normalizeWhitespace: true,
        }],
      }
    } : {}
  },
}
