"""tests the enforce_notebook_run_order module"""

import os
from click.testing import CliRunner
import pytest
from enforce_notebook_run_order import enforce_notebook_run_order
from enforce_notebook_run_order.cli import cli

# pylint: disable=redefined-outer-name


@pytest.fixture
def valid_notebook_data():
    """Returns valid test notebook json."""
    return {
        "cells": [
            {"cell_type": "code", "execution_count": 1},
            {"cell_type": "code", "execution_count": 2},
            {"cell_type": "code", "execution_count": 3},
        ]
    }


@pytest.fixture
def out_of_order_notebook_data():
    """Returns invalid test notebook json."""
    return {
        "cells": [
            {"cell_type": "code", "execution_count": 1},
            {"cell_type": "code", "execution_count": 3},
            {"cell_type": "code", "execution_count": 2},
        ]
    }


@pytest.fixture
def notebook_cell_not_run_data():
    """Returns invalid test notebook json."""
    return {
        "cells": [
            {"cell_type": "code", "execution_count": 1},
            {"cell_type": "code", "execution_count": 2},
            {"cell_type": "code", "execution_count": None},
        ]
    }


@pytest.fixture
def notebook_all_cell_not_run_data():
    """Returns valid, with --allow-not-run-notebook=true, test notebook json."""
    return {
        "cells": [
            {"cell_type": "code", "execution_count": None},
            {"cell_type": "code", "execution_count": None},
            {"cell_type": "code", "execution_count": None},
        ]
    }


def test_check_notebook_run_order_valid(valid_notebook_data):
    """Tests that valid notebook data does not raise an error."""
    enforce_notebook_run_order.check_notebook_run_order(valid_notebook_data)


def test_check_notebook_run_order_out_of_order(out_of_order_notebook_data):
    """Tests that out of order notebook data raises an error."""
    with pytest.raises(enforce_notebook_run_order.NotebookRunOrderError) as error:
        enforce_notebook_run_order.check_notebook_run_order(out_of_order_notebook_data)

    expected_error_message = (
        "Cells were not run sequentially. "
        "The cell that caused this error is #3 "
        "and the previous cell was #1. \n\n"
        "Cell contents: \n\n> {'cell_type': 'code', 'execution_count': 3}"
    )
    assert str(error.value) == expected_error_message


def test_check_notebook_run_order_cell_not_run(notebook_cell_not_run_data):
    """Tests that a notebook cell not run raises an error."""
    with pytest.raises(enforce_notebook_run_order.NotebookCodeCellNotRunError) as error:
        enforce_notebook_run_order.check_notebook_run_order(notebook_cell_not_run_data)

    expected_error_message = (
        "Code cell was not run. The previous cell was #2. \n\n"
        "Cell contents: \n\n> {'cell_type': 'code', 'execution_count': None}"
    )
    assert str(error.value) == expected_error_message


def test_check_notebook_run_order_all_cell_not_run(notebook_all_cell_not_run_data):
    """
    Tests that notebook with all cells not run does not raise an error,
    with --allow-not-run-notebook=true.
    """
    enforce_notebook_run_order.check_notebook_run_order(
        notebook_all_cell_not_run_data, True
    )


def test_notebook_is_in_virtualenv():
    """Tests that notebook_is_in_virtualenv returns True when in a virtualenv."""
    assert enforce_notebook_run_order.notebook_is_in_virtualenv(
        ".venv/lib/python3.8/site-packages/nbclient/tests/files/Empty Cell.ipynb"
    )
    assert not enforce_notebook_run_order.notebook_is_in_virtualenv(
        "notebooks/Empty Cell.ipynb"
    )


def test_process_path_valid(mocker):
    """
    Tests that check_notebook_run_order is called correctly
    for each notebook in a given folder.
    """
    mock_check_notebook_run_order = mocker.patch(
        "enforce_notebook_run_order.enforce_notebook_run_order.check_notebook_run_order"
    )

    test_data_dir = os.path.join(
        "test", "test_data", "enforce_notebook_run_order_valid"
    )

    enforce_notebook_run_order.process_path(test_data_dir)

    assert mock_check_notebook_run_order.call_count == 2


def test_process_path_invalid():
    """
    Tests that check_notebook_run_order raises InvalidNotebookRunError
    for each notebook in a given folder.
    """
    test_data_dir = os.path.join(
        "test", "test_data", "enforce_notebook_run_order_invalid"
    )

    with pytest.raises(enforce_notebook_run_order.InvalidNotebookRunError):
        enforce_notebook_run_order.process_path(test_data_dir)


def test_process_path_ignores_virtualenv(mocker):
    """
    Tests that check_notebook_run_order is not called for notebooks
    in a virtualenv.
    """
    mock_check_notebook_run_order = mocker.patch(
        "enforce_notebook_run_order.enforce_notebook_run_order.check_notebook_run_order"
    )

    test_data_dir = os.path.join(
        "test",
        "test_data",
        "test_virtual_environment",
        "test_lib",
        "python3.x",
        "site-packages",
        "testpackage",
        "tests",
        "test_data",
    )

    enforce_notebook_run_order.process_path(test_data_dir)

    assert mock_check_notebook_run_order.call_count == 0


def test_process_path_invalid_notebook_path():
    """Tests that the CLI raises an error when given a file that is not an ipynb."""
    with pytest.raises(ValueError):
        enforce_notebook_run_order.process_path("test/test_data/invalid_notebook.py")


def test_cli_valid_notebook_path_valid_notebook():
    """Tests that the CLI returns 0 when given a valid notebook path."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "test/test_data/enforce_notebook_run_order_valid/valid_notebook.ipynb",
        ],
    )
    assert result.exit_code == 0


def test_cli_valid_notebook_path_invalid_notebook():
    """Tests that the CLI returns 1 when given an invalid notebook path."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "test/test_data/enforce_notebook_run_order_invalid/test_subdirectory/"
            "invalid_subdirectory_notebook.ipynb",
        ],
    )
    assert result.exit_code == 1


def test_cli_valid_notebook_dir_valid_notebooks():
    """Tests that the CLI returns 0 when given a valid notebook_dir."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "test/test_data/enforce_notebook_run_order_valid",
        ],
    )
    assert result.exit_code == 0


def test_cli_no_paths_searches_entire_dir(mocker):
    """
    Tests that the CLI searches the entire current directory if no paths are specified.
    """
    mock_process_path = mocker.patch("enforce_notebook_run_order.cli.process_path")

    runner = CliRunner()
    result = runner.invoke(cli)

    # The process_path function should be called once, with the current directory as its argument
    mock_process_path.assert_called_once_with(".", False, False)

    assert result.exit_code == 0


def test_cli_no_run_option(mocker):
    """
    Tests that process_path is called with the correct run option
    when the --no-run option is specified, and a warning was was printed
    """
    mock_process_path = mocker.patch("enforce_notebook_run_order.cli.process_path")

    mock_warning = mocker.patch("warnings.warn")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "test/test_data/enforce_notebook_run_order_valid",
            "--no-run",
        ],
    )

    # The process_path function should be called once, with the current directory as its argument
    mock_process_path.assert_called_once_with(
        "test/test_data/enforce_notebook_run_order_valid", True, False
    )

    assert result.exit_code == 0
    assert mock_warning.call_count == 1
