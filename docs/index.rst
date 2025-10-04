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