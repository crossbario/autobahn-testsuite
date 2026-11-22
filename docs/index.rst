AutobahnTestsuite Documentation
===============================

The AutobahnTestsuite provides a fully automated test suite to verify client and server implementations of the WebSocket protocol for specification conformance and implementation robustness.

Features
--------

* Over 500 test cases covering WebSocket protocol compliance
* Framing, Pings/Pongs, Reserved Bits, Opcodes testing  
* Fragmentation and UTF-8 handling validation
* Limits and performance testing
* Closing and opening handshake verification
* WebSocket compression (permessage-deflate extension) support

Installation
------------

**Using Docker (Recommended)**

.. code-block:: bash

   docker run -it --rm \
       -v "${PWD}/config:/config" \
       -v "${PWD}/reports:/reports" \
       -p 9001:9001 \
       --name fuzzingserver \
       crossbario/autobahn-testsuite

**Using Python Package**

.. code-block:: bash

   pip install autobahntestsuite

.. note::
   The Python package requires Python 2.7 and is primarily maintained for compatibility. 
   We recommend using the Docker image for new deployments.

Usage
-----

**Testing WebSocket Servers**

.. code-block:: bash

   # Start the fuzzing server
   wstest -m fuzzingserver
   
   # Point your WebSocket client to ws://localhost:9001

**Testing WebSocket Clients**

.. code-block:: bash

   # Start your WebSocket server on port 9001
   # Then run the fuzzing client
   wstest -m fuzzingclient

**Docker Usage**

.. code-block:: bash

   # Create configuration directory
   mkdir -p config reports
   
   # Run testsuite in fuzzingserver mode (test clients)
   docker run -it --rm \
       -v "${PWD}/config:/config" \
       -v "${PWD}/reports:/reports" \
       -p 9001:9001 \
       crossbario/autobahn-testsuite

Memory Usage
------------

`wstest` runs on PyPy, whose garbage collector sizes its nursery from the
CPU cache size. On CPUs that report a large cache (for example 480MB on
Intel Xeon 6, giving a 240MB nursery), the GC runs rarely, if ever,
resulting in substantial memory growth: a run of all test cases can then
need more than 8GB, instead of about 1GB.

To avoid this, pin the nursery size with the ``PYPY_GC_NURSERY`` environment
variable. This applies to every ``wstest`` mode. For the fuzzing server (the
default command of the image):

.. code-block:: bash

   docker run -it --rm \
       -e PYPY_GC_NURSERY=4MB \
       -v "${PWD}/config:/config" \
       -v "${PWD}/reports:/reports" \
       -p 9001:9001 \
       crossbario/autobahn-testsuite

and for the fuzzing client:

.. code-block:: bash

   docker run -it --rm --network host \
       -e PYPY_GC_NURSERY=4MB \
       -v "${PWD}/config:/config" \
       -v "${PWD}/reports:/reports" \
       crossbario/autobahn-testsuite \
       wstest --mode fuzzingclient --spec /config/fuzzingclient.json

When running the Python package under PyPy, set the variable in the
environment of ``wstest`` in the same way.

To see the nursery size PyPy chooses on your machine:

.. code-block:: bash

   docker run --rm crossbario/autobahn-testsuite pypy -c "import gc; print gc.get_stats()"

Background and measurements:
`#171 <https://github.com/crossbario/autobahn-testsuite/issues/171>`_. The
``wstest-memory`` workflow runs all test cases with a 4MB and with a 240MB
nursery under an 8GB memory limit.

Test Reports
------------

After running tests, detailed HTML reports are generated showing:

* Test case results (Pass/Fail/Unimplemented)
* Protocol compliance summary
* Detailed failure descriptions
* Performance metrics

The reports include compliance status for each test case and help identify specific areas where implementations may need improvement.

Resources
---------

* `GitHub Repository <https://github.com/crossbario/autobahn-testsuite>`_
* `PyPI Package <https://pypi.org/project/autobahntestsuite/>`_
* `Docker Hub Image <https://hub.docker.com/r/crossbario/autobahn-testsuite>`_
* `WebSocket Protocol RFC 6455 <https://tools.ietf.org/html/rfc6455>`_
* `WAMP Protocol <https://wamp-proto.org/>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
