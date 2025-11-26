"""Main CLI entry point for site command."""

import click

from .commands.build import build
from .commands.deploy import deploy
from .commands.organize import organize
from .commands.validate import validate


@click.group()
def main():
    """Site build and deployment command system."""
    pass


# Register commands
main.add_command(validate)
main.add_command(organize)
main.add_command(build)
main.add_command(deploy)


if __name__ == "__main__":
    main()
