import path from 'node:path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue2'
import WindiCSS from 'vite-plugin-windicss'
import Components from 'unplugin-vue-components/vite'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import AutoImport from 'unplugin-auto-import/vite'
import TopLevelAwait from 'vite-plugin-top-level-await'

const config = defineConfig({
  resolve: {
    alias: {
      '@': `${path.resolve(__dirname, 'src')}`,
      '%': `${path.resolve(__dirname, 'node_modules')}`
    }
  },

  build: {
    minify: true,
    emptyOutDir: true,
    outDir: '../static',
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  },

  plugins: [
    vue(),
    WindiCSS(),
    Components({
      resolvers: [
        IconsResolver({
          componentPrefix: '',
          alias: {
            hi: 'humbleicons'
          }
        })
      ],
      dts: 'src/components.d.ts'
    }),
    Icons(),
    AutoImport({
      imports: [
        'vue',
        '@vueuse/core'
      ],
      dts: 'src/auto-imports.d.ts'
    }),
    TopLevelAwait({
      promiseExportName: '__tla',
      promiseImportName: i => `__tla_${i}`
    })

  ],

  server: {
    port: 3333
  }
})

export default config
