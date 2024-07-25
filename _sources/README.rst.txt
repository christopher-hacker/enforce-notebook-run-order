enforce-notebook-run-order
==========================

Enforce the run order of Jupyter notebooks.

Jupyter notebooks are great for interactive data analysis. However, when
they can encourage a bad habit: running cells out of order. This can lead
to notebooks being committed to the repository in a state where they don't run
from top to bottom, and other collaborators may receive different results
when running the notebook from top to bottom.

``enforce-notebook-run-order`` enforces the run order of a notebook by raising an exception if
any cells are run out of order.

Installation
------------

``enforce-notebook-run-order`` can be installed via pip:

.. code-block:: bash

    pip install enforce-notebook-run-order

It can also be set up as a `pre-commit hook <https://pre-commit.com/>`__. See the
`pre-commit hook <#pre-commit-hook>`__ section for more details.

Usage
-----

``enforce-notebook-run-order`` can be used as a standalone script, or as a `pre-commit hook <https://pre-commit.com/>`__.

Standalone
^^^^^^^^^^

To use ``enforce-notebook-run-order`` as a standalone script, simply run it with the path to the
notebook(s) you want to check:

.. code-block:: bash

    nbcheck my_notebook.ipynb my_other_notebook.ipynb

Or point it to a directory to check all notebooks in that directory:

.. code-block:: bash

    nbcheck my_notebooks/

If no paths are specified, ``nbcheck`` will check all notebooks in the current directory.

You can also use the full ``enforce-notebook-run-order`` command, but the ``nbcheck`` command is
provided as a convenience.

pre-commit hook
^^^^^^^^^^^^^^^

To use ``enforce_notebook_run_order`` as a pre-commit hook, add the following to your ``.pre-commit-config.yaml``:

.. code-block:: yaml

    repos:
    -   repo: https://github.com/christopher-hacker/enforce-notebook-run-order
        rev: 1.4.1
        hooks:
        -   id: enforce-notebook-run-order

disabling output checks
^^^^^^^^^^^^^^^^^^^^^^^

By default, ``enforce-notebook-run-order`` will check that the output of each cell matches the
output of the previous run. This will catch cases where a cell is run out of order, but the
execution count is still sequential. However, this can be problematic if the output of a cell
changes between runs, such as when using random numbers. It can also be problematic if the
notebook runs for a long time.

There are three ways to disable output checks:

1. Disabling running all notebooks using the ``--no-run`` flag:

   .. code-block:: bash

       nbcheck --no-run my_notebook.ipynb

2. Disabling running a single notebook using the ``no-run`` marker **in the first cell of the notebook**:

    .. code-block:: python
    
         # no-run
         print("This notebook will not be run")

3. Disabling output checks for a single cell using the ``no-check-output`` marker:

    .. code-block:: python
    
         # no-check-output
         print("This cell will be run, but its output will not be checked")
