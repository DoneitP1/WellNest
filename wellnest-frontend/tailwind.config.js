/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#14b8a6",
                secondary: "#0f766e",
                dark: "#1e293b",
                light: "#f1f5f9",
            },
        },
    },
    plugins: [],
}
