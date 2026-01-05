"""Deploy command implementation."""

from pathlib import Path

import click

from build.config_manager import ConfigManager
from deploy.bunnynet_client import create_clients_from_config
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
        # Load deploy configuration
        config_manager = ConfigManager()
        deploy_config = config_manager.get_deploy_config()

        # Initialize deployment components
        photo_client, site_client = create_clients_from_config(deploy_config)
        manifest_comparator = ManifestComparator()

        orchestrator = DeployOrchestrator(
            photo_client,
            site_client,
            manifest_comparator
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
