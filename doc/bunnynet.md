# Bunny.net CDN Deployment Setup


This guide covers setting up dual-zone deployment to Bunny.net CDN with separate storage zones for photos and site content.

## Overview

The deploy command uses a **dual storage zone strategy**:

- **Photo Zone**: Stores all images (`/output/pics/*`) with manifest-based incremental uploads
- **Site Zone**: Stores all other content (HTML, CSS, etc.) with full uploads

This separation optimizes deployment speed and CDN performance by treating photos differently from site content.

## Prerequisites

- Bunny.net account with CDN enabled
- Two storage zones created (see Setup Guide below)
- Environment variables configured with storage zone passwords

## Bunny.net Control Panel Setup

### 1. Create Photo Storage Zone

1. Log into [Bunny.net Dashboard](https://panel.bunny.net/)
2. Navigate to **Storage** → **Storage Zones**
3. Click **Add Storage Zone**
4. Configure:
   - **Name**: `your-site-photos` (e.g., `mycompany-site-photos`)
   - **Region**: Frankfurt (default) or your preferred region
   - **Replication**: Optional (can add later)
5. Click **Create**
6. **Important**: Note the **Storage Password** from the zone details

### 2. Create Site Content Storage Zone

1. Click **Add Storage Zone** again
2. Configure:
   - **Name**: `your-site-content` (e.g., `mycompany-site-content`)
   - **Region**: Your preferred region (can differ from photo zone)
   - **Replication**: Recommended for production (e.g., Stockholm + NY)
5. Click **Create**
6. **Important**: Note the **Storage Password** from the zone details

### 3. Configure Environment Variables

Each storage zone has its own unique password. The deploy configuration system reads environment variable names from `config/deploy.json`, allowing you to customize variable names:

```bash
# Configure your environment variables based on config/deploy.json settings
# Example configuration:
export BUNNYNET_PHOTO_PASSWORD="your-photo-zone-password"
export BUNNYNET_SITE_PASSWORD="your-site-zone-password"

# The deploy config determines which env vars to read:
# config/deploy.json:
# {
#   "photo_password_env_var": "BUNNYNET_PHOTO_PASSWORD",
#   "site_password_env_var": "BUNNYNET_SITE_PASSWORD",
#   "photo_zone_name": "your-site-photos",
#   "site_zone_name": "your-site-content",
#   "region": ""  # empty for Frankfurt, "uk" for London, "ny" for NY
# }
```

**Important**: When adding to shell profiles (`.bashrc`, `.zshrc`), use `export` to make variables available to child processes:

```bash
# In your shell profile
export BUNNYNET_PHOTO_PASSWORD="your-password"
export BUNNYNET_SITE_PASSWORD="your-password"
```

**Security Note**: Never commit these passwords to version control. Add them to your shell profile or deployment environment.

## Deployment Process

### Basic Deployment

```bash
# Deploy complete site (automatically runs build first)
uv run site deploy
```

The deploy command:
1. **Runs build pipeline**: Automatically calls `build` → `organize` → `validate`
2. **Routes files by type**:
   - `output/pics/*` → Photo storage zone
   - Everything else → Site content storage zone
3. **Uploads incrementally**: Only changed photos uploaded (based on manifest comparison)
4. **Uploads site content**: Always uploads all site files (smaller transfer)

**Note**: Due to build system behavior, deployments currently rebuild and re-upload site content even when source files haven't changed. Photo incremental uploads work correctly. This affects deployment speed but not functionality.

### Manual Build + Deploy

```bash
# Build first (if you want separate steps)
uv run site build

# Then deploy the built content
uv run site deploy
```

## How Dual Zone Routing Works

The deploy orchestrator automatically routes files based on path:

```
output/
├── pics/                    → Photo Zone (incremental)
│   ├── full/               → High-res images
│   └── thumb/              → Thumbnails
├── index.html              → Site Zone (full upload)
├── galleries/              → Site Zone (full upload)
└── static/                 → Site Zone (full upload)
```

### Verified Relative URL Generation

The build system correctly generates relative URLs that work with Edge Rules routing:

**Gallery pages generate**:
- Navigation links: `/galleries/wedding/`
- Full photo links: `/pics/full/wedding-20250809T132034-r5a.JPG`
- Thumbnail sources: `/galleries/wedding/thumbnails/wedding-20250809T132034-r5a.webp`

**File structure matches URLs**:
- Photos deployed to: `output/pics/full/` → Photo Zone
- Gallery pages deployed to: `output/galleries/` → Site Zone  
- Thumbnails embedded in gallery pages: `galleries/wedding/thumbnails/` → Site Zone

### Photo Zone Strategy
- **Incremental uploads**: Only uploads changed/new photos
- **Manifest tracking**: Uses SHA-256 hashes to detect changes
- **Optimized for large files**: Reduces deployment time for photo-heavy sites

### Site Zone Strategy
- **Full uploads**: Always uploads all site content
- **Optimized for small files**: HTML/CSS files are small, less optimization needed
- **Ensures consistency**: Guarantees all site files are current

## Configuration System

### Deploy Configuration (`config/deploy.json`)

The deploy system uses a flat configuration structure that specifies environment variable names and zone settings:

```json
{
  "photo_password_env_var": "BUNNYNET_PHOTO_PASSWORD",
  "site_password_env_var": "BUNNYNET_SITE_PASSWORD",
  "photo_zone_name": "your-site-photos",
  "site_zone_name": "your-site-content",
  "region": ""
}
```

### Dual Client Architecture

The deploy system creates two separate BunnyNetClient instances:
- **Photo Client**: Configured for the photo storage zone
- **Site Client**: Configured for the site content storage zone

Each client contains its zone name and uses the appropriate password from the environment variables specified in the configuration.

## Troubleshooting

### Environment Variable Issues

**Problem**: `Missing [ENV_VAR_NAME] environment variable`

**Solution**: Check your `config/deploy.json` and ensure the specified environment variables are set:

```bash
# Check current config
cat config/deploy.json

# Set the variables it expects
export BUNNYNET_PHOTO_PASSWORD="your-photo-password"
export BUNNYNET_SITE_PASSWORD="your-site-password"
```

### API Connection Issues

**Test connectivity**:
```bash
python3 -c "from deploy.bunnynet_client import create_clients_from_config; import json; config = json.load(open('config/deploy.json')); photo_client, site_client = create_clients_from_config(config); print('Photo zone:', photo_client.base_url); print('Site zone:', site_client.base_url)"
```

**Common issues**:
- Wrong password → Check storage zone password in Bunny.net dashboard
- Wrong zone name → Verify exact zone name (case-sensitive)
- Network issues → Check firewall/proxy settings

### Build Directory Missing

**Error**: `Output directory not found - run build first`

**Solution**: 
```bash
uv run site build  # This will create the output/ directory
uv run site deploy
```

## Performance Considerations

### Photo Optimization
- Large photo collections benefit most from incremental uploads
- Initial deployment uploads all photos
- Subsequent deployments only upload changed photos

### Site Content
- HTML/CSS files are always uploaded (full sync)
- Small file size makes full upload acceptable
- Ensures consistency across deployments

## Security Best Practices

1. **Never log storage passwords**: Code never inspects environment variable values
2. **Use separate zones**: Isolates photo and site content permissions
3. **Rotate passwords regularly**: Update storage zone passwords periodically
4. **Monitor access logs**: Check Bunny.net dashboard for unexpected access

## Future Enhancements

- **Configurable routing rules**: Custom file type → zone mappings
- **Rollback functionality**: Automated rollback on partial deployment failures
- **Progress indicators**: Real-time upload progress for large deployments
- **Multiple region support**: Deploy to different regions per zone

## Related Documentation

- [Deploy Command Usage](commands/deploy.md)
- [Build Pipeline](commands/build.md)
- [Site Configuration](config/)