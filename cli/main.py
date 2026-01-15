"""Main CLI entry point for site command."""

import click

from .commands.benchmark import benchmark
from .commands.build import build
from .commands.deploy import deploy
from .commands.organize import organize
from .commands.purge import purge
from .commands.serve import serve
from .commands.validate import validate


@click.group()
def main():
    """Site build and deployment command system."""
    pass


# Register commands
main.add_command(validate)
main.add_command(organize)
main.add_command(build)
main.add_command(serve)
main.add_command(deploy)
main.add_command(purge)
main.add_command(benchmark)


if __name__ == "__main__":
    main()
