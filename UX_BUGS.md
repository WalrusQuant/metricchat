# UX Bug Tracker

## 🔴 Critical

- [x] **1. Report state not reset when navigating between reports** — `pages/reports/[id]/index.vue:503` — Messages, visualizations, split-screen state persist from previous report. Users see stale data flash. **Fixed:** Added `watch(route.params.id)` + `cleanupReportState()`/`initReportPage()` to reset all 30+ refs on navigation.

- [x] **2. Event listener leak on report navigation** — `pages/reports/[id]/index.vue:1725-1729` — `dashboard:ensure_open` listener added on mount but never removed. Each report visit adds another, causing phantom split-screen toggles. **Fixed:** Replaced anonymous listener with named `handleDashboardEnsureOpen`, removed in `cleanupReportState()`.

- [x] **3. Active SSE stream not aborted on navigation** — `pages/reports/[id]/index.vue` + `layouts/default.vue:41` — Clicking logo or "New Report" while streaming doesn't cancel the AbortController. Old stream runs in background. **Fixed:** `cleanupReportState()` calls `currentController?.abort()` on route change and unmount.

- [x] **4. Polling timers leak across reports** — `pages/reports/[id]/index.vue:2201-2240` — Polling for in-progress completions isn't stopped on route change (only in `onUnmounted`, which doesn't fire for same-layout navigation). **Fixed:** `cleanupReportState()` calls `stopPollingInProgressCompletion()` on route change.

- [x] **5. No 401 interceptor — silent auth expiry** — `composables/useMyFetch.ts:61-68` — Expired JWT causes silent API failures. No re-auth trigger, no global logout on 401. **Fixed:** Added `handleAuthError()` with redirect guard, intercepting 401 in all 3 code paths (stream, $fetch, useFetch).

- [x] **6. Settings plugin crashes app on API failure** — `plugins/settings.ts` — No try-catch on `$fetch('/api/settings')`. Backend down = blank page, no error message. **Fixed:** Wrapped in try-catch with empty object fallback and `??` defaults for all runtime config values.

- [x] **7. Upload error permanently disables button** — `pages/onboarding/data/index.vue:212-214` — `uploadingFile` never reset to `false` on failure. Button stays disabled until page reload. **False positive:** JavaScript `finally` blocks execute even after early `return` inside `try`. The reset on line 233 always runs.

## 🟡 Important

- [x] **8. Two "New Report" buttons behave differently** — Sidebar (`layouts/default.vue:364-392`) creates empty report with no error toast. Reports list (`pages/reports/index.vue:648`) has proper error handling. Home page prompt auto-submits on arrival. Inconsistent behavior. **Fixed:** Added error toast to sidebar `createNewReport` and `PromptBoxV2.createReport`. Reports list now uses `useDomain()` `selectedDomainObjects` instead of fetching all data sources.

- [x] **9. Organization loading has no timeout** — `composables/useOrganization.ts:14-22` — `getSession({ force: true })` has no timeout. If `/api/users/whoami` hangs, entire app hangs since every API call goes through `ensureOrganization()`. **Fixed:** Wrapped `getSession()` in `Promise.race` with 5s timeout and try-catch fallback.

- [x] **10. Permissions bypass on first page load** — `middleware/permissions.global.ts:22-29` — `permissionsLoaded === false` on initial state causes middleware to return early, allowing any page to render before redirect. **Fixed:** Changed `permissionsLoaded` from boolean to tri-state (`'loading' | 'loaded' | 'error'`). Middleware now polls up to 5s for permissions to load before redirecting to `/`.

- [x] **11. Error page has no safe recovery** — `error.vue` — Only "Go home" option. If home is broken, users get stuck in redirect loop. No "Go back", "Sign out", or "Try again". **Fixed:** Added "Go back", "Reload page" (for 500s), and "Sign out" buttons alongside existing "Go home".

- [x] **12. Missing route: `/onboarding/data/schema`** — `pages/onboarding/data/index.vue:186` — Fallback navigates to route without `[ds_id]` param. Route doesn't exist, users hit 404. **Fixed:** Changed fallback to redirect to `/onboarding/data` instead of dead `/onboarding/data/schema` route.

- [x] **13. Connection test gate with no escape** — `components/datasources/ConnectForm.vue:184` — Must pass connection test before saving. If test fails (firewall, restricted access), complete dead end. **Fixed:** Removed `!connectionTestPassed` from submit disabled condition. Button shows "Save Without Testing" when untested, tooltip warns "Connection has not been tested".

- [x] **14. Domain selector state inconsistency** — `layouts/default.vue:369-370` — Sidebar "New Report" uses `selectedDomainObjects` from domain selector. Reports list page has its own selection. Different data sources depending on which button is clicked. **Fixed:** Reports list now uses `useDomain()` `selectedDomainObjects` instead of fetching all data sources from API.

- [x] **15. Permissions marked "loaded" even on error** — `plugins/fetchPermissions.client.ts` — On error, `permissionsLoaded = true` still set. Navigation proceeds with empty permissions, potentially granting access to restricted pages. **Fixed:** Error paths now set `permissionsLoaded = 'error'` instead of `true`. Only successful permission fetch sets `'loaded'`.

## 🔵 Suggestions

- [x] **16. Split-screen state persists across reports** — Opening report A in split-screen, then creating report B, lands in split-screen on B. **Fixed:** Resolved by Bug #1 fix — `initReportPage()` resets `isSplitScreen = false` before loading new report data.

- [x] **17. Non-admin users can reach onboarding forms** — `/onboarding` paths bypass permission middleware. Users without `create_data_source` permission see forms but fail on submit.

- [x] **18. No loading indicator during data source fetch** — `pages/onboarding/data/index.vue` renders before data sources load, causing brief empty grid flash.

- [x] **19. Form state not reset on back navigation** — Going back from connection form and re-selecting same data source retains old credential values.

- [skipped] **20. Confusing dual URL hierarchy** — `/data/new/{id}/schema` vs `/data/{id}/schema` — two parallel paths for similar operations with no clear transition.

- [x] **21. Remove "Upload a CSV or Excel file to query" link from home page** — `pages/index.vue:56-68` — Light text link and hidden file input on the home page. Remove the entire quick CSV upload block including the handler logic. **Fixed:** Removed template block, `uploadingCsv`, `toast`, `findFileUploadConnection()`, `handleCsvUpload()`, `useExcel` import, and unused `initDomain`/`selectDomains` destructuring.

- [x] **22. Unused `KeyCode` import from monaco-editor on home page** — `pages/index.vue:135` — `import { KeyCode } from 'monaco-editor'` was imported but never referenced. Accidental leftover from upstream `onboarding` commit (`fa8159ee`). **Fixed:** Removed.

## 🟠 TypeScript Errors (pre-existing)

- [x] **23. CompletionMessageComponent props untyped** — `components/CompletionMessageComponent.vue` — Props use bare `Object` type. Every property access (`.status`, `.role`, `.completion`, `.widget`, `.prompt`, `.sigkill`) fails typecheck. Needs a proper interface.

- [x] **24. ConnectForm mode type incomplete** — `components/datasources/ConnectForm.vue:133` / `components/AddConnectionModal.vue:130` — `mode` prop typed as `'onboarding' | 'create' | 'edit'` but `'create_connection_only'` is used at runtime. Union type needs updating.

- [x] **25. AgGridComponent loose types** — `components/AgGridComponent.vue` — Spread on `unknown` types, implicit `any` on `trace` parameter. Needs typed column definitions and error handler signature.

- [x] **26. Reports index untyped API responses** — `pages/reports/index.vue` — API response cast as `{}` instead of proper interface. Accessing `.reports` and `.meta` fails typecheck. Needs response type definitions.
