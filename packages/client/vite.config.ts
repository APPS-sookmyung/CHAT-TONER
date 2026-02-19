import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import tailwind from "@tailwindcss/vite";
import svgr from "vite-plugin-svgr";

export default defineConfig({
  // Monorepo note:
  // Some editors resolve `vite` types from the repo root while plugins resolve from `packages/client`,
  // which can cause TS2769 (Plugin type incompatibility) even though runtime is fine.
  // Casting here keeps the config usable while dependencies are deduped.
  plugins: [react(), tailwind(), svgr()] as any,
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
