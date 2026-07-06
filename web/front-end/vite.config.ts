import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      {
        find: "@",
        replacement: path.resolve(__dirname, "src"),
      },
      {
        find: "@components",
        replacement: path.resolve(__dirname, "src/components"),
      },
      {
        find: "@fonts",
        replacement: path.resolve(__dirname, "src/assets/fonts"),
      },
      {
        find: "@images",
        replacement: path.resolve(__dirname, "src/assets/images"),
      },
    ],
  },
});
