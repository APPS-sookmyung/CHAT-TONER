import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import tailwind from "@tailwindcss/vite";
import svgr from "vite-plugin-svgr";

export default defineConfig({
  plugins: [react(), tailwind(), svgr()],
  server: {
    proxy: {
      "/api": {
        // Dev: point to local FastAPI so LLM-only logic is used
        target: process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8080",
        changeOrigin: true,
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Proxying:', req.method, req.url, '->', process.env.VITE_PROXY_TARGET || 'http://127.0.0.1:5000');
          });
        },
      },
    },
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
});
