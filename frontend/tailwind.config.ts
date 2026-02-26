import type { Config } from 'tailwindcss'

export default {
  theme: {
    extend: {
      colors: {
        teal: {
          50:  '#E6F4F4',
          100: '#CCE9E9',
          200: '#99D3D3',
          300: '#66BDBD',
          400: '#33A7A7',
          500: '#109090',
          600: '#0C7C7C',
          700: '#0A6363',
          800: '#084F4F',
          900: '#063B3B',
          950: '#042929',
        },
        accent: {
          DEFAULT: '#C4841D',
          light: '#F5E6D0',
        },
      },
      fontFamily: {
        sans: ['DM Sans', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
      },
    },
  },
} satisfies Partial<Config>
