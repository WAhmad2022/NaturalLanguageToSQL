import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/query": { target: "http://127.0.0.1:8081", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:8081", changeOrigin: true },
    },
  },
});
