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

**Version Bump Process:**
- On minor/major version bump, move all timestamped sections (`## YYYY-MM-DD`) to `doc/release/X-Y.md`
- Only the timestamped sections are deleted; this header and format section remain
- Bump version in `pyproject.toml` and `galleria/__main__.py`
- This keeps the working changelog small while preserving history by release

---

