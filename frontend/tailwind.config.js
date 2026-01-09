/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // 1. Base Color Palette (Primitives)
      colors: {
        // Base palette for the light theme
        neutral: {
          '50': '#FFFFFF',   // Primary Background
          '100': '#F8F9FA',  // Secondary Background
          '200': '#F1F3F5',  // Panel Background
          '300': '#E9ECEF',  // Elevated Surface
          '400': '#DEE2E6',  // Border Standard
          '500': '#ADB5BD',  // Border Emphasis
          '600': '#6C757D',  // Tertiary Text / Labels
          '700': '#495057',  // Secondary Text
          '900': '#212529',  // Primary Text
        },
        // Semantic Colors
        action: {
          'primary': '#0066CC',
          'primary-hover': '#0052A3',
        },
        signal: {
          'bullish': '#10B981',
          'bearish': '#EF4444',
          'neutral': '#3B82F6',
        },
        state: {
          'critical': '#DC2626',
          'warning': '#F59E0B',
          'success': '#059669',
          'info': '#0284C7',
        },
      },
      // 2. Typography System
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        financial: ['IBM Plex Mono', 'monospace'],
      },
      // 3. Z-Index Layering Strategy
      zIndex: {
        'layer-grid': '10',
        'layer-panel': '20',
        'layer-menu': '30',
        'layer-modal': '40',
        'layer-critical': '50',
      },
    },
  },
  plugins: [],
}
