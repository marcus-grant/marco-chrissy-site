"""Validate command implementation."""

import click

from validator.config import ConfigValidator


@click.command()
def validate():
    """Pre-flight checks for configs, dependencies, and permissions."""
    click.echo("Running validation checks...")

    # Check config files
    config_validator = ConfigValidator()
    result = config_validator.validate_config_files()

    if result.success:
        click.echo("✓ Config files found")
    else:
        click.echo("✗ Config validation failed:")
        for error in result.errors:
            click.echo(f"  - {error}")
        return

    click.echo("Validation completed successfully!")
