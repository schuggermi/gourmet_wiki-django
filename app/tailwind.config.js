// tailwind.config.js
module.exports = {
    content: [
        './templates/**/*.html',
        './static/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/typography'),
        require('@tailwindcss/line-clamp'),
    ],
};
