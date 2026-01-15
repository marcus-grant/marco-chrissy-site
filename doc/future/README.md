# Future Architecture Documentation

This directory contains architectural vision and planning for post-MVP modularization.

## Documents

- [Generalization Strategy](generalization.md) - Modular architecture vision for extracting reusable components
- [Galleria Extraction](galleria-extraction.md) - Strategy for extracting Galleria as standalone package
- [Architecture Decisions](architecture-decisions.md) - SSG evaluation and strategic direction

## Overview

Post-MVP, the project will be modularized into reusable components:
- **Galleria** - Standalone photo gallery generator
- **SnakeCharmer** - Multi-paradigm site orchestration framework (coordinates SSG, APIs, micro frontends, CDN deployment)
- **Cobra** - Python-based SSG inspired by 11ty (Pelican replacement)
- **Endpoint Abstraction** - Deploy same logic as static/FastAPI/HTMX/edge functions
- **This Repository** - Configuration/deployment hub for marco-chrissy-site