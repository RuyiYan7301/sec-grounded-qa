import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// `npm run dev` proxies the API to `secqa web` on :7860
export default defineConfig(({ mode }) => ({
  base: mode === "static" ? "./" : "/",   // `npm run build:static`: relative paths, any host or sub-path
  plugins: [react(), tailwindcss()],
  server: { proxy: { "/api": "http://127.0.0.1:7860" } },
}));
