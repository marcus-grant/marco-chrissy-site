"""Validate command implementation."""

import sys

import click

from validator.config import ConfigValidator
from validator.dependencies import DependencyValidator
from validator.permissions import PermissionValidator


@click.command()
def validate():
    """Pre-flight checks for configs, dependencies, and permissions."""
    click.echo("Running validation checks...")

    # Check config files
    config_validator = ConfigValidator()
    config_result = config_validator.validate_config_files()

    if config_result.success:
        click.echo("✓ Config files found")
    else:
        click.echo("✗ Config validation failed:")
        for error in config_result.errors:
            click.echo(f"  - {error}")
        sys.exit(1)

    # Check dependencies
    dependency_validator = DependencyValidator()
    dep_result = dependency_validator.validate_dependencies()

    if dep_result.success:
        click.echo("✓ Dependencies available")
    else:
        click.echo("✗ Dependency validation failed:")
        for error in dep_result.errors:
            click.echo(f"  - {error}")
        sys.exit(1)

    # Check permissions
    permission_validator = PermissionValidator()
    perm_result = permission_validator.validate_output_permissions()

    if perm_result.success:
        click.echo("✓ Permissions verified")
    else:
        click.echo("✗ Permission validation failed:")
        for error in perm_result.errors:
            click.echo(f"  - {error}")
        sys.exit(1)

    click.echo("Validation completed successfully!")
