/** @type {import('tailwindcss').Config} */
module.exports = {
  // 1. CRITICAL: Content Configuration
  // This array tells Tailwind which files to scan for class names (e.g., 'text-indigo-700').
  // It MUST include all your React components (*.js, *.jsx) files.
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  
  // 2. Theme Configuration (Optional for MVP, but good practice)
  // You can extend or override Tailwind's default colors, spacing, etc., here.
  theme: {
    extend: {
      // Example: Adding a custom shade of indigo
      colors: {
        'indigo-800': '#3730a3',
      },
    },
  },
  
  // 3. Plugins (Highly recommended for text-heavy content)
  // The @tailwindcss/typography plugin provides the 'prose' class,
  // which is perfect for styling the LLM's Markdown output beautifully.
  plugins: [
    require('@tailwindcss/typography'),
  ],
}