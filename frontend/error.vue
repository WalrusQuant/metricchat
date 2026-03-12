<template>
  <UContainer class="page text-center px-6 py-16">
    <div class="max-w-xl w-full mx-auto">
      <img src="/assets/logo-icon.svg" alt="MetricChat" class="logo mx-auto mb-8" />

      <div v-if="error?.statusCode === 404" class="space-y-3">
        <h1 class="text-5xl font-semibold tracking-tight">404</h1>
        <p class="text-base text-stone-500">Page not found</p>
        <p class="text-sm text-stone-400">{{ route.fullPath }}</p>
      </div>

      <div v-else class="space-y-3">
        <h1 class="text-2xl font-semibold tracking-tight">Something went wrong</h1>
        <p class="text-base text-stone-600">{{ error?.message || 'Unknown error' }}</p>
      </div>

      <div class="mt-6 flex flex-wrap items-center justify-center gap-2">
        <UButton color="gray" variant="ghost" @click="goBack">Go back</UButton>
        <UButton color="gray" variant="ghost" to="/">Go home</UButton>
        <UButton v-if="isServerError" color="gray" variant="ghost" @click="reload">Reload page</UButton>
        <UButton color="gray" variant="ghost" @click="handleSignOut">Sign out</UButton>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
import type { NuxtError } from '#app'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps<{ error: NuxtError | null }>()
const error = props.error
const route = useRoute()
const router = useRouter()

const isServerError = computed(() => (error?.statusCode ?? 0) >= 500)

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    navigateTo('/')
  }
}

function reload() {
  window.location.reload()
}

async function handleSignOut() {
  try {
    const { signOut } = useAuth()
    await signOut({ callbackUrl: '/users/sign-in' })
  } catch {
    window.location.href = '/users/sign-in'
  }
}
</script>

<style scoped>
/* Minimal layout + subtle cursor behavior */
.page {
  min-height: 100vh;
  margin-top: 100px;
  align-items: center;
  justify-content: center;
  cursor: default;
}

.logo {
  width: 48px;
  height: 48px;
}

a, button {
  cursor: pointer;
}
</style>
