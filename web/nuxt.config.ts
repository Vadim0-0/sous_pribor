const apiProxyTarget = process.env.NUXT_API_PROXY || 'http://localhost:8000'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },

  typescript: {
    nodeTsConfig: {
      compilerOptions: {
        types: ['node'],
      },
    },
  },

  css: ['~/assets/styles/main.scss'],

    components: [
    {
      path: '~/components',
    },
    {
      path: '~/components/ui'
    }
  ],

  routeRules: {
    '/api/**': {
      proxy: `${apiProxyTarget}/api/**`,
    },
  },

  vue: {
    compilerOptions: {
      isCustomElement: (tag) => tag === 'model-viewer',
    },
  },
})

