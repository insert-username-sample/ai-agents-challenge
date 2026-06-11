/** @type {import('tailwindcss').Config} */
export default {
  content: ['./app/**/*.{tsx,ts,jsx,js}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        brand: {
          blue: '#2563EB',
          gold: '#C9A84C',
          green: '#16A34A',
          orange: '#EA580C',
        },
      },
    },
  },
  plugins: [],
}
