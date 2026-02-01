Installation
------------
There is no need to directly install this package - it should get installed automatically
as a dependency when installing a specific display driver. See the instructions in the
relevant sub-project documentation.

Installing from PyPi
^^^^^^^^^^^^^^^^^^^^
If you do want to install this package directly, use the latest version of the luma.core
library directly from `PyPI <https://pypi.org/project/luma.core>`_.

First, create a `virtual environment <https://docs.python.org/3/library/venv.html>`__::

  $ python3 -m venv ~/luma-env

This creates a virtual environment in the home directory called ``luma-env``
and a Python executable at ``~/luma-env/bin/python``.

Activate the environment::

  $ source ~/luma-env/bin/activate

Finally, install the latest version of the luma.core library in the
virtual environment with::

  $ ~/luma-env/bin/python -m pip install luma.core

Test if it worked by printing the luma.core version number:

  $ ~/luma-env/bin/python -c "import luma.core;print(luma.core.__version__)"
  2.5.3
