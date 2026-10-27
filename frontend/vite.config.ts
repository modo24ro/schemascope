import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    // Forward API calls to the FastAPI dev server (uvicorn on port 8000).
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
});
