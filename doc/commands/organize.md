# Organize Command

## Overview

The organize command orchestrates NormPic photo organization, preparing source photos for gallery generation. It implements idempotent behavior - if photos are already organized, it skips the operation.

## Usage

```bash
uv run site organize
uv run site organize --benchmark
```

### Options

- `--benchmark`: Output timing metrics for performance analysis

## Functionality

The organize command:

1. **Runs validation first** (cascading pattern calls `validate`)
2. **Checks idempotency** - Skips if photos already organized
3. **Orchestrates NormPic** - Runs the photo organization tool
4. **Reports results** - Shows processed photo count and manifest path

## Command Pipeline Position

The organize command sits in the middle of the cascading pipeline:
```
deploy → build → organize → validate
```

When called directly, it automatically runs validation. When called by `build` or `deploy`, it processes photos before those commands proceed.

## Idempotent Behavior

The organize command checks if photos are already organized before running:

```
✓ Photos are already organized, skipping...
Organization completed successfully!
```

This prevents redundant processing on repeated runs.

## Output Examples

### First Run (Processing Required)
```
Running photo organization...
Running validation checks...
✓ Config files found
✓ Dependencies available
✓ Permissions verified
Validation completed successfully!
Orchestrating NormPic tool...
✓ NormPic organization completed successfully!
  Processed 645 photos
  Generated manifest: pics/manifest.json
Organization completed successfully!
```

### Subsequent Runs (Already Organized)
```
Running photo organization...
Running validation checks...
Validation completed successfully!
✓ Photos are already organized, skipping...
Organization completed successfully!
```

### With Benchmark Flag
```
uv run site organize --benchmark
...
Organization completed successfully!
Benchmark: organize duration 2.345 seconds
```

## Architecture

The organize command uses the `NormPicOrganizer` class:

- **Location**: `organizer/normpic.py`
- **Responsibility**: Wrapper for NormPic tool integration
- **Returns**: `OrganizeResult(success, pics_processed, manifest_path, errors)`

### Key Methods

- `is_already_organized()` - Check if organization can be skipped
- `organize_photos()` - Execute NormPic organization

## Configuration

The organize command reads configuration from `config/normpic.json`:

```json
{
  "source_dir": "pics/source",
  "manifest_path": "pics/manifest.json"
}
```

## Exit Codes

- **0**: Organization successful (or skipped if already organized)
- **1**: Organization failed or validation errors

## Troubleshooting

### NormPic Not Found
- Ensure `normpic` is installed: `uv sync`
- Check it's in the dependency list

### Organization Fails
- Verify source photo directory exists
- Check file permissions on source and output directories
- Review NormPic error messages in output

### Repeated Processing
- If photos keep re-processing, check the manifest file
- Verify `is_already_organized()` logic matches your setup
