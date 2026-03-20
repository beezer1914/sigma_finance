/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep navy backgrounds
        sigma: {
          950: '#060b18',
          900: '#0c1222',
          850: '#111a2e',
          800: '#162033',
          700: '#1e2d4a',
          600: '#2a3f66',
          500: '#3a5a8c',
        },
        // Royal blue primary
        royal: {
          50: '#e8f0fe',
          100: '#c5d9fc',
          200: '#9cbcf9',
          300: '#729ef5',
          400: '#4f85f1',
          500: '#2d6bec',
          600: '#1d4ed8',
          700: '#1740b0',
          800: '#113388',
          900: '#0b2560',
        },
        // Warm gold accent
        gold: {
          50: '#fdf8e8',
          100: '#faefc5',
          200: '#f5df8e',
          300: '#eece57',
          400: '#e4bc2e',
          500: '#d4a017',
          600: '#b58612',
          700: '#8e690e',
          800: '#674c0a',
          900: '#403006',
        },
        // Surface colors for cards/panels
        surface: {
          DEFAULT: 'rgba(255, 255, 255, 0.04)',
          hover: 'rgba(255, 255, 255, 0.07)',
          border: 'rgba(255, 255, 255, 0.08)',
          'border-hover': 'rgba(255, 255, 255, 0.15)',
        },
      },
      fontFamily: {
        heading: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        body: ['"Red Hat Display"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Consolas', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.5s ease-out forwards',
        'slide-in-right': 'slideInRight 0.3s ease-out forwards',
        'glow-pulse': 'glowPulse 3s ease-in-out infinite',
        'progress-fill': 'progressFill 1s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(16px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(29, 78, 216, 0.15)' },
          '50%': { boxShadow: '0 0 30px rgba(29, 78, 216, 0.25)' },
        },
        progressFill: {
          '0%': { width: '0%' },
          '100%': { width: 'var(--progress-width)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glow-blue': '0 0 20px rgba(29, 78, 216, 0.2)',
        'glow-gold': '0 0 20px rgba(212, 160, 23, 0.2)',
        'card': '0 4px 24px rgba(0, 0, 0, 0.3)',
        'card-hover': '0 8px 32px rgba(0, 0, 0, 0.4)',
      },
    },
  },
  plugins: [],
}
