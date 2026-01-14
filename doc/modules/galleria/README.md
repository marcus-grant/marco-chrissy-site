# Galleria Module Documentation

## Overview

Galleria is a focused gallery generator that converts NormPic manifests into static HTML galleries. This directory contains detailed documentation for each Galleria module.

## Module Documentation

- [Plugin System](plugin-system.md) - Plugin architecture and extensibility framework
- [Serializer Module](serializer.md) - Photo collection loading and manifest parsing
- [Processor Module](processor.md) - Image processing and thumbnail generation
- [Template Filters](template-filters.md) - Jinja2 filters for context-aware URL generation
- [Template Plugins](template-plugins.md) - Template plugin implementations
- [Themes](themes.md) - Theme system and asset management
- [Testing Fixtures](testing-fixtures.md) - Comprehensive test fixtures for galleria development

## Module Status

**✅ Completed**:
- Plugin System: Complete foundation with interfaces, exceptions, hooks, and implementations
- Serializer: NormPic v0.1.0 manifest loading
- Processor: Thumbnail generation with caching
- Template Filters: Context-aware URL generation with BuildContext integration
- Template: HTML rendering system with plugin architecture
- Generator: Workflow orchestration
- Themes: Asset and template management
