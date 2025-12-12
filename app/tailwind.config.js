// tailwind.config.js
module.exports = {
    content: [
        './templates/**/*.html',
        './static/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
        extend: {
            fontFamily: {
                // Montserrat for headings
                sans: [
                    'Montserrat',
                    'ui-sans-serif',
                    'system-ui',
                    'Segoe UI',
                    'Roboto',
                    'Helvetica Neue',
                    'Arial',
                    'Noto Sans',
                    'sans-serif',
                    'Apple Color Emoji',
                    'Segoe UI Emoji',
                ],
                // Merriweather for body text
                serif: [
                    'Merriweather',
                    'ui-serif',
                    'Georgia',
                    'Cambria',
                    "Times New Roman",
                    'Times',
                    'serif',
                ],
            },
            // Semantic font sizes to control typography centrally
            fontSize: {
                // Body text
                'body': ['1rem', { lineHeight: '1.6', letterSpacing: '0' }], // 16px
                'body-lg': ['1.125rem', { lineHeight: '1.65', letterSpacing: '0' }], // 18px
                'small': ['0.875rem', { lineHeight: '1.45' }], // 14px
                'muted': ['0.875rem', { lineHeight: '1.45' }],

                // Headings — base, md, lg responsive steps
                'h1': ['2rem', { lineHeight: '1.2', fontWeight: '800' }], // 32px
                'h1-md': ['2.5rem', { lineHeight: '1.15', fontWeight: '800' }], // 40px
                'h1-lg': ['3rem', { lineHeight: '1.1', fontWeight: '800' }], // 48px

                'h2': ['1.75rem', { lineHeight: '1.25', fontWeight: '700' }], // 28px
                'h2-md': ['2.125rem', { lineHeight: '1.2', fontWeight: '700' }], // 34px
                'h2-lg': ['2.5rem', { lineHeight: '1.15', fontWeight: '700' }], // 40px

                'h3': ['1.5rem', { lineHeight: '1.3', fontWeight: '700' }], // 24px
                'h3-md': ['1.75rem', { lineHeight: '1.25', fontWeight: '700' }], // 28px
                'h3-lg': ['2rem', { lineHeight: '1.2', fontWeight: '700' }], // 32px

                'h4': ['1.25rem', { lineHeight: '1.35', fontWeight: '600' }], // 20px
                'h4-md': ['1.5rem', { lineHeight: '1.3', fontWeight: '600' }], // 24px
                'h4-lg': ['1.75rem', { lineHeight: '1.25', fontWeight: '600' }], // 28px

                'h5': ['1rem', { lineHeight: '1.4', fontWeight: '600' }], // 16px
                'h5-md': ['1.125rem', { lineHeight: '1.4', fontWeight: '600' }], // 18px
                'h5-lg': ['1.25rem', { lineHeight: '1.35', fontWeight: '600' }], // 20px
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
        require('@tailwindcss/line-clamp'),
    ],
};
