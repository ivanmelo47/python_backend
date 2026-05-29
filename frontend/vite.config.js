import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');
    const hmrHost = env.VITE_HMR_HOST || 'localhost';
    const devPort = Number(env.VITE_DEV_SERVER_PORT || 5173);

    return {
        plugins: [
            vue({
                template: {
                    transformAssetUrls: {
                        base: null,
                        includeAbsolute: false,
                    },
                },
            }),
            tailwindcss(),
        ],
        server: {
            host: '0.0.0.0',
            port: devPort,
            strictPort: true,
            cors: true,
            origin: `http://${hmrHost}:${devPort}`,
            hmr: {
                host: hmrHost,
                protocol: 'ws',
                port: devPort,
                clientPort: devPort,
            },
            proxy: {
                '/storage': {
                    target: env.VITE_API_BASE_URL ? env.VITE_API_BASE_URL.replace(/\/api$/i, '') : 'http://localhost:8000',
                    changeOrigin: true,
                    secure: false,
                },
            },
        },
        resolve: {
            alias: {
                '@': '/resources/js',
            },
        },
        build: {
            chunkSizeWarningLimit: 900,
            rollupOptions: {
                output: {
                    manualChunks(id) {
                        if (!id.includes('node_modules')) {
                            return;
                        }

                        const normalizedId = id.replaceAll('\\', '/');
                        const modulePath = normalizedId.split('/node_modules/')[1];

                        if (!modulePath) {
                            return 'vendor';
                        }

                        const segments = modulePath.split('/');
                        const packageName = segments[0].startsWith('@')
                            ? `${segments[0]}/${segments[1]}`
                            : segments[0];

                        if (packageName === 'vue' || packageName === '@vue/devtools-api') {
                            return;
                        }

                        return `vendor-${packageName.replace('@', '').replace('/', '-')}`;
                    },
                },
            },
        },
    };
});
