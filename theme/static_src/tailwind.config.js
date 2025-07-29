/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Templates in this project
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
    '../../**/templates/**/*.js',
    // Include JavaScript files that might contain Tailwind CSS classes
    '../../static/**/*.js',
    // Include all possible template locations for the apps
    '../../apps/**/templates/**/*.html',
    '../../business/templates/**/*.html',
  ],
  theme: {
    extend: {
      // Extended theme configurations
      fontFamily: {
        sans: ['Arial', 'sans-serif'],
      },
      colors: {
        'primary': {
          DEFAULT: '#3498db',
          '50': '#edf7fd',
          '100': '#d0e8f9',
          '200': '#a2d1f4',
          '300': '#74baee',
          '400': '#46a3e8',
          '500': '#3498db', // primary color
          '600': '#1a7ab9',
          '700': '#166297',
          '800': '#114a75',
          '900': '#0c3352',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('./content-type-plugin'), // Add our custom content-type plugin
  ],
}
