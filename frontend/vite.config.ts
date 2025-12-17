import react from '@vitejs/plugin-react'
import path from 'path'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const devPort = Number(env.VITE_DEV_PORT || '5173')

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        branding: path.resolve(__dirname, './branding'),
      },
    },
    server: {
      host: true, // listen on 0.0.0.0 for external access
      port: devPort,
    },
    build: {
      rollupOptions: {
        output: {
          assetFileNames: (assetInfo) => {
            const ext = path.extname(assetInfo.name ?? '').toLowerCase();
            if (['.woff', '.woff2', '.ttf', '.otf', '.eot'].includes(ext)) {
              return 'fonts/[name]-[hash][extname]';
            }
            return 'assets/[name]-[hash][extname]';
          },
        },
      },
    },
  }
})
