import {defineConfig} from 'vite';
import {resolve} from 'path';
import tailwindcss from "@tailwindcss/vite";
import sri from '@vividlemon/vite-plugin-sri';

export default defineConfig({
    base: "/static/",
    resolve: {
        alias: {
            "@": resolve('./static')
        }
    },
    build: {
        manifest: true,
        outDir: resolve("./assets"),
        rollupOptions: {
            input: resolve('./static/js/main.js')
        }
    },
    server: {
        host: '0.0.0.0',
        origin: 'http://localhost:5173',
        port: 5173,
        strictPort: true,
        cors: true,
        hmr: {
            protocol: 'ws',
            host: 'localhost',
        },
        watch: {
            usePolling: true,
        }
    },
    plugins: [
        sri(),
        tailwindcss(),
    ]
})
