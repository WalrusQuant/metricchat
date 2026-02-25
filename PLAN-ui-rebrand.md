# Plan: UI Visual Rebrand — "Refined Instrument"

## Brand Personality

MetricChat feels like a precision tool for data work — confident, clean, with enough warmth and character to feel human-designed rather than template-generated.

## Current State

- Primary color: Blue (`#2563eb` / Tailwind `blue-600`) — stock Tailwind
- Font: Inter / system-ui — the most generic choice possible
- Neutrals: Cold grays (`gray-50` through `gray-900`)
- Layout: Identical to BoW with no visual identity
- Logos: Still using renamed BoW logo files
- No centralized theme config — all hardcoded Tailwind classes

---

## 1. Color System

Custom values, not Tailwind defaults. The warm neutrals are the biggest differentiator — most AI tools use cold blue-grays.

| Role | Hex | Tailwind Token | Usage |
|------|-----|---------------|-------|
| Primary | `#0C7C7C` | `primary-600` | Buttons, links, active states. Deep teal — richer than stock `teal-600`. |
| Primary hover | `#0A6363` | `primary-700` | Darkened primary for hover/press |
| Primary light | `#E6F4F4` | `primary-50` | Subtle backgrounds, highlights, badges |
| Primary 100 | `#CCE9E9` | `primary-100` | Light borders, focus rings |
| Primary 200 | `#99D3D3` | `primary-200` | Lighter accents |
| Primary 300 | `#66BDBD` | `primary-300` | Focus rings |
| Primary 400 | `#33A7A7` | `primary-400` | Icons, secondary text |
| Primary 500 | `#109090` | `primary-500` | Slightly lighter primary |
| Primary 800 | `#084F4F` | `primary-800` | Dark text on light primary bg |
| Primary 900 | `#063B3B` | `primary-900` | Darkest primary |
| Accent | `#C4841D` | — | Sparingly: active indicators, stars, premium badges. Warm gold that contrasts the cool primary. |
| Background | `#FAFAF8` | — | Main page bg (warm off-white, not cold `#F9FAFB`) |
| Surface | `#F3F2EF` | — | Cards, sidebar bg (warm stone, not `gray-50`) |
| Border | `#D6D3CD` | — | Borders (warm, not `gray-200`) |
| Text | `#1C1917` | `stone-900` | Primary text (warmer than `slate-900`) |
| Muted text | `#78716C` | `stone-500` | Secondary text (warmer than `gray-500`) |

---

## 2. Typography

Kill Inter. It's the single biggest "AI slop" signal.

| Role | Font | Weight | Source |
|------|------|--------|--------|
| Headings | **DM Sans** | 700 (Bold), 600 (Semibold) | Google Fonts |
| Body | **DM Sans** | 400 (Regular), 500 (Medium) | Google Fonts |
| Data/Code | **JetBrains Mono** | 400, 500 | Google Fonts |

DM Sans has distinctive geometric letterforms (look at the 'a' and 'g') — professional but noticeably not Inter. JetBrains Mono for SQL, metric values, and chart labels creates a "data tool" identity.

Load both via `@nuxtjs/google-fonts` or the Nuxt head config.

---

## 3. Signature Detail: Teal Left-Edge Accent

One recurring visual motif that makes MetricChat recognizable: a **2-3px left border in primary teal** on active/focused elements. Instead of highlighting with background color changes (which every tool does), use a sharp left accent edge.

Where it appears:
- Active sidebar item → teal left border (not gray background)
- AI response in chat → subtle teal left border
- Selected dashboard card → teal left border
- Active input/card focus → teal left border

This creates a consistent "that's MetricChat" effect.

---

## 4. Spatial Adjustments

Small changes, big impact:

| Change | From | To | Why |
|--------|------|----|-----|
| Card border-radius | `rounded-xl` (12px) | `rounded-lg` (8px) | Tighter radii feel more precise. Oversized radii = 2023 AI SaaS. |
| Sign-in card | `shadow-sm` | No shadow, `1px` warm border only | Shadows on centered auth cards are overused. Clean border is more confident. |
| Sidebar border | `border-r-[3px] border-gray-100` | `border-r border-[#D6D3CD]` | Thinner, warm-toned |
| Sidebar background | `bg-gray-50` | `bg-[#F3F2EF]` | Warm stone instead of cold gray |
| Button padding | Current chunky sizing | Slightly less padding, `font-medium` not `font-semibold` | Less chunky = more refined |

---

## 5. What NOT to Change

- Sidebar width (`w-48` / `w-14`) — structure is fine
- Page grid / chat interface layout — fine
- Nuxt UI component library — keep it, just retheme
- Dashboard grid system — fine
- Responsive breakpoints — fine

This is a material/finish change, not a layout redesign.

---

## 6. Logo

Create a clean SVG wordmark: "MetricChat" in DM Sans Bold, primary teal color. No icon — a confident wordmark is better than a forgettable Canva icon.

**Files to replace:**
- `frontend/public/assets/logo.png` → SVG wordmark (~200x50px)
- `frontend/public/assets/logo-128.png` → "M" lettermark in teal on white (128x128px)
- `frontend/public/favicon.ico` → "M" lettermark (32x32px)
- `media/logo-128.png` → Same as above

---

## 7. Implementation Steps

### Step 1: Theme Foundation (30 min)

Create `frontend/tailwind.config.ts` with custom `primary` color scale and warm neutral overrides. Create or update `frontend/app.config.ts` to set Nuxt UI's default color to `primary`.

Load DM Sans + JetBrains Mono via Nuxt head config or `@nuxtjs/google-fonts`.

### Step 2: Auth Pages (30 min)

**Files:** `frontend/pages/users/sign-in.vue`, `frontend/pages/users/sign-up.vue`

- Swap `blue-*` → `primary-*` on buttons, links, focus states
- Swap `gray-*` → warm neutrals on backgrounds, borders, text
- Drop card shadow, use warm border only
- Tighten card radius to `rounded-lg`
- Update font stack (will cascade from global config)

### Step 3: Sidebar + Layout (45 min)

**Files:** `frontend/layouts/default.vue`

- Sidebar bg → `#F3F2EF`
- Sidebar border → `1px` warm border
- Active item → teal left-border accent (not bg change)
- Avatar bg → primary teal
- Onboarding banner → primary teal
- Swap all `blue-*` and `gray-*` references

### Step 4: Home Page (20 min)

**Files:** `frontend/pages/index.vue`

- Update gradient glow colors (currently purple-to-cyan → teal-to-gold)
- Swap any blue references
- Update placeholder/empty state text

### Step 5: Components + Settings (45 min)

Bulk find-and-replace across remaining files:

```
color="blue"           → color="primary" (Nuxt UI components)
bg-blue-*              → bg-primary-*
text-blue-*            → text-primary-*
border-blue-*          → border-primary-*
focus:border-blue-*    → focus:border-primary-*
focus:ring-blue-*      → focus:ring-primary-*
hover:bg-blue-*        → hover:bg-primary-*
hover:text-blue-*      → hover:text-primary-*
#2563eb                → #0C7C7C
#3b82f6                → #109090
```

Key files:
- `frontend/pages/settings/*.vue`
- `frontend/components/onboarding/OnboardingView.vue`
- `frontend/ee/components/UpgradeBanner.vue`
- All components with `color="blue"` prop

### Step 6: Dashboard Themes (20 min)

**Files:** `frontend/components/dashboard/themes/index.ts`

- Update default theme primary from `#2563eb` → `#0C7C7C`
- Update default palette to include the new brand colors
- Update chart fallback palettes in `RenderVisual.vue` and `ArtifactFrame.vue`

### Step 7: Logo + Favicon (20 min)

Create SVG wordmark and lettermark. Replace the 4 logo files.

### Step 8: Verify (15 min)

- [ ] Sign-in — new colors, warm neutrals, DM Sans font, no shadow
- [ ] Sign-up — matches sign-in
- [ ] Home page — teal accents, warm background
- [ ] Sidebar — warm stone bg, teal left-edge on active items
- [ ] Settings pages — buttons use primary teal
- [ ] Dashboard — charts use updated palette
- [ ] Favicon — "M" lettermark in browser tab
- [ ] No remaining `blue-600` / Inter / cold gray references

---

## 8. Time Estimate

| Step | Time |
|------|------|
| Theme foundation (Tailwind + fonts) | 30 min |
| Auth pages | 30 min |
| Sidebar + layout | 45 min |
| Home page | 20 min |
| Components + settings (bulk swap) | 45 min |
| Dashboard themes | 20 min |
| Logo + favicon | 20 min |
| Verify | 15 min |
| **Total** | **~3.5 hours** |
