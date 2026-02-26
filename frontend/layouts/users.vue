<template>
  <div class="bg-[var(--brand-bg)]">
    <UNotifications />
    <slot />
  </div>
</template>

<script setup lang="ts">
const { getSession } = useAuth()
const route = useRoute()

onMounted(async () => {
  // If redirected with an access_token in query, let the target page set the token first
  if (route.query.access_token) {
    return
  }
  await getSession({ force: true })
})

</script>