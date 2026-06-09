import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // Served from a project sub-path on GitHub Pages (https://<org>.github.io/valuechains-app/).
  // Override at build time with VITE_BASE=/ for root hosting or local preview.
  base: process.env.VITE_BASE || "/valuechains-app/",
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
