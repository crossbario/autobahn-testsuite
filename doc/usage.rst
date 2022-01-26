Usage
=====


The test suite is packaged up and installed as a command line tool **wstest**.

To get help and a list of options:

::

   wstest --help

**wstest** has different modes in which it can run:

* ``echoserver``
* ``echoclient``
* ``broadcastclient``
* ``broadcastserver``
* ``fuzzingserver``
* ``fuzzingclient``
* ``testeeserver``
* ``testeeclient``
* ``wsperfcontrol``
* ``wsperfmaster``
* ``wampserver``
* ``wampclient``
* ``massconnect``

Server and client modes support TLS (that is WSS). For servers you will need to provide a server key and certificate file.


Mode fuzzingserver/fuzzingclient
--------------------------------

The automated WebSocket test suite comes under the modes:

* fuzzingserver
* fuzzingclient

For example, to test browsers (or other WebSocket clients):

::

   wstest -m fuzzingserver

and point your browser to ``http://localhost:8080``.

The fuzzing modes are configured using a spec file. If you don't provide one, **wstest** will auto-generate one (and reuse that the next time).

You can provide your own, modified spec file by doing

::

   wstest -m fuzzingserver -s <your spec file>

Reports will be generated as a set of HTML files. To create reports for multiple testee's, DO NOT restart **wstest** in between, since (currently), it will forget everything when stopped.

To enable Server Name Indication for the fuzzing client, you can add optional "hostname" keys for the servers in your spec file, e.g

::

   "servers":  [
                  {"agent": "ExampleServer",
                  "url": "wss://socket.example.com",
                  "options": {"version": 18}},
                  "hostname": "socket.example.com"
               ]

Mode testeeserver/testeeclient
------------------------------

These modes are for testing `AutobahnPython <http://autobahn.ws/python>`__ against the test suite.

The ``testeeserver`` can be tested using a 2nd instance of **wstest** running in ``fuzzingclient`` mode.

For example, to test Autobahn along other WebSocket servers, do

::

   wstest -m testeeserver -w ws://localhost:9001

start your other WebSocket servers on other ports, and then run the testsuite against all:

::

   wstest -m fuzzingclient -s fuzzingclient.json

where you have edited ``fuzzingclient.json`` for all servers under test, e.g.

::

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

Likewise, the ``testeeclient`` can be tested using a 2nd instance of **wstest** running in fuzzingserver mode.


Mode echoserver/echoclient
--------------------------

WebSocket echo server that will just send back any text or binary message it receives from its connected peer.

::

   wstest -m echoserver -w ws://localhost:9000

WebSocket echo client

::

   wstest -m echoclient -w <Your Server IP:Port>


Mode broadcastclient/broadcastserver
------------------------------------

The ``broadcastserver`` mode will run a WebSocket server that will broadcast any text or binary message it receives to all currently connected clients.

::

   wstest -m broadcastserver -w ws://localhost:9000

The broadcastclient mode is intended as a test peer for the broadcastserver. It will dump any message it receives to console, and send a message every two seconds.

::

   wstest -m broadcastclient -w <Your Server IP:Port>


Mode wsperfcontrol
------------------

This mode is used to control **wsperf** running in master mode. **wsperf** is a WebSocket performance probe developed as part of WebSocket++.

* https://github.com/zaphoyd/wsperf
* https://github.com/zaphoyd/websocketpp
* https://github.com/zaphoyd/websocketpp/wiki/wsperf
* https://github.com/zaphoyd/websocketpp/wiki/wsperf:-stress_test

Build **wsperf**:

::

   git clone git://github.com/zaphoyd/websocketpp.git
   cd websocketpp
   scons
   cd build/release/wsperf

Run **wsperf** in *server mode*:

::

   wsperf -s

Start a testee server:

::

   wstest -m testeeserver -w ws://127.0.0.1:9000

Start **wstest** to control **wsperf**:

::

   wstest -m wsperfcontrol -w ws://127.0.0.1:9050

**wsperf** is running in *server mode*, which means it can be controlled via **wstest** running in `wsperfcontrol` mode. **wsperf** will perform test against the testee as controlled from **wstest**.

The tests to be run are provided in a test specification. When **wstest** is run without providing a test specification, it will create an example (which has happened as we did above).

Here is the generated test spec:

::

   {
      "options": {
         "debug": false
      },
      "servers":  [
                     {
                        "name": "AutobahnPython",
                        "uri": "ws://127.0.0.1:9000",
                        "desc": "Autobahn WebSocket Python on localhost"
                     }
                  ],
      "testsets": [
         {
            "mode": "echo",
            "options": {
               "outfile": "report_echo.txt",
               "digits": 0,
               "sep": "\t",
               "rtts": false,
               "quantile_count": 10,

               "count": 1000,
               "timeout": 100000,
               "binary": true,
               "sync": true,
               "verify": false
            },
            "cases": [
                        {"size": 0},
                        {"size": 64},
                        {"size": 1024}
                     ]
         }
      ]
   }


A test spec must provide a list of *servers* and a list of *testsets*. Each *testset* must specify the test *mode* (currently only "echo"). *Options* specify tunables that apply to the complete *testset*:

* ``outfile`` - name of the output file to write results
* ``digits`` - numbers of digits to round results to
* ``sep`` - separator character used for writing results
* ``rtts`` - output Round-trip times of each and every message
* ``quantile_count`` - number of quantiles in result statistics

A list of *cases* specifies the actual test cases. Test cases for echo have the following parameters:

* ``count`` - number of message to send
* ``size`` - size of messages in bytes
* ``timeout`` - WebSocket connection timeout in seconds
* ``binary`` - if true, send binary WebSocket messages, else text
* ``sync`` - if true, wait for message echo before sending new message
* ``verify`` - if true, verify the content of the echo reply, else only check length

When the parameter is present in the ``case``, that value applies. If not, the setting from ``options`` on ``testset`` applies. At least one must be present.

Here is an example output:
::

   name            outcome count   size    min median  max avg stddev  q0  q1  q2  q3  q4  q5  q6  q7  q8  q9
   AutobahnPython  PASSED  1000    0       129 133     541 142 24      132 132 132 132 133 134 139 149 153 541
   AutobahnPython  PASSED  1000    64      177 193     650 197 25      179 180 190 191 193 194 195 204 219 650
   AutobahnPython  PASSED  1000    1024    490 543     907 548 53      497 498 501 508 543 571 579 591 600 907

All times are in microseconds. The single most import column is median. The columns q0 to q9 give the upper bounds of the respective quantile.


Mode wsperfmaster
-----------------

*UNDER DEVELOPMENT*

This mode is used to control distributed sets of *wsperf* (running in slave mode). *wsperf* is a WebSocket performance probe developed as part of WebSocket++.

* http://www.zaphoyd.com/wsperf
* https://github.com/zaphoyd/websocketpp


Mode wampserver/wampclient
--------------------------

Provides test WAMP client and server to aid in both learning WAMP and developing WAMP conforming implementations.

::

   wstest -d -m wampserver -w ws://localhost:9000
   wstest -d -m wampclient -w <Your Server IP:Port>


Mode massconnect
----------------

``massconnect`` mode can be used to test the maximum number of WebSocket connections a server can sustain and how many WebSocket opening handshakes a server can do per second.

The mode is controlled via a spec file. When no spec file is provided, a template is generated:

::

   wstest -m massconnect

Edit the file for your needs, and restart

::

   wstest -m massconnect -s massconnect.json

You can provide a list of servers.

The ramp up of WebSocket connections is controlled via 3 parameters:

::

   batchsize
   batchdelay
   retrydelay

**wstest** will start ``batchsize`` connections in a fast loop, then wait ``batchdelay`` ms, and go on until ``connections`` is reached.

Depending on network settings and server, this can quickly overwhelm a server, and the server will deny/fail connections. Those are retried after ``retrydelay`` ms. Thus, **wstest** will not give up until ``connections`` is reached.

The number of connections **wstest** can open on a server is limited by the number of ephemeral ports on the machine on the outgoing interface / IP. Something like 64k at most. If you need to test the server with more connections, currently you will need to run multiple instances of **wstest** (on different machines).

On Windows, you will need to tune some settings for large numbers of outgoing TCP connections. Edit the registry entry

::

   Computer/HKEY_LOCAL_MACHINE\SYSTEM\CurrenControlSet\Services\Tcpip\Parameters

and create or set the key ``MaxUserPort`` to ``DWORD`` with value ``65534``. I forgot whether you need to reboot .. probably.
