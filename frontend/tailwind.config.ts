import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./contexts/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#07070d",
        surface: "#0f0f18",
        panel: "#141422",
        card: "#1a1a2e",
        line: "rgba(255,255,255,0.08)",
        accent: "#7c5cff",
        accent2: "#22d3ee",
        muted: "#8b8ca8",
        foreground: "#f4f4ff",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(124, 92, 255, 0.15)",
        card: "0 4px 24px rgba(0,0,0,0.4)",
      },
    },
  },
  plugins: [],
};
export default config;
