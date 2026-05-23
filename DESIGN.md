# DESIGN.md - Developer Portfolio

## 1. Visual Theme & Atmosphere

- **Mood:** Minimalist, confident, premium, dark-first
- **Density:** Medium whitespace, editorial feel with intentional breathing room
- **Philosophy:** Let the work speak. Typography is the hero. Dark surfaces with subtle elevation.
- **Inspiration:** Linear (precision), Vercel (developer-focused), SpaceX (stark imagery)

## 2. Color Palette & Roles

| Token | Hex | Role |
|---|---|---|
| `background` | `#0a0a0a` | Near-black canvas. Never pure `#000000` |
| `surface` | `#171717` | Elevated cards, sections, input backgrounds |
| `surface-elevated` | `#262626` | Hover states, active selections |
| `primary-text` | `#fafafa` | Headings, primary body text |
| `secondary-text` | `#a3a3a3` | Metadata, captions, disabled states |
| `muted-text` | `#737373` | Placeholders, subtle labels |
| `accent` | `#3b82f6` | CTAs, links, focus rings, interactive highlights |
| `accent-hover` | `#2563eb` | Accent hover state |
| `border` | `#262626` | Subtle dividers, card outlines |
| `border-hover` | `#404040` | Hover state for borders |
| `success` | `#22c55e` | Positive states, confirmations |
| `warning` | `#eab308` | Alerts, caution |
| `error` | `#ef4444` | Errors, destructive actions |

### Usage Rules
- Backgrounds must always be tinted (warm or cool), never pure gray or pure black.
- Text on colored/accent backgrounds must be white or near-white.
- Borders should be subtle; use them to define structure, not decoration.

## 3. Typography

- **Heading Font:** Geist Sans (default Next.js 15 font)
- **Body Font:** Geist Sans
- **Mono Font:** Geist Mono (code, labels, technical metadata)

### Scale
| Token | Size | Weight | Letter-Spacing | Line-Height |
|---|---|---|---|---|
| `display` | `64px` | `700` | `-0.03em` | `1.1` |
| `h1` | `48px` | `600` | `-0.02em` | `1.15` |
| `h2` | `36px` | `600` | `-0.015em` | `1.2` |
| `h3` | `24px` | `600` | `-0.01em` | `1.3` |
| `h4` | `20px` | `500` | `-0.005em` | `1.35` |
| `body` | `16px` | `400` | `0` | `1.6` |
| `body-sm` | `14px` | `400` | `0` | `1.5` |
| `caption` | `12px` | `500` | `0.02em` | `1.4` |
| `mono` | `14px` | `400` | `0` | `1.5` |

### Rules
- Headings must use negative letter-spacing for a tight, modern feel.
- Body text must be comfortable to read (line-height >= 1.5).
- All caps only for labels/captions, never for body or headings.

## 4. Component Stylings

### Buttons
- **Default:** `bg-surface`, `text-primary`, `border-border`, `rounded-md`, `px-4 py-2`
- **Hover:** `bg-surface-elevated`, `border-border-hover`, `transition-all duration-200`
- **Primary:** `bg-accent`, `text-white`, `border-transparent`
- **Primary Hover:** `bg-accent-hover`
- **Ghost:** `bg-transparent`, `text-secondary`, hover `text-primary`
- **Disabled:** `opacity-50`, `cursor-not-allowed`

### Cards
- **Background:** `bg-surface`
- **Border:** `1px solid border`
- **Border Radius:** `rounded-lg` (8px) — subtle, not too round
- **Shadow:** None. Rely on border and background contrast for elevation.
- **Padding:** `p-6`

### Inputs
- **Background:** `bg-surface`
- **Border:** `1px solid border`, `rounded-md`
- **Focus:** `ring-2 ring-accent ring-offset-2 ring-offset-background`
- **Placeholder:** `text-muted`
- **Disabled:** `opacity-50`

### Navigation
- **Background:** `bg-background/80 backdrop-blur-md` (sticky/fixed)
- **Height:** `64px`
- **Links:** `text-secondary`, hover `text-primary`, `transition-colors duration-200`

## 5. Layout Principles

- **Max Width:** `1200px` centered (`mx-auto`)
- **Section Padding:** `py-24 md:py-32` (desktop), `py-16` (mobile)
- **Grid:** 12-column implicit grid, `gap-6`
- **Whitespace:** Generous vertical padding between sections. Let content breathe.

## 6. Depth & Elevation

- **No heavy drop shadows.**
- **Elevation is communicated via:**
  - Background color shifts (`background` → `surface` → `surface-elevated`)
  - Subtle borders (`border`)
  - Backdrop blur for overlays (`backdrop-blur-md`)
- **Z-Index Scale:**
  - Base: `0`
  - Sticky nav: `40`
  - Modals/Overlays: `50`
  - Tooltips: `60`

## 7. Do's and Don'ts

### Do
- Use tight letter-spacing on large headings.
- Use tinted neutrals for backgrounds.
- Ensure all interactive elements have hover and focus states.
- Use Lucide React for all icons.
- Respect `prefers-reduced-motion`.
- Use semantic HTML (`<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`).

### Don't
- Use pure black (`#000000`) or pure gray (`#808080`) for backgrounds.
- Use gray text on colored backgrounds.
- Nest cards inside cards.
- Use bounce, elastic, or spring easing for UI transitions.
- Use emojis as icons.
- Forget `cursor-pointer` on clickable elements.
- Skip focus-visible states.

## 8. Responsive Behavior

| Breakpoint | Width | Behavior |
|---|---|---|
| `base` | < 640px | Mobile-first. Single column. Reduced typography scale. |
| `sm` | >= 640px | Minor adjustments. |
| `md` | >= 768px | Tablet. 2-column grids begin. Full typography scale. |
| `lg` | >= 1024px | Desktop. Full layout. Sidebar layouts possible. |
| `xl` | >= 1280px | Wide desktop. Max-width container kicks in. |
| `2xl` | >= 1536px | Ultra-wide. Extra padding if needed. |

### Touch Targets
- Minimum `44x44px` for all interactive elements on mobile.

## 9. Agent Prompt Guide

When generating UI for this portfolio:

1. **Read this DESIGN.md first.** All components must use the tokens defined here.
2. **Use the dark palette** unless the user explicitly asks for light mode.
3. **Typography:** Geist Sans for everything except code (Geist Mono). Tight letter-spacing on headings.
4. **Components:** Check `src/components/ui/` for existing shadcn components. Build custom only when necessary.
5. **Animations:** Subtle and purposeful. Fade-up entrances, smooth hover transitions. No bouncing.
6. **Accessibility:** ARIA labels on icon buttons, semantic HTML, focus-visible rings, alt text on images.
7. **Code Quality:** TypeScript strict, explicit return types, clean Tailwind classes (no arbitrary values unless justified).
