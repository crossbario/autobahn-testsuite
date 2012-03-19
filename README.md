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


Server and client modes do support TLS (that is WSS). For servers you will
need to provide a server key and certificate file.


Mode fuzzingserver/fuzzingclient
--------------------------------

The automated WebSocket test suite comes under the modes: fuzzingserver and
fuzzingclient.

For example, to test browsers (or other WS clients):

    wstest -m fuzzingserver

and point your browser to http://localhost:8080.

The fuzzing modes are configured using a spec file. If you don't provide
one, wstest will auto-generate one (and reuse that the next time).

You can provide your own, modified spec file by doing

    wstest -m fuzzingserver -s <your spec file>


Mode testeeserver/testeeclient
------------------------------

These modes are for testing Autobahn itself against the test suite.

The testeeserver can be tested using a 2nd instance of wstest running
in fuzzingclient mode.

The testeeclient can be tested using a 2nd instance of wstest running
in fuzzingserver mode.


Mode echoserver/echoclient
--------------------------

Simple WebSocket echo server and client that will just send back any
text or binary message it receives from it's connected peer.


    wstest -m echoserver -w ws://localhost:9000


Mode broadcastclient/broadcastserver
------------------------------------

The broadcastserver mode will run a WebSocket server that will broadcast
any text or binary message it receives to all currently connected clients.

The broadcastclient mode is intended as a test peer for the broadcastserver.
It will dump any message it receives to console, and send a message every
two seconds.


Mode wsperfcontrol
------------------

PERLIMINARY

This mode is used to control wsperf (running in master mode).

wsperf is a WebSocket performance probe developed as part of WebSocket++

  https://github.com/zaphoyd/websocketpp


Mode wsperfmaster
------------------

PERLIMINARY

This mode is used to control distributed sets of wsperf (running in slave mode).

wsperf is a WebSocket performance probe developed as part of WebSocket++

  https://github.com/zaphoyd/websocketpp


Mode wampserver/wampclient
--------------------------

Not yet implemented. Will provide test WAMP client and server to aid in
developing WAMP conforming implementations.


More Information
----------------

For more information, current test reports and a list of
users (over 20 projects/companies), please visit:

   http://autobahn.ws/testsuite


Contact
-------

Get in touch on IRC #autobahn on chat.freenode.net or join the mailing
list on http://groups.google.com/group/autobahnws.
