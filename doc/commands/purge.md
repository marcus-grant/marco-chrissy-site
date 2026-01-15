# Purge Command

Purge CDN cache to immediately invalidate cached content.

## Synopsis

```bash
uv run site purge
```

## Description

The `purge` command clears the CDN cache for the site pullzone. This forces edge servers to fetch fresh content from the origin storage zone on the next request.

### When to Use

- After deploying breaking changes (CSS/JS updates that must be visible immediately)
- When fixing critical content errors
- For coordinated releases where multiple changes need to go live together

### What It Does

1. Loads deploy configuration from `config/deploy.json`
2. Reads CDN API credentials from environment variables
3. Calls Bunny.net API to purge the entire site pullzone cache
4. Reports success or failure

## Configuration

### Required Configuration Fields

In `config/deploy.json`:
```json
{
  "cdn_api_key_env_var": "BUNNYNET_CDN_API_KEY",
  "site_pullzone_id_env_var": "BUNNYNET_SITE_PULLZONE_ID"
}
```

### Required Environment Variables

```bash
export BUNNYNET_CDN_API_KEY="your-account-api-key"
export BUNNYNET_SITE_PULLZONE_ID="your-pullzone-id"
```

The API key is your Bunny.net Account API key (found in Account Settings → API). The pullzone ID is visible in the Pull Zone details in the CDN section.

## Examples

### Standalone Purge

```bash
# Purge cache after manual changes
uv run site purge
```

### Deploy with Purge

```bash
# Deploy and purge in one command
uv run site deploy --purge
```

This is equivalent to running `deploy` followed by `purge`, but more convenient.

## Output

### Successful Purge

```
Purging CDN cache...
✓ CDN cache purged successfully!
```

### Failed Purge

```
Purging CDN cache...
✗ CDN cache purge failed
```

## Error Handling

### Missing Configuration

```
✗ Configuration not found: config/deploy.json
```

**Solution**: Ensure `config/deploy.json` exists with required CDN fields.

### Missing Environment Variables

```
✗ Configuration error: Missing BUNNYNET_CDN_API_KEY environment variable
```

**Solution**: Set the environment variable specified in your configuration.

### API Failure

```
✗ Purge failed: <error details>
```

**Solution**: Check your API key validity and network connectivity.

## Scope

The purge command currently clears the **site pullzone only**. The photos pullzone is excluded because:

- Photo content rarely changes
- Photos have longer cache TTLs
- Purging photos would cause unnecessary origin fetches

## Related Commands

- [`deploy`](deploy.md) - Deploy site with optional `--purge` flag
- [`build`](build.md) - Build the complete site

## Related Documentation

- [Bunny.net Setup Guide](../bunnynet.md)
- [Configuration System](../configuration.md)
