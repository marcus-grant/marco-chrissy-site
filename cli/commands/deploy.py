"""Deploy command implementation."""

import os
from pathlib import Path

import click

from deploy.bunnynet_client import create_client_from_env
from deploy.manifest_comparator import ManifestComparator
from deploy.orchestrator import DeployOrchestrator

from .build import build


@click.command()
def deploy():
    """Upload site to Bunny CDN with dual zone strategy."""
    click.echo("Deploying site to Bunny CDN...")

    # Run build first (cascading pattern)
    click.echo("Running build...")
    ctx = click.get_current_context()
    result = ctx.invoke(build)

    if result and hasattr(result, "exit_code") and result.exit_code != 0:
        click.echo("✗ Build failed - stopping deploy")
        ctx.exit(1)

    # Execute deployment using orchestrator
    click.echo("Uploading to CDN with dual zone strategy...")
    try:
        # Initialize deployment components
        bunnynet_client = create_client_from_env()
        manifest_comparator = ManifestComparator()

        # Read zone names from environment variables
        photo_zone_name = os.getenv("BUNNYNET_PHOTO_ZONE_NAME")
        site_zone_name = os.getenv("BUNNYNET_SITE_ZONE_NAME")

        if not photo_zone_name:
            click.echo("✗ Missing BUNNYNET_PHOTO_ZONE_NAME environment variable")
            ctx.exit(1)

        if not site_zone_name:
            click.echo("✗ Missing BUNNYNET_SITE_ZONE_NAME environment variable")
            ctx.exit(1)

        orchestrator = DeployOrchestrator(
            bunnynet_client,
            manifest_comparator,
            photo_zone_name=photo_zone_name,
            site_zone_name=site_zone_name
        )

        # Execute deployment
        output_dir = Path("output")

        if not output_dir.exists():
            click.echo("✗ Output directory not found - run build first")
            ctx.exit(1)

        success = orchestrator.execute_deployment(output_dir)

        if success:
            click.echo("✓ Deploy completed successfully!")
        else:
            click.echo("✗ Deploy failed")
            ctx.exit(1)

    except Exception as e:
        click.echo(f"✗ Deploy failed: {e}")
        ctx.exit(1)
