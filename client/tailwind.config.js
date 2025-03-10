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
        // 如果需要默认的所有颜色，可以这样配置
        ...require('tailwindcss/colors'),
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
