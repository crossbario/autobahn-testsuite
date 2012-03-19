Autobahn WebSocket Test Suite
=============================

Provides a fully automated test suite to verify client and server
implementations of the WebSocket protocol and a couple of other
tools useful for WebSocket implementors and developers.


Test Suite Coverage
-------------------

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


Other Tools
-----------

Besides the automated testsuite (aka "fuzzing" server/client), **wstest**
also includes a number of other handy modes:

 * WebSocket echo server and client
 * WebSocket broadcast server (and client driver)
 * Testee modes to test Autobahn itself against the test suite
 * **wsperf** controller and master (see below for more)
 * WAMP server and client, for developing WAMP implementations


Prerequisites
-------------

AutobahnTestSuite is implemented in Python. It should run anywhere where
Python is available.

You will need:

  * Python - http://www.python.org
  * Python Setuptools - http://pypi.python.org/pypi/setuptools

Recommended is using the latest Python 2.7 release.


Installation
------------

Open a command shell, and install from Python package index:

    easy_install autobahntestsuite


Doing so automatically downloads and installs everything needed
including any dependencies.


Install from Source:

    git clone git://github.com/tavendo/AutobahnTestSuite.git
    cd AutobahnTestSuite/autobahntestsuite
    python setup.py install


*Caution: You should know what you are doing if you use HEAD on master.
Releases are usually tagged. Probably use those.*


Usage
-----

The test suite is packaged up and installed as a command line tool **wstest**.

To get help and a list of options:

    wstest --help


**wstest** has different modes in which it can run:

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


### Mode fuzzingserver/fuzzingclient

The automated WebSocket test suite comes under the modes: fuzzingserver and
fuzzingclient.

For example, to test browsers (or other WS clients):

    wstest -m fuzzingserver

and point your browser to http://localhost:8080.

The fuzzing modes are configured using a spec file. If you don't provide
one, **wstest** will auto-generate one (and reuse that the next time).

You can provide your own, modified spec file by doing

    wstest -m fuzzingserver -s <your spec file>

Reports will be generated as a set of HTML files. To create reports for
multiple testee's, DO NOT restart **wstest** in between, since (currently),
it will forget everything when stopped.


### Mode testeeserver/testeeclient

These modes are for testing Autobahn itself against the test suite.

The testeeserver can be tested using a 2nd instance of **wstest** running
in fuzzingclient mode.

For example, to test Autobahn along other WebSocket servers, i.e. do

    wstest -m testeeserver ws://localhost:9001

start your other WebSocket servers on other ports, and then run the testsuite
against all:

    wstest -m fuzzingclient -s fuzzingclient.json

where you have edited *fuzzingclient.json* for all servers under test, i.e.


    {
       "options": {"failByDrop": false},
       "outdir": "./reports/servers",

       "servers": [
                    {"agent": "AutobahnServer",
                     "url": "ws://localhost:9001",
                     "options": {"version": 18}},

                    {"agent": "MyAwesomeServer",
                     "url": "ws://localhost:9002",
                     "options": {"version": 18}}
                  ],

       "cases": ["*"],
       "exclude-cases": [],
       "exclude-agent-cases": {}
    }


Likewise, the testeeclient can be tested using a 2nd instance of **wstest**
running in fuzzingserver mode.


### Mode echoserver/echoclient

Simple WebSocket echo server and client that will just send back any
text or binary message it receives from it's connected peer.


    wstest -m echoserver -w ws://localhost:9000


### Mode broadcastclient/broadcastserver

The broadcastserver mode will run a WebSocket server that will broadcast
any text or binary message it receives to all currently connected clients.

The broadcastclient mode is intended as a test peer for the broadcastserver.
It will dump any message it receives to console, and send a message every
two seconds.


### Mode wsperfcontrol

PERLIMINARY

This mode is used to control wsperf (running in master mode).

wsperf is a WebSocket performance probe developed as part of WebSocket++

  https://github.com/zaphoyd/websocketpp


### Mode wsperfmaster

PERLIMINARY

This mode is used to control distributed sets of wsperf (running in slave mode).

wsperf is a WebSocket performance probe developed as part of WebSocket++

  https://github.com/zaphoyd/websocketpp


### Mode wampserver/wampclient

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
