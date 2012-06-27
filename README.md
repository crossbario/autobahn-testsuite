AutobahnTestsuite
=================

The AutobahnTestsuite provides a fully automated test suite to verify client and server implementations of [The WebSocket Protocol](http://tools.ietf.org/html/rfc6455) for specification conformance and implementation robustness.

AutobahnTestsuite also provides a couple of other tools useful for WebSocket
(and [WAMP](http://wamp.ws)) implementors and developers.


Test Suite Coverage
-------------------

The test suite will check an implementation by doing basic WebSocket
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
 * Testee modes to test [AutobahnPython](http://autobahn.ws/python) against the test suite
 * **wsperf** controller and master (see below for more)
 * WAMP server and client, for developing WAMP implementations


Prerequisites
-------------

AutobahnTestSuite is implemented in Python. It should run anywhere where
Python is available.

You will need:

  * [Python](http://www.python.org)
  * [Python Setuptools](http://pypi.python.org/pypi/setuptools)
  * [Twisted](http://twistedmatrix.com)

Recommended is using the latest Python 2.7 release, Python 2.6 works also fine, but Python 3 won't cut it.


Installation
------------

Open a command shell, and install from Python package index:

    easy_install autobahntestsuite


Doing so automatically downloads and installs everything needed
including any dependencies.

Alternatively, install from sources:

    git clone git://github.com/tavendo/AutobahnTestSuite.git
    cd AutobahnTestSuite
    git checkout v0.5.1
    cd autobahntestsuite
    python setup.py install


*Caution: Do NOT use current HEAD, but a tagged release like above.*


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


Server and client modes support TLS (that is WSS). For servers you will
need to provide a server key and certificate file.


### Mode fuzzingserver/fuzzingclient

The automated WebSocket test suite comes under the modes: **fuzzingserver** and
**fuzzingclient**.

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

These modes are for testing [AutobahnPython](http://autobahn.ws/python) against the test suite.

The **testeeserver** can be tested using a 2nd instance of **wstest** running
in **fuzzingclient** mode.

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

WebSocket echo server that will just send back any text or binary message
it receives from it's connected peer.

    wstest -m echoserver -w ws://localhost:9000

WebSocket echo client 

	wstest -m echoclient -w <Your Server IP:Port>


### Mode broadcastclient/broadcastserver

The broadcastserver mode will run a WebSocket server that will broadcast
any text or binary message it receives to all currently connected clients.

	wstest -m broadcastserver -w ws://localhost:9000

The broadcastclient mode is intended as a test peer for the broadcastserver.
It will dump any message it receives to console, and send a message every
two seconds.


	wstest -m broadcastclient -w <Your Server IP:Port>


### Mode wsperfcontrol

PERLIMINARY

This mode is used to control **wsperf** (running in master mode).

**wsperf** is a WebSocket performance probe developed as part of WebSocket++

* http://www.zaphoyd.com/wsperf
* https://github.com/zaphoyd/websocketpp
* https://github.com/zaphoyd/websocketpp/wiki/wsperf
* https://github.com/zaphoyd/websocketpp/wiki/wsperf:-stress_test


### Mode wsperfmaster

PERLIMINARY

This mode is used to control distributed sets of **wsperf** (running in slave mode).

**wsperf** is a WebSocket performance probe developed as part of WebSocket++

  http://www.zaphoyd.com/wsperf
  https://github.com/zaphoyd/websocketpp


### Mode wampserver/wampclient

Provides test WAMP client and server to aid in both learning WAMP and
developing WAMP conforming implementations.


	wstest -d -m wampserver -w ws://localhost:9000
	wstest -d -m wampclient -w <Your Server IP:Port>


More Information
----------------

For more information, current test reports and a list of
users (over 30 projects/companies), please visit the project's [homepage](http://autobahn.ws/testsuite).


Contact
-------

Get in touch on IRC #autobahn on chat.freenode.net or join the mailing
list on http://groups.google.com/group/autobahnws.
