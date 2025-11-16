# Development Commands

## Cascading Dev Commands

These development commands call pipeline commands to get fresh builds:

### serve
**Purpose**: Local development server for the full site  
**Calls**: `build` only (gets full chain: build → organize → validate)

**Responsibilities**:
- Generate fresh site build
- Serve locally for development
- Hot reload on changes (future enhancement)

### watch  
**Purpose**: Auto-rebuild when files change  
**Calls**: `build` only

**Responsibilities**:
- Monitor source files for changes
- Trigger builds automatically
- Report build status

## Standalone Dev Commands

These commands don't cascade - they're independent utilities:

### clean
**Purpose**: Clean up generated files  
**Calls**: Nothing

**Responsibilities**:
- Remove output directories
- Clear caches
- Reset to clean state

### test
**Purpose**: Run test suites  
**Calls**: Nothing

**Responsibilities**:
- Run `uv run pytest` for all modules
- Generate coverage reports
- Validate code quality

### lint
**Purpose**: Code quality checks  
**Calls**: Nothing

**Responsibilities**:
- Run `uv run ruff check`
- Validate configurations
- Check documentation links

### format
**Purpose**: Auto-format code  
**Calls**: Nothing

**Responsibilities**:
- Run `uv run ruff format`
- Fix code style issues