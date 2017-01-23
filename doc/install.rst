Installation
------------
.. note:: The library has been tested against Python 2.7 and 3.4+.

   For **Python3** installation, substitute the following in the 
   instructions below.

   * ``pip`` ⇒ ``pip3``, 
   * ``python`` ⇒ ``python3``, 
   * ``python-dev`` ⇒ ``python3-dev``,
   * ``python-pip`` ⇒ ``python3-pip``.

Installing from PyPi
^^^^^^^^^^^^^^^^^^^^
.. note:: This is the preferred installation mechanism.

Install the latest version of the library directly from
`PyPI <https://pypi.python.org/pypi?:action=display&name=luma.core>`_::

  $ sudo apt-get install python-dev python-pip
  $ sudo pip install --upgrade luma.core

Installing from source
^^^^^^^^^^^^^^^^^^^^^^
Alternatively, clone the code from github::

  $ git clone https://github.com/rm-hull/luma.core.git

Next, follow the specific steps below for your OS.

Raspbian
""""""""
.. code:: bash

  $ cd luma.core
  $ sudo apt-get install python-dev python-pip
  $ sudo pip install spidev
  $ sudo python setup.py install

Arch Linux
""""""""""
.. code:: bash

  cd luma.core
  pacman -Sy base-devel python2
  pip install spidev
  python2 setup.py install
