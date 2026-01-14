# Changelog

Buffer for changes during current development cycle. Migrated to `doc/release/X-Y.md` at each release.

## Format

```markdown
## YYYY-MM-DD

- Brief description of what was done
- Another change
```

**Guidelines:**
- Date headers in descending order (latest first)
- Terse descriptions - what was done, not phase/cycle numbers
- Migrate to release notes before tagging

---

## 2026-01-14

- Add touch-friendly pagination controls (44px min-height/min-width)
- Fix navbar margin by adding body reset (margin: 0) to shared.css
- Fix Pelican navbar to use responsive hamburger structure
  - Updated shared/header.html to match navbar.html structure
  - Both Pelican and Galleria now render identical responsive navbars
- Add unit test for body margin reset
- Add mobile-first gallery grid with responsive breakpoints
  - 2 cols (default), 3 cols (560px), 4 cols (768px), 6 cols (1024px)
  - Uses min-width media queries for progressive enhancement
- Add CSS-only responsive mobile navbar
  - Checkbox toggle with animated hamburger icon
  - Hidden on desktop, visible on mobile (<768px)
  - Nav links collapse to dropdown menu
  - 44px touch targets for accessibility
- Add CSS custom properties to shared.css for responsive design
  - Breakpoints: 480px, 768px, 1024px, 1200px
  - Touch target minimum: 44px (WCAG 2.1 AAA)
  - Spacing scale: xs/sm/md/lg
- Add E2E tests for responsive layout (skipped until implementation)
  - CSS variables: breakpoints, touch targets, spacing
  - Gallery grid: 1→2→3→4→6 column breakpoints
  - Navbar: CSS-only mobile menu structure
  - Typography: clamp() for fluid sizing

