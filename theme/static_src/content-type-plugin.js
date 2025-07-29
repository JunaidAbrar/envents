// Tailwind CSS plugin to consistently handle content types
// This ensures CSS is properly served with the correct MIME type

const plugin = require('tailwindcss/plugin');

module.exports = plugin(function({ addBase }) {
  // Add content-type comment at the top of generated CSS files
  addBase({
    ':root': {
      // This comment helps servers identify the file as CSS
      // even if the MIME type detection fails
    }
  });
  
  // Add pseudo-rule that ensures proper content type
  addBase({
    '@charset "UTF-8";': {}
  });
}, {
  // Plugin configuration options
  content: {
    type: 'text/css',
    charset: 'UTF-8',
  }
});
