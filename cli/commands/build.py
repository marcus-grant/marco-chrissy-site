"""Build command implementation."""

import os

import click

from build.benchmark import TimingContext
from build.exceptions import BuildError
from build.orchestrator import BuildOrchestrator

from .organize import organize


@click.command()
@click.option("--benchmark", is_flag=True, help="Output timing metrics for benchmarking")
def build(benchmark: bool):
    """Build the complete site with galleries and pages."""
    click.echo("Building site...")

    timer = TimingContext() if benchmark else None
    if timer:
        timer.__enter__()

    # Run organize first (cascading pattern)
    click.echo("Running organization...")
    ctx = click.get_current_context()
    result = ctx.invoke(organize)

    if result and hasattr(result, "exit_code") and result.exit_code != 0:
        click.echo("✗ Organize failed - stopping build")
        ctx.exit(1)

    # Execute complete build using orchestrator
    click.echo("Generating galleries and site pages...")
    try:
        orchestrator = BuildOrchestrator()
        orchestrator.execute()
        click.echo("✓ Build completed successfully!")

        if timer:
            timer.__exit__(None, None, None)
            click.echo(f"Benchmark: build duration {timer.duration_s:.3f} seconds")

    except BuildError as e:
        click.echo(f"✗ Build failed: {e}")
        ctx.exit(1)


def _is_already_built(output_dir="output"):
    """Check if site is already built and up to date."""
    # Simple check for key output files existence
    # Note: Don't check for index.html as Pelican manages that file
    output_paths = [f"{output_dir}/galleries"]

    return all(os.path.exists(path) for path in output_paths)
