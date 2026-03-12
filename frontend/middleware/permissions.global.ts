import { useCan, usePermissionsLoaded } from '~/composables/usePermissions'

export default defineNuxtRouteMiddleware(async (to, from) => {
  // Skip permission checks for auth/public pages
  const publicPaths = ['/users/', '/organizations/', '/onboarding', '/r/', '/not_found']
  if (publicPaths.some(path => to.path.startsWith(path))) {
    return
  }

  // Skip if no permissions required for this route
  const requiredPermissions = (to.meta.permissions as string[] | undefined) || []
  if (!requiredPermissions.length) {
    return
  }

  // Get auth status - if not authenticated, let the auth middleware handle redirect
  const { status } = useAuth()
  if (status.value !== 'authenticated') {
    return
  }

  // Check if permissions have been loaded
  const permissionsLoaded = usePermissionsLoaded()

  // Wait for permissions to finish loading (up to 5s)
  if (permissionsLoaded.value === 'loading') {
    const start = Date.now()
    while (permissionsLoaded.value === 'loading' && Date.now() - start < 5000) {
      await new Promise(resolve => setTimeout(resolve, 50))
    }
  }

  // If still loading or errored, redirect to home with no permission check
  if (permissionsLoaded.value !== 'loaded') {
    if (to.path === '/' || to.path === '') {
      return
    }
    return navigateTo('/')
  }

  // Check if user has all required permissions
  let hasPermission = true
  for (const permission of requiredPermissions) {
    const can = useCan(permission)
    if (!can) {
      hasPermission = false
      break
    }
  }

  if (!hasPermission) {
    // Don't redirect to '/' if already on '/' to avoid infinite loop
    if (to.path === '/' || to.path === '') {
      return
    }

    // Redirect to home for protected pages user can't access
    return navigateTo('/')
  }
})
