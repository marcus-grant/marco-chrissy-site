# Changelog

## 2026-01-14

### Dead Code Investigation & Cleanup

- **Removed dead code**: ~190 lines of commented-out proxy implementation in `cli/commands/serve.py` (already extracted to `serve/proxy.py`)
- **Documented serializer intent**: `galleria/serializer/` is incomplete extraction infrastructure, not dead code
- **Investigation findings**: All config files active, PIL usage correct, skipped tests are post-MVP placeholders

### Documentation Quality Assurance

- **New command docs**: Created organize.md and benchmark.md for missing site commands
- **Fixed broken links**: Config path refs in galleria.md, .toml→.json in serve.md
- **Updated galleria README**: Moved completed items from "In Progress", added nav links
- **Added missing doc links**: CONTRIBUTE.md and HANDOFF.md now in doc/README.md
- **Fixed link hierarchy**: Deep links now use READMEs per documentation rules
- **Marked planned commands**: development.md commands noted as future implementation
- **Merged duplicates**: bconfiguration.md content merged into configuration.md

