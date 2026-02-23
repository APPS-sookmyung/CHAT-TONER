import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import tailwind from "@tailwindcss/vite";
import svgr from "vite-plugin-svgr";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  const proxyTarget =
    env.VITE_PROXY_TARGET ||
    process.env.VITE_PROXY_TARGET ||
    "http://127.0.0.1:8000";

  console.log(`[vite] mode=${mode} proxyTarget=${proxyTarget}`);

  return {
    plugins: [react(), tailwind(), svgr()],
    server: {
      proxy: {
        "/api": {
          // Dev: point to local FastAPI so LLM-only logic is used
          target: proxyTarget,
          changeOrigin: true,
          rewrite: (path) => path,
          configure: (proxy, _options) => {
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log(`[vite] Proxying: ${req.method} ${req.url} -> ${proxyTarget}`);
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
  };
});
