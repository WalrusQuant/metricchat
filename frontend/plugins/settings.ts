export default defineNuxtPlugin(async (nuxtApp) => {
    let config: any = {}
    try {
      config = await $fetch('/api/settings')
    } catch (error) {
      console.error('Failed to load app settings:', error)
    }

    // Make settings available throughout the app
    nuxtApp.provide('settings', config)

    // Update runtime config with fetched settings
    const runtimeConfig = useRuntimeConfig()
    Object.assign(runtimeConfig.public, {
      googleSignIn: config.google_oauth?.enabled ?? false,
      deployment: config.deployment?.type ?? 'self-hosted',
      version: config.version ?? 'unknown',
      environment: config.environment ?? 'production',
      app_url: config.base_url ?? '',
      intercom: {
        enabled: config.intercom?.enabled ?? false
      }
    })
  })
