#!/usr/bin/env python3
"""Profiler script to debug the infinite loop."""

import cProfile
import sys
from pathlib import Path

# Add the project to path
sys.path.insert(0, str(Path(__file__).parent))

def run_galleria():
    """Run galleria generate with profiling."""
    from galleria.__main__ import cli

    # Set up the command arguments
    sys.argv = ['galleria', 'generate', '--config', 'config/galleria.json', '--verbose']

    # Run the CLI
    cli()

if __name__ == "__main__":
    print("Starting profiler...")
    cProfile.run('run_galleria()', 'profile_output.prof')
    print("Profiling complete.")
