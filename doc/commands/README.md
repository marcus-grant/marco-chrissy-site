# Command System

## Overview

This project uses a molecule-inspired cascading command system where each command calls only its immediate predecessor, creating a clean chain of execution.

## Command Documentation

- [Pipeline Commands](pipeline.md) - Main site building commands
- [Build Command](build.md) - Complete site generation documentation
- [Serve Command](serve.md) - Development server with proxy routing
- [Development Commands](development.md) - Developer workflow commands  
- [Galleria Commands](galleria.md) - Gallery-specific commands

## Command Pattern

### Cascading Rule
Each command calls only its immediate predecessor. The chain executes automatically:
- `deploy` calls `build` only (which calls `organize` → `validate`)
- `build` calls `organize` only (which calls `validate`)
- `organize` calls `validate` only
- `validate` calls nothing

### Benefits
- Simple implementation (no complex dependency management)
- Clear execution order
- Easy to reason about and debug
- Fail-fast validation before expensive operations