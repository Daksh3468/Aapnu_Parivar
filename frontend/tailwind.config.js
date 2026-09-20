/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        gov: {
          navy: '#0f2942',     // Primary Government Navy
          blue: '#1e40af',     // Official Action Blue
          hover: '#1d4ed8',
          light: '#f0f4f8',    // Light section canvas
          border: '#cbd5e1',
          text: '#1e293b',
          muted: '#64748b',
        },
        saffron: {
          DEFAULT: '#d97706',
          dark: '#b45309',
          light: '#fef3c7',
        },
        flagGreen: {
          DEFAULT: '#15803d',
          light: '#dcfce7',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'gov': '0 1px 3px 0 rgba(0, 0, 0, 0.08), 0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        'gov-md': '0 4px 6px -1px rgba(15, 41, 66, 0.08), 0 2px 4px -1px rgba(15, 41, 66, 0.04)',
      }
    },
  },
  plugins: [],
}
