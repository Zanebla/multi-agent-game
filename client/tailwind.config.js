/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      transitionProperty: {
        scale: 'transform',
      },
      colors: {
        ...require('tailwindcss/colors'),
        gold: '#FFD700',
        pink: '#FFC0CB',
        main: '#052f9c',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
