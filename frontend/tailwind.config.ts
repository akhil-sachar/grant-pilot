import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#18212f",
        muted: "#5c6677",
        line: "#d9e0e8",
        canvas: "#f6f8fb",
        panel: "#ffffff",
        spruce: "#087f5b",
        amber: "#b7791f",
        coral: "#c2410c",
        skyline: "#2563eb",
      },
      boxShadow: {
        soft: "0 8px 24px rgba(24, 33, 47, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;

