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

### 3. Create a Pull Zone

A pull zone is required for CDN distribution and cache purging.

1. Navigate to **CDN** → **Pull Zones**
2. Click **Add Pull Zone**
3. Configure:
   - **Name**: `your-site` (e.g., `mycompany-site`)
   - **Origin URL**: Point to your site storage zone URL
4. Click **Create**
5. **Important**: Note the **Pull Zone ID** from the URL or zone details

### 4. Get Your Account API Key

The Account API key is required for CDN operations like cache purging.

1. Click your profile icon (top right)
2. Navigate to **Account Settings** → **API**
3. Copy your **Account API Key**

**Security Note**: The Account API key provides full access to your Bunny.net account. Keep it secure and never commit it to version control.

### 5. Configure Environment Variables

Each storage zone has its own unique password. The deploy configuration system reads environment variable names from `config/deploy.json`, allowing you to customize variable names:

```bash
# Configure your environment variables based on config/deploy.json settings
# Example configuration:
export BUNNYNET_PHOTO_PASSWORD="your-photo-zone-password"
export BUNNYNET_SITE_PASSWORD="your-site-zone-password"

# CDN API credentials for cache purging:
export BUNNYNET_CDN_API_KEY="your-account-api-key"
export BUNNYNET_SITE_PULLZONE_ID="your-pullzone-id"

# The deploy config determines which env vars to read:
# config/deploy.json:
# {
#   "photo_password_env_var": "BUNNYNET_PHOTO_PASSWORD",
#   "site_password_env_var": "BUNNYNET_SITE_PASSWORD",
#   "cdn_api_key_env_var": "BUNNYNET_CDN_API_KEY",
#   "site_pullzone_id_env_var": "BUNNYNET_SITE_PULLZONE_ID",
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
export BUNNYNET_CDN_API_KEY="your-api-key"
export BUNNYNET_SITE_PULLZONE_ID="your-pullzone-id"
```

**Security Note**: Never commit these credentials to version control. Add them to your shell profile or deployment environment.

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

### Deploy with Cache Purge

To automatically purge CDN cache after deployment:

```bash
# Deploy and purge cache in one command
uv run site deploy --purge
```

This is useful when you need changes to appear immediately without waiting for cache TTL expiration.

## CDN Cache Purging

CDN caching improves performance but can delay visibility of updates. Use cache purging to invalidate cached content when immediate updates are needed.

### When to Purge

- **Breaking changes**: CSS/JS updates that must be visible immediately
- **Critical fixes**: Security patches or important content corrections
- **Coordinated releases**: When multiple changes need to go live together

### Purge Commands

```bash
# Standalone purge (site pullzone only)
uv run site purge

# Deploy with automatic purge
uv run site deploy --purge
```

### How It Works

The purge command uses Bunny.net's CDN API to invalidate the entire pullzone cache:

1. Reads CDN API credentials from environment variables
2. Calls Bunny.net API endpoint: `POST /pullzone/{id}/purgeCache`
3. Bunny.net returns 204 on success, indicating cache cleared

**Scope**: Currently purges the site pullzone only. Photos pullzone is excluded because photo content rarely changes and has longer cache TTLs.

### Future Purge Features

The Bunny.net API supports more granular purging options (not yet implemented):

**URL-specific purging**:
```
POST https://api.bunny.net/purge?url=https://yoursite.b-cdn.net/path/to/file.html
```

**Wildcard patterns**:
```
POST https://api.bunny.net/purge?url=https://yoursite.b-cdn.net/galleries/*
```

**Tag-based purging** (requires cache tags on responses):
```
POST https://api.bunny.net/pullzone/{id}/purgeCache
Body: { "CacheTag": "galleries" }
```

These features may be implemented based on usage patterns and need.

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

### Edge Rules Redirect Strategy

**Initial Setup (302 Temporary Redirects)**:
- Edge Rule: `/pics/full/*` → `302 Temporary` → `https://[photo-zone].b-cdn.net/full/$1`
- Use 302 initially to allow testing and easy rollback if needed
- Monitor production for several days to ensure all URLs redirect correctly

**Production Transition (301 Permanent Redirects)**:
- After confirming 302s work correctly, change to `301 Permanent`
- Benefits: Better SEO ranking, client-side browser caching, reduced server load
- Considerations: Harder to rollback, browsers cache 301s more aggressively

**Deployment Order**:
1. Deploy code with relative URLs (safe with existing 302 Edge Rules)
2. Monitor 302 redirects in production
3. Change Edge Rules from 302 → 301 after confirming stability

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
  "cdn_api_key_env_var": "BUNNYNET_CDN_API_KEY",
  "site_pullzone_id_env_var": "BUNNYNET_SITE_PULLZONE_ID",
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
export BUNNYNET_CDN_API_KEY="your-api-key"
export BUNNYNET_SITE_PULLZONE_ID="your-pullzone-id"
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

### CDN Cache Purge Issues

**Problem**: `CDN cache purge failed`

**Possible causes**:
- Invalid API key → Verify Account API key in Bunny.net dashboard
- Wrong pullzone ID → Check Pull Zone ID in CDN section
- Network issues → Check firewall/proxy settings

**Problem**: `CDN purge configuration error: Missing [ENV_VAR] environment variable`

**Solution**: Set CDN environment variables:
```bash
export BUNNYNET_CDN_API_KEY="your-account-api-key"
export BUNNYNET_SITE_PULLZONE_ID="your-pullzone-id"
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
- [Purge Command Usage](commands/purge.md)
- [Build Pipeline](commands/build.md)
- [Site Configuration](config/)