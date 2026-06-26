import {defineConfig} from 'vite'


export default defineConfig({
    build: {
        outDir: 'static/dist',
        emptyOutDir: true,
        rollupOptions: {
            input: {
                main: './static/js/main.js'
            },
            output: {
                entryFileNames: 'main.js',
                chunkFileNames: 'chunks/[name].js',
                assetFileNames: (assetInfo) => {
                    if (assetInfo.name.endsWith('.css')) {
                        return 'main.css'
                    }
                    return 'assets/[name][extname]'
                }
            }
        }
    }
})
//npx vite build --watch