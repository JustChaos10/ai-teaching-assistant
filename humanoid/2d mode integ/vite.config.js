import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@cubism': resolve(__dirname, 'src/vendor/Framework'),  // Points to ESM entry dir
    },
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
  },
  optimizeDeps: {
    include: ['@cubism/live2dcubismframework'],  // Pre-bundle Framework
    exclude: ['live2dcubismcore'],  // If Core loaded as global script
  },
  assetsInclude: ['**/*.wasm', '**/*.moc3', '**/*.model3.json', '**/*.motion3.json', '**/*.exp3.json', '**/*.physics3.json', '**/*.png'],  // Serves model assets raw
  define: {
    global: 'globalThis',  // Polyfill for Framework internals
  },
  server: {
    port: 5173,
    open: false,
  },
  build: {
    target: 'esnext',
    sourcemap: false,  // Disable sourcemaps to avoid warnings
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress sourcemap warnings for vendor files
        if (warning.code === 'SOURCEMAP_ERROR') return;
        warn(warning);
      }
    }
  },
})
