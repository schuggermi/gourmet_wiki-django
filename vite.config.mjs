import { defineConfig } from 'vite';
import { resolve } from 'path';
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
    manifest: "manifest.json",
    outDir: resolve("./assets"),
    rollupOptions: {
      input: {
        main: resolve('./static/js/main.js'),
      }
    }
  },
  plugins: [
      tailwindcss(),
  ]
})