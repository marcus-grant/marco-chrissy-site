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
- Run galleria for gallery generation (`uv run python -m galleria` for each config)
- Run Pelican for site generation
- Integrate outputs

### 4. deploy
**Purpose**: Deploy site to CDN  
**Calls**: `build` only (which calls full chain)

**Responsibilities**:
- Upload to Bunny CDN
- Set appropriate cache headers
- Validate deployment

## Implementation Location
Pipeline commands are implemented in the `orchestrator/` module as they coordinate multiple external tools.