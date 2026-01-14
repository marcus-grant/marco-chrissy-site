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

- Add CSS custom properties to shared.css for responsive design
  - Breakpoints: 480px, 768px, 1024px, 1200px
  - Touch target minimum: 44px (WCAG 2.1 AAA)
  - Spacing scale: xs/sm/md/lg
- Add E2E tests for responsive layout (skipped until implementation)
  - CSS variables: breakpoints, touch targets, spacing
  - Gallery grid: 1→2→3→4→6 column breakpoints
  - Navbar: CSS-only mobile menu structure
  - Typography: clamp() for fluid sizing

