# Deploy Command

Deploy the generated site to Bunny.net CDN with dual storage zone strategy.

## Synopsis

```bash
uv run site deploy
```

## Description

The `deploy` command uploads your built site to Bunny.net CDN using a dual storage zone strategy that separates photos from site content for optimal performance.

### Automatic Build Cascade

The deploy command follows the cascading pattern and automatically runs the build pipeline:

```
deploy → build → organize → validate
```

If any step in the cascade fails, the deploy process stops.

### Dual Zone Strategy

The deploy command routes files to separate storage zones:

- **Photo Zone**: All files in `output/pics/` (photos and thumbnails)
  - Uses manifest-based incremental uploads
  - Only uploads changed/new files based on SHA-256 comparison
  - Optimized for large photo collections

- **Site Zone**: All other content (HTML, CSS, galleries)
  - Uses full upload strategy 
  - Always uploads all site content files
  - Ensures consistency across deployments

## Configuration

### Required Configuration Files

1. **Deploy Configuration** (`config/deploy.json`):
   ```json
   {
     "photo_password_env_var": "BUNNYNET_PHOTO_PASSWORD",
     "site_password_env_var": "BUNNYNET_SITE_PASSWORD", 
     "photo_zone_name": "your-site-photos",
     "site_zone_name": "your-site-content",
     "region": ""
   }
   ```

2. **Environment Variables**:
   ```bash
   export BUNNYNET_PHOTO_PASSWORD="your-photo-zone-password"
   export BUNNYNET_SITE_PASSWORD="your-site-zone-password"
   ```

### Customizing Environment Variable Names

The configuration system allows you to use any environment variable names by updating `config/deploy.json`:

```json
{
  "photo_password_env_var": "MY_CUSTOM_PHOTO_VAR",
  "site_password_env_var": "MY_CUSTOM_SITE_VAR",
  "region": "uk"
}
```

## Examples

### Basic Deployment

```bash
# Deploy complete site (runs build automatically)
uv run site deploy
```

### Manual Step-by-Step

```bash
# Build first (validate → organize → build)
uv run site build

# Then deploy the built content
uv run site deploy
```

### Different Regions

Configure region in `config/deploy.json`:
```json
{
  "region": "uk"  // London region
}
```

Available regions:
- `""` (empty): Frankfurt (default)
- `"uk"`: London
- `"ny"`: New York

**Note**: This affects the primary storage region. Zone replication (multiple regions per zone) is configured separately in the Bunny.net dashboard and doesn't require code changes.

## Output

The deploy command shows progress information:

```
Deploying site to Bunny CDN...
Running build...
✓ Build completed successfully
Uploading to CDN with dual zone strategy...
✓ Uploaded 45 site files to site zone
✓ Uploaded 12 new photos to photo zone (skipped 234 unchanged)
✓ Deploy completed successfully!
```

## Error Handling

### Missing Environment Variables

```
✗ Missing BUNNYNET_PHOTO_PASSWORD environment variable
```

**Solution**: Set the environment variable specified in your `config/deploy.json`.

### Build Failure

```
✗ Build failed - stopping deploy
```

**Solution**: Fix build issues before retrying deploy. The build cascade ensures only successful builds are deployed.

### Upload Failures

```
✗ Deploy failed: Upload to photo zone failed
```

**Solution**: Check network connectivity and storage zone credentials.

## Performance Notes

### Photo Collections

- **First deploy**: Uploads all photos (can be slow for large collections)
- **Subsequent deploys**: Only uploads changed photos (much faster)
- **Manifest tracking**: Uses SHA-256 hashes to detect changes efficiently

**Build Behavior**: The build step currently regenerates all site content even when source files haven't changed, causing site content to be re-uploaded on every deploy. This affects deployment time but not correctness.

### Site Content

- **Always full upload**: Ensures site consistency
- **Small file optimization**: HTML/CSS files are typically small
- **Fast upload**: Site content uploads quickly compared to photos

## Security

- Environment variables are read but never logged or exposed
- Each storage zone has separate credentials for isolation
- Configurable environment variable names prevent credential conflicts

## Related Commands

- [`build`](build.md) - Build the complete site
- [`organize`](organize.md) - Organize source photos
- [`validate`](validate.md) - Validate site configuration

## Related Documentation

- [Bunny.net Setup Guide](../bunnynet.md)
- [Configuration System](../configuration.md)
- [Build Pipeline](../build-system.md)