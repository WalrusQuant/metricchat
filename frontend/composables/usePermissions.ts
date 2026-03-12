export const usePermissions = () => {
  return useState<string[]>('permissions', () => [])
}

export const usePermissionsLoaded = () => {
  return useState<'loading' | 'loaded' | 'error'>('permissionsLoaded', () => 'loading')
}

// Add the useCan function to check permissions
export const useCan = (permission: string) => {
  const permissions = usePermissions()
  const permissionsLoaded = usePermissionsLoaded()

  // Only return true if permissions are loaded and permission exists
  return permissionsLoaded.value === 'loaded' && permissions.value.includes(permission)
}
