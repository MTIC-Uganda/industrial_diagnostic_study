import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";
import { copyFileSync } from "fs";
import { resolve } from "path";

// After each build, copy the single-file output to report/explorer.html so
// sources-of-truth.html (which iframes it) always reflects the React app.
const copyExplorerPlugin = {
  name: "copy-explorer",
  closeBundle() {
    const src = resolve(__dirname, "../../report/explorer-dist/index.html");
    const dst = resolve(__dirname, "../../report/explorer.html");
    copyFileSync(src, dst);
    console.log("\n✓ report/explorer.html updated from build\n");
  },
};

export default defineConfig({
  base: "./",
  plugins: [react(), viteSingleFile(), copyExplorerPlugin],
  build: {
    // Inline all assets (images, fonts) so the output is a single self-contained file
    assetsInlineLimit: 100_000_000,
    outDir: "../../report/explorer-dist",
    emptyOutDir: true,
  },
  server: {
    port: 3001,
  },
});
