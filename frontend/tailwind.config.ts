/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'hr-white': '#FFFFFF',
        'hr-black': '#0A0A0A',
        'hr-surface': '#F5F5F5',
        'hr-gold': '#C9A96E',
        'hr-border': '#E8E8E8',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
      },
      borderRadius: {
        'sm': '2px',
        DEFAULT: '4px',
        'md': '4px',
        'lg': '4px',
        'xl': '4px',
        '2xl': '4px',
        '3xl': '4px',
      },
      boxShadow: {
        'sm': 'none',
        DEFAULT: 'none',
        'md': 'none',
        'lg': 'none',
        'xl': 'none',
        '2xl': 'none',
        'inner': 'none',
      },
      transitionTimingFunction: {
        'DEFAULT': 'ease',
      },
      transitionDuration: {
        'DEFAULT': '200ms',
      }
    },
  },
  plugins: [],
}
