# Pipeline Commands

## Main Site Commands

The core site building pipeline follows this cascading sequence:

### 1. validate
**Purpose**: Validate all configs and dependencies before any work begins  
**Calls**: Nothing (base command)

**Responsibilities**:
- Validate all config files (site.json, normpic configs, galleria configs)
- Check source photo directories exist and are readable
- Verify output directories are writable  
- Check required env vars are set for deployment
- Verify NormPic executable is available

### 2. organize  
**Purpose**: Organize photos using NormPic  
**Calls**: `validate` only

**Responsibilities**:
- Run NormPic for photo organization
- Generate photo manifests

### 3. build
**Purpose**: Generate the complete site  
**Calls**: `organize` only (which calls `validate`)

**Responsibilities**:
- Run galleria for gallery generation via `galleria.generate()` Python module
- Run Pelican for site generation via `pelican.Pelican().run()` Python module  
- Create integrated output structure:
  ```
  output/
  ├── pics/           # From organize (NormPic)
  ├── galleries/      # From galleria generation
  │   └── wedding/    
  ├── about/          # From pelican generation  
  └── index.html      # From pelican generation
  ```
- Provide progress reporting and error handling for each stage
- Support basic idempotency (skip if output files exist)

### 4. deploy
**Purpose**: Deploy site to CDN  
**Calls**: `build` only (which calls full chain)

**Responsibilities**:
- Upload to Bunny CDN
- Set appropriate cache headers
- Validate deployment

## Implementation Location
Pipeline commands are implemented in the `cli/commands/` module. Each command uses direct Python module imports rather than subprocess calls for better integration and error handling.