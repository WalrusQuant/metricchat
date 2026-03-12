// /composables/useMyFetch.ts

let isRedirectingToLogin = false

function handleAuthError() {
  if (isRedirectingToLogin) return
  isRedirectingToLogin = true
  const { signOut } = useAuth()
  signOut({ callbackUrl: '/users/sign-in' }).finally(() => {
    isRedirectingToLogin = false
  })
}

export const useMyFetch: typeof useFetch = async (request, opts?) => {
  const config = useRuntimeConfig()
  const { token } = useAuth()
  const { organization, ensureOrganization } = useOrganization()

  // IMPORTANT: Capture component instance state BEFORE any await calls
  // After await, getCurrentInstance() may return null even in mounted components
  const isInComponent = getCurrentInstance() !== null
  const isClient = process.client

  // Ensure organization is loaded before making the request
  const orgResult = await ensureOrganization()

  opts = opts || {}
  opts.headers = {
    ...opts.headers,
    Authorization: `${token.value}`,
  }

  // Add the organization ID to the headers if it's set
  // Use the returned organization from ensureOrganization to avoid timing issues
  if (orgResult?.id) {
    opts.headers['X-Organization-Id'] = orgResult.id
  } else {
    // Still make the request but without org header - let backend handle the error
    console.warn('No organization ID available for API request:', request)
  }

  if (opts.stream) {
    return new Promise((resolve, reject) => {
      fetch(`${config.public.baseURL}${request}`, {
        ...opts,
        headers: opts.headers,
      }).then(response => {
        if (!response.ok) {
          if (response.status === 401) {
            handleAuthError()
          }
          reject(new Error(`HTTP error! status: ${response.status}`))
        } else {
          resolve({ data: response })
        }
      }).catch(reject)
    })
  }

  // Use $fetch for post-mounted requests to avoid Nuxt warning
  // The isInComponent check was captured before any awaits to be reliable
  if (isInComponent && isClient) {
    try {
      const data = await $fetch(request, {
        baseURL: config.public.baseURL,
        ...opts
      })
      return {
        data: ref(data),
        error: ref(null),
        pending: ref(false),
        refresh: () => {},
        status: ref('success')
      }
    } catch (error: any) {
      if (error?.response?.status === 401 || error?.status === 401 || error?.statusCode === 401) {
        handleAuthError()
      }
      return {
        data: ref(null),
        error: ref(error),
        pending: ref(false),
        refresh: () => {},
        status: ref('error')
      }
    }
  }

  const response = await useFetch(request, { baseURL: config.public.baseURL, ...opts })
  if (response.error.value) {
    const statusCode = (response.error.value as any)?.statusCode || (response.error.value as any)?.status
    if (statusCode === 401) {
      handleAuthError()
    }
  }
  return response
};
