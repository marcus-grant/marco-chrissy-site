# Module Organization Patterns

## Rules

### Avoid Catch-All Patterns
**❌ Bad**:
- `core/` - too generic
- `utils/` - dumping ground
- `common/` - unclear purpose
- `shared/` - vague responsibility

**✅ Good**:
- `validation/` - validates configs and dependencies
- `template/` - handles template loading and rendering
- `serializer/` - handles config and manifest (de)serialization

### Exception: Utility Modules
`util/` is acceptable **only** when it contains:
- Singular-purpose modules
- Simple, testable, pure functions
- Generic functionality (not domain-specific)

**Example acceptable `util/` contents**:
- `util/filesystem.py` - file system helpers
- `util/validation.py` - generic validation functions
- `util/formatting.py` - string/data formatting

### Generic vs Domain-Specific
**Generic modules** (acceptable in `util/`):
- Pure functions with no business logic
- Reusable across multiple domains
- Simple, well-tested interfaces

**Domain-specific modules** (get their own directories):
- Business logic and workflows
- Domain knowledge and rules
- Context-aware functionality

## Patterns by Project

### Orchestrators vs Managers

**Site Project** → **Orchestrators**
- Coordinates multiple external tools
- Manages workflows and data flow
- Examples: `build/`, `deployment/`

**Galleria** → **Managers** (and some orchestrators)
- Manages internal resources and processes
- Examples: `template/` (manager), `generator/` (orchestrator)

## Anti-Patterns

### Directory Dumping Grounds
- Directories with too many unrelated files
- Modules that do "everything" 
- Unclear naming conventions

### Tight Coupling
- Circular dependencies between modules
- Direct imports across major boundaries
- Shared mutable state