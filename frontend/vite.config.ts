import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "VITE_");

  return {
    base: env.VITE_BASE_PATH || "/",
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: "http://localhost:8000",
          changeOrigin: true
        },
        "/health": {
          target: "http://localhost:8000",
          changeOrigin: true
        }
      }
    }
  };
});
