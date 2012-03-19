Autobahn WebSocket Test Suite
=============================

Provides a fully automated test suite to verify client and server
implementations of the WebSocket protocol.

Coverage
--------

The test suite will check an implementation by doing basic WebSockets
conversations, extensive protocol compliance verification and performance
and limits testing.

Contains about 300 test cases covering

 * Framing
 * Pings/Pongs
 * Reserved Bits
 * Opcodes
 * Fragmentation
 * UTF-8 Handling
 * Limits/Performance
 * Closing Handshake
 * Opening Handshake (under development)


Installation
------------

Install from Python package index:

    pip autobahntestsuite

Install from Source:

    git clone git://github.com/tavendo/AutobahnTestSuite.git
    cd AutobahnTestSuite/autobahntestsuite
    python setup.py install


Usage
-----

The test suite is packaged up and installed as a command line tool "wstest".
To get help and a list of options:

    wstest --help

wstest has different modes in which it can run:

 * echoserver
 * echoclient
 * broadcastclient
 * broadcastserver
 * fuzzingserver
 * fuzzingclient
 * testeeserver
 * testeeclient
 * wsperfcontrol
 * wsperfmaster
 * wampserver
 * wampclient

The automated WebSocket test suite comes under the modes: fuzzingserver and
fuzzingclient.

For example, to test browsers (or other WS clients):

    wstest -m fuzzingserver -s examples/fuzzingserver/fuzzingserve.json

and point your browser to http://localhost:8080.


More Information
----------------

For more information, current test reports and a list of
users (over 20 projects/companies), please visit:

   http://autobahn.ws/testsuite


Contact
-------

Get in touch on IRC #autobahn on chat.freenode.net or join the mailing
list on http://groups.google.com/group/autobahnws.
