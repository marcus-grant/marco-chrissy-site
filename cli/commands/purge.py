"""Purge command implementation."""

import click

from build.config_manager import ConfigManager
from deploy.bunny_cdn_client import create_cdn_client_from_config


@click.command()
def purge():
    """Purge CDN cache for site pullzone."""
    click.echo("Purging CDN cache...")

    try:
        # Load deploy configuration
        config_manager = ConfigManager()
        deploy_config = config_manager.load_deploy_config()

        # Create CDN client and purge
        cdn_client = create_cdn_client_from_config(deploy_config)
        success = cdn_client.purge_pullzone()

        if success:
            click.echo("✓ CDN cache purged successfully!")
        else:
            click.echo("✗ CDN cache purge failed")
            raise SystemExit(1)

    except FileNotFoundError as e:
        click.echo(f"✗ Configuration not found: {e}")
        raise SystemExit(1) from None

    except ValueError as e:
        click.echo(f"✗ Configuration error: {e}")
        raise SystemExit(1) from None

    except Exception as e:
        click.echo(f"✗ Purge failed: {e}")
        raise SystemExit(1) from None
