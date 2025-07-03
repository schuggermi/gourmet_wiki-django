import {defineConfig} from 'vite';
import {resolve} from 'path';
import tailwindcss from "@tailwindcss/vite";
import lineClamp from "@tailwindcss/line-clamp";

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
        origin: 'http://localhost:5173',
        port: 5173,
        strictPort: true,
        cors: true,
        hmr: {
            protocol: 'ws',
            host: 'localhost',
        }
    },
    plugins: [
        tailwindcss(),
    ]
})
