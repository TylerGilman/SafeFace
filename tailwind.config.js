/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/templates/*.html"],
  theme: {
    extend: {
      colors: {
        primary: {
          100: '#f0f4ff',
          200: '#d9e6ff',
          300: '#a6c1ff',
          400: '#598bff',
          500: '#3366ff',
          600: '#274bdb',
          700: '#1a34b8',
          800: '#102694',
          900: '#091c7a',
        },
        bg: {
          900: '#1a1a1a',
          800: '#2b2b2b',
          700: '#4d4d4d',
          600: '#666666',
          500: '#808080',
          400: '#999999',
          300: '#b3b3b3',
          200: '#cccccc',
          100: '#e6e6e6',
          50: '#f2f2f2',
        },
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],

}

