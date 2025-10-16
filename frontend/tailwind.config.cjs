/** @type {import('tailwindcss').Config} */

const brandPalette = {
  gray: {
    50:  '#FAFAFA', 950: '#111111',
  },
  // Add other palette colors here if needed for the test
};

module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-bg-primary':    brandPalette.gray[950],
        'brand-text-primary':  brandPalette.gray[50],
      },
    },
  },
  plugins: [],
}
