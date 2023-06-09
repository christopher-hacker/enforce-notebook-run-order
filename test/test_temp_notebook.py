"""tests the temp notebook module"""

import json
import os
import tempfile
import pytest
from enforce_notebook_run_order import temp_notebook

# pylint: disable=redefined-outer-name


@pytest.fixture
def valid_notebook_data():
    """
    returns the path to a tempfile containing complete json of a jupyter notebook with 1 cell
    """
    return {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": ["hello world\n"],
                    }
                ],
                "source": ['print("hello world")'],
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": ".venv",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.10",
            },
            "orig_nbformat": 4,
        },
        "nbformat": 4,
        "nbformat_minor": 2,
    }


@pytest.fixture
def invalid_notebook_data():
    """returns json that is not a valid jupyter notebook"""
    return {"not_a_notebook": True}


@pytest.fixture
def output_mismatch_data():
    """
    returns the json of a notebook whose cell output does not match
    the expected output
    """
    return {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": ["var_1 = 2\n"],
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [
                    {"name": "stdout", "output_type": "stream", "text": ["1\n"]}
                ],
                "source": ["print(var_1)\n"],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": ".venv",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.10",
            },
            "orig_nbformat": 4,
        },
        "nbformat": 4,
        "nbformat_minor": 2,
    }


@pytest.fixture
def output_mismatch_data_no_run_comment():
    """
    returns the json of a notebook whose cell output does not match
    the expected output, but has the "no-run" comment in the first cell
    """
    return {
        # pylint: disable=R0801
        # ^^ R0801 is similar lines in multiple files. this DOES actually need to be duplicated
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": ["# no-run"],
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [],
                "source": ["var_1 = 2\n"],
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "outputs": [
                    {"name": "stdout", "output_type": "stream", "text": ["1\n"]}
                ],
                "source": ["print(var_1)\n"],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": ".venv",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.10",
            },
            "orig_nbformat": 4,
        },
        "nbformat": 4,
        "nbformat_minor": 2,
    }


@pytest.fixture
def output_mismatch_data_no_check_output_comment():
    """
    returns the json of a notebook which has outputs that will not match
    the expected outputs, but has the "no-check-output" comment in the
    cell that always changes
    """
    return {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": ["from datetime import datetime\n"],
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": ["2023-06-06 09:50:37.141395\n"],
                    }
                ],
                "source": ["# no-check-output\n", "print(datetime.now())\n"],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": ".venv",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.10",
            },
            "orig_nbformat": 4,
        },
        "nbformat": 4,
        "nbformat_minor": 2,
    }


def create_temp_nb_and_return_path(nb_json):
    """
    creates a temp notebook file and returns the path to it
    """
    temp_dir = tempfile.mkdtemp()
    temp_nb_path = os.path.join(temp_dir, "temp_nb.ipynb")
    with open(temp_nb_path, "w", encoding="UTF-8") as notebook_file:
        json.dump(nb_json, notebook_file)
    return temp_nb_path


def test_run_valid_json(valid_notebook_data):
    """tests that the temp notebook runs with valid json"""
    with temp_notebook.TempNotebook(
        create_temp_nb_and_return_path(valid_notebook_data)
    ) as temp_notebook_obj:
        temp_notebook_obj.run()


def test_run_invalid_json(invalid_notebook_data):
    """tests that the temp notebook raises an exception with invalid json"""
    with temp_notebook.TempNotebook(
        create_temp_nb_and_return_path(invalid_notebook_data)
    ) as temp_notebook_obj:
        with pytest.raises(temp_notebook.NotebookRunFailedError):
            temp_notebook_obj.run()


def test_check_notebook_valid(valid_notebook_data):
    """tests that the temp notebook passes with valid json"""
    with temp_notebook.TempNotebook(
        create_temp_nb_and_return_path(valid_notebook_data)
    ) as temp_notebook_obj:
        temp_notebook_obj.check_notebook()


def test_check_notebook_invalid(output_mismatch_data):
    """tests that the temp notebook fails with invalid json"""
    with temp_notebook.TempNotebook(
        create_temp_nb_and_return_path(output_mismatch_data)
    ) as temp_notebook_obj:
        with pytest.raises(temp_notebook.CellOutputMismatchError):
            temp_notebook_obj.check_notebook()


def test_output_mismatch_data_no_run_comment(output_mismatch_data_no_run_comment):
    """
    tests that the output_mismatch_data_no_run_comment fixture fails without the comment
    """
    # delete the cell with the comment for this test
    del output_mismatch_data_no_run_comment["cells"][0]
    with temp_notebook.TempNotebook(
        create_temp_nb_and_return_path(output_mismatch_data_no_run_comment)
    ) as temp_notebook_obj:
        with pytest.raises(temp_notebook.CellOutputMismatchError):
            temp_notebook_obj.check_notebook()


def test_check_notebook_no_run_comment(output_mismatch_data_no_run_comment):
    """tests that the temp notebook passes with invalid json"""
    with temp_notebook.TempNotebook(
        create_temp_nb_and_return_path(output_mismatch_data_no_run_comment)
    ) as temp_notebook_obj:
        temp_notebook_obj.check_notebook()


def test_output_mismatch_data_no_check_output_comment(
    output_mismatch_data_no_check_output_comment,
):
    """
    tests that the output_mismatch_data_no_check_output_comment fixture fails without the comment
    """
    # delete the comment for this test
    del output_mismatch_data_no_check_output_comment["cells"][1]["source"][0]
    with temp_notebook.TempNotebook(
        create_temp_nb_and_return_path(output_mismatch_data_no_check_output_comment)
    ) as temp_notebook_obj:
        with pytest.raises(temp_notebook.CellOutputMismatchError):
            temp_notebook_obj.check_notebook()


def test_check_notebook_no_check_output_comment(
    output_mismatch_data_no_check_output_comment,
):
    """tests that the temp notebook passes with invalid json"""
    with temp_notebook.TempNotebook(
        create_temp_nb_and_return_path(output_mismatch_data_no_check_output_comment)
    ) as temp_notebook_obj:
        temp_notebook_obj.check_notebook()


def test_check_notebook_uses_external_data():
    """tests that data files used by the notebook are copied to the temp directory"""
    with temp_notebook.TempNotebook(
        "test/test_data/temp_notebook_uses_external_data/temp_notebook_uses_external_data.ipynb"
    ) as temp_notebook_obj:
        temp_notebook_obj.check_notebook()


def test_check_notebook_uses_external_data_directory():
    """
    tests that data files used by the notebook are copied to the temp directory
    when the notebook references a directory
    """
    with temp_notebook.TempNotebook(
        "test/test_data/temp_notebook_uses_external_data/"
        "temp_notebook_uses_external_data_directory.ipynb"
    ) as temp_notebook_obj:
        temp_notebook_obj.check_notebook()
