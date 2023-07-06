"""Command-line interface for enforce_notebook_run_order"""

from typing import List
import warnings
import click
from .enforce_notebook_run_order import process_path


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=False)
@click.option(
    "--no-run",
    is_flag=True,
    help="Do not run the notebooks, only check the run order. "
    "This may miss some errors, but is useful for extremely long running notebooks. "
    "If you use this option, you should consider moving the long-running code to a "
    "separate task that runs separately from the notebook.",
)
@click.option(
    "--allow-not-run-notebook",
    is_flag=True,
    help="Allow notebooks with only unrun cells to pass.",
)
def cli(
    paths: List[str] = None, no_run: bool = False, allow_not_run_notebook: bool = False
):
    """
    Checks the run order of notebooks in the specified paths,
    or the entire repo if no paths are specified

    Args:
        paths: The paths to check. If no paths are specified, the current directory is checked.
        no_run: If True, the notebooks will not be run. This may miss some errors, but is useful
    """
    if no_run:
        warnings.warn(
            "The --no-run option will not catch all problems with notebooks. "
            "It is possible that the checks will pass, but the notebook was still run "
            "out of order. It is highly recommended to move any long-running code to a separate "
            "task that runs separately from the notebook."
        )

    if paths:
        for path in paths:
            process_path(path, no_run, allow_not_run_notebook)
    else:
        # If no paths are provided, check the current directory
        process_path(".", no_run, allow_not_run_notebook)
