"""Forces notebooks to run cells sequentially and fails if cells were run out of order"""

import os
import pathlib
from . import temp_notebook
from . import utils


class NotebookCodeCellNotRunError(Exception):
    """Raised when a notebook code cell was not run"""


class NotebookRunOrderError(Exception):
    """Raised when a notebook is run out of order"""


class InvalidNotebookRunError(Exception):
    """Raised when any problems were identified with a notebook's run order"""


def notebook_is_in_virtualenv(notebook_path: pathlib.Path) -> bool:
    """
    Checks whether a notebook is in the current repo or is in the virtual environment's
    site-packages directory.

    Some dependencies may contain Jupyter notebooks in their site-packages directory for
    testing or documentation purposes. These notebooks should not be checked for run order.

    Args:
        notebook_path (pathlib.Path): Path to the notebook file.

    Returns:
        bool: True if the notebook is in the virtual environment's site-packages directory.
    """
    # if the notebook_path contains "site-packages", it is in the virtual environment
    # and should not be checked
    return "site-packages" in str(notebook_path)


def check_notebook_run_order(
    notebook_data: dict, allow_not_run_notebook: bool = False
) -> None:
    """
    Checks that the notebook cells were run sequentially and fails if not.

    Args:
        notebook_data (dict): Notebook data in dictionary format.
        allow_not_run_notebook (bool, optional): If True, allow notebooks
        with only unrun cells to pass. Defaults to False.

    Raises:
        NotebookCodeCellNotRunError: If a code cell in the notebook was not run.
        NotebookRunOrderError: If the cells in the notebook were not run sequentially.
    """
    previous_cell_number = 0
    code_cells = utils.get_code_cells(notebook_data)
    for cell in code_cells:
        current_cell_number = cell["execution_count"]
        if current_cell_number is None:
            if allow_not_run_notebook and previous_cell_number == 0:
                continue
            raise NotebookCodeCellNotRunError(
                f"Code cell was not run. The previous cell was #{previous_cell_number}. \n\n"
                f"Cell contents: \n\n> {cell}"
            )
        if current_cell_number != previous_cell_number + 1:
            raise NotebookRunOrderError(
                "Cells were not run sequentially. "
                f"The cell that caused this error is #{current_cell_number} "
                f"and the previous cell was #{previous_cell_number}. \n\n"
                f"Cell contents: \n\n> {cell}"
            )
        previous_cell_number = current_cell_number


def check_single_notebook(
    notebook_path: str, no_run: bool = False, allow_not_run_notebook: bool = False
):
    """Check a single notebook

    Args:
        notebook_path (str): Path to the notebook file.
        no_run (bool, optional): If True, do not run the notebook. Defaults to False.
        allow_not_run_notebook (bool, optional): If True, allow notebooks
        with only unrun cells to pass. Defaults to False.

    Raises:
        InvalidNotebookRunError: If any problems were identified with the notebook's run order.
    """
    notebook_path = pathlib.Path(notebook_path)
    notebook_data = utils.load_notebook_data(notebook_path)
    try:
        check_notebook_run_order(notebook_data, allow_not_run_notebook)
        if not no_run:
            with temp_notebook.TempNotebook(notebook_path) as temp_nb:
                temp_nb.check_notebook()
    except (
        NotebookCodeCellNotRunError,
        NotebookRunOrderError,
        temp_notebook.NotebookRunFailedError,
        temp_notebook.CellOutputMismatchError,
    ) as error:
        raise InvalidNotebookRunError(
            f"Notebook {notebook_path} was not run in order.\n\n{error}\n\n"
        ) from error
    print(f"Notebook {notebook_path} was run correctly.")


def process_path(path: str, no_run: bool = False, allow_not_run_notebook: bool = False):
    """
    Processes a single path. Raises an exception if the path is invalid

    Args:
        path (str): Path to the notebook file or directory.
        no_run (bool, optional): If True, do not run the notebook. Defaults to False.
        allow_not_run_notebook (bool, optional): If True, allow notebooks
        with only unrun cells to pass. Defaults to False.

    Raises:
        ValueError: If the path is invalid.
    """

    if os.path.isdir(path):
        # Get all .ipynb files in the directory and its subdirectories
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                notebok_path = pathlib.Path(dirpath) / filename
                if filename.endswith(".ipynb") and not notebook_is_in_virtualenv(
                    notebok_path
                ):
                    check_single_notebook(
                        os.path.join(dirpath, filename),
                        no_run=no_run,
                        allow_not_run_notebook=allow_not_run_notebook,
                    )
    elif path.endswith(".ipynb"):
        check_single_notebook(
            path,
            no_run=no_run,
            allow_not_run_notebook=allow_not_run_notebook,
        )
    else:
        raise ValueError(
            f"Cannot check file {path}. "
            "Must be a path to a notebook file with the .ipynb extension, or a directory."
        )
