"""Deploy command implementation."""

import click


@click.command()
def deploy():
    """Upload site to Bunny CDN."""
    click.echo("Deploy command - not yet implemented")
