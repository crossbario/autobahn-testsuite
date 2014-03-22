.. _installation:

Installation
============

.. |at| replace:: **Autobahn**\|Testuite

Prerequisites
-------------

|at| is implemented in Python. It should run anywhere where Python is available.

You will need:

 * `Python <http://www.python.org/>`_
 * `pip <https://pypi.python.org/pypi/pip>`_
 * `Twisted <http://twistedmatrix.com/>`_

Recommended is using the latest Python 2.7 release, Python 2.6 works also fine, but Python 3 doesn't.

.. note:: Unless you have a specific requirement and know what you are doing, a 32-bit Python is recommended.

For best performance, you should run on `PyPy <http://pypy.org/>`_.

On Windows, for better performance, you might want to run Twisted under IOCP reactor. For that, you will need

 * `PyWin32 <http://sourceforge.net/projects/pywin32/>`_

If you want to do tests involving secure WebSocket (wss), you will need

 * `PyOpenSSL <http://pypi.python.org/pypi/pyOpenSSL/>`_


Installation
------------

Open a command shell, and install from Python package index:

::

   pip install autobahntestsuite

Doing so automatically downloads and installs everything needed including any dependencies.

Alternatively, install from sources:

::

   git clone git://github.com/tavendo/AutobahnTestSuite.git
   cd AutobahnTestSuite
   git checkout v0.6.1
   cd autobahntestsuite
   python setup.py install

.. note:: Caution: Do NOT use current HEAD, but a tagged release like above.


Testing
-------

To test your installation, open a command shell and do:

::

   wstest --help

``wstest`` is the |at| executable and installed in a system-wide location, i.e. on Windows under

::

   C:\Python27\Scripts\wstest.exe

.. note:: If wstest cannot be found on your command line, make sure you have the Python Scripts path in your PATH.
