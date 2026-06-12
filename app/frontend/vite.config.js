import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";
import { copyFileSync } from "fs";
import { resolve } from "path";

// After each build, copy the single-file output to report/sankey.html so
// sources-of-truth.html (which iframes it) always reflects the React app.
const copySankeyPlugin = {
  name: "copy-sankey",
  closeBundle() {
    const src = resolve(__dirname, "../../report/sankey-dist/index.html");
    const dst = resolve(__dirname, "../../report/sankey.html");
    copyFileSync(src, dst);
    console.log("\n✓ report/sankey.html updated from build\n");
  },
};

export default defineConfig({
  base: "./",
  plugins: [react(), viteSingleFile(), copySankeyPlugin],
  build: {
    // Inline all assets (images, fonts) so the output is a single self-contained file
    assetsInlineLimit: 100_000_000,
    outDir: "../../report/sankey-dist",
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
