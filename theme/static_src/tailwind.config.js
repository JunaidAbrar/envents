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
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
