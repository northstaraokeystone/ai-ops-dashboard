import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const API = env.VITE_API_BASE || "http://127.0.0.1:8000";

  return {
    plugins: [react()],
    resolve: {
      alias: { "@": path.resolve(__dirname, "./src") },
    },
    server: {
      port: 5173,
      proxy: {
        "/ask":   { target: API, changeOrigin: true },
        "/brief": { target: API, changeOrigin: true },
        "/health":{ target: API, changeOrigin: true },
      },
    },
    preview: {
      port: 5173,
      proxy: {
        "/ask":   { target: API, changeOrigin: true },
        "/brief": { target: API, changeOrigin: true },
        "/health":{ target: API, changeOrigin: true },
      },
    },
  };
});
