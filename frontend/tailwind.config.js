/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // NBA Brand Colors
        nba: {
          primary: '#000000',
          secondary: '#FFFFFF',
          accent: '#C4122E',
          gold: '#FDB927',
        },
        // Dark mode
        dark: {
          bg: '#0f172a',
          surface: '#1e293b',
          hover: '#334155',
          border: '#475569',
          text: '#f1f5f9',
          muted: '#94a3b8',
        },
      },
      backgroundColor: {
        'court': '#0f172a',
        'surface': '#1e293b',
      },
      borderColor: {
        'court': '#475569',
      },
      textColor: {
        'court': '#f1f5f9',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
};
