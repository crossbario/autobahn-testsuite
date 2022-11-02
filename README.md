# Autobahn|Testsuite

The **Autobahn**|Testsuite provides a fully automated test suite to verify client and server implementations of [The WebSocket Protocol](http://tools.ietf.org/html/rfc6455) for specification conformance and implementation robustness.

**Autobahn**|Testsuite also provides a couple of other tools useful for WebSocket
(and [WAMP](http://wamp.ws)) implementors and developers.

**What users are saying:**

> "Autobahn was a huge help during the standardization and early development of WebSocket in [Firefox](www.mozilla.org/firefox). It helped find many nasty corner conditions in a clean and repeatable way.
Interoperation testing like this really moves the Open Web forward."
**Patrick McManus, [Mozilla](http://www.mozilla.org/) [Firefox](www.mozilla.org/firefox)**

> "The [Jetty project](http://eclipse.org/jetty) has been active in the development of the websocket protocol and lack of a comprehensive test suite was an impediment to the standardisation of the protocol. The Autobahn test suit has filled that void and been warmly embraced by our websocket engineers at [Intalio](http://www.intalio.com/products/jetty/overview/) as it has been invaluable for evaluating the protocol development, improving inter operability and monitoring adoption of new/optional features.
*Our own implementation and the wider websocket 'ecosystem' are significantly better due to the availability of Autobahn*."
**Greg Wilkins, [Jetty](http://eclipse.org/jetty) author, Chief Architect at [Intalio](http://www.intalio.com/)**

> "During the time of implementing the latest WebSocket version in [Netty](http://netty.io/) and [Undertow](https://github.com/undertow-io/undertow) we were searching for a way to test our implementations and make sure they are 100% RFC compliant. While we already had unit tests in place there was a lack of good tests for the whole implementation. Using the AutobahnTestsuite for this purpose allowed us to concentrate on the implementation and made it easy to catch regressions as soon as possible."
**Norman Maurer, Principal Software Engineer at [Red Hat](http://www.redhat.com/)**


## Reports

For some current reports on the test coverage of [Autobahn|Python](https://github.com/crossbario/autobahn-python) see

* [WebSocket client functionality](https://crossbar.io/autobahn/testsuite/reports/clients/index.html)
* [WebSocket server functionality](https://crossbar.io/autobahn/testsuite/reports/servers/index.html)


## Test Suite Coverage

The test suite will check an implementation by doing basic WebSocket
conversations, extensive protocol compliance verification and performance
and limits testing.

**Autobahn**|Testsuite is used across the industry and contains over 500 test cases covering

* Framing
* Pings/Pongs
* Reserved Bits
* Opcodes
* Fragmentation
* UTF-8 Handling
* Limits/Performance
* Closing Handshake
* Opening Handshake (under development)
* WebSocket compression ([permessage-deflate extension](https://tools.ietf.org/html/draft-ietf-hybi-permessage-compression))


## Other Tools

Besides the automated testsuite (aka "fuzzing" server/client), **wstest**
also includes a number of other handy modes:

* WebSocket echo server and client
* WebSocket broadcast server (and client driver)
* Testee modes to test [AutobahnPython](http://autobahn.ws/python) against the test suite
* **wsperf** controller and master (see below for more)
* WAMP server and client, for developing WAMP implementations
* WebSocket Mass-Connect


## Users

Autobahn|Testsuite is used by numerous projects and companies across the industry:

<div class="testsuite_users_table">
  <ul style="float: left; width: 190px">
      <li><a href="http://autobahn.ws">Autobahn</a></li>
      <li><a href="http://www.mozilla.org/" target="_blank">Mozilla Firefox</a></li>
      <li><a href="http://www.chromium.org/Home" target="_blank">Google Chrome / WebKit</a></li>
      <li><a href="http://windows.microsoft.com/en-us/internet-explorer/products/ie/home" target="_blank">Microsoft Internet Explorer</a></li>
      <li><a href="http://www.rim.com/" target="_blank">RIM / Browser</a></li>
      <li><a href="http://www.zaphoyd.com/websocketpp" target="_blank">WebSocket++</a></li>
      <li><a href="http://www.serverframework.com" target="_blank">The Server Framework</a></li>
      <li><a href="http://eclipse.org/jetty/" target="_blank">Jetty</a></li>
      <li><a href="http://netty.io/" target="_blank">Netty</a></li>
      <li><a href="http://grizzly.java.net/" target="_blank">Grizzly</a></li>
      <li><a href="https://github.com/kerryjiang/WebSocket4Net" target="_blank">WebSocket4Net</a></li>
      <li><a href="https://github.com/kerryjiang/SuperWebSocket" target="_blank">SuperWebSocket</a></li>
      <li><a href="https://github.com/webbit/webbit" target="_blank">Webbit</a></li>
      <li><a href="https://github.com/lipp/lua-websockets" target="_blank">lua-websockets</a></li>
  </ul>
  <ul style="float: left; margin-left: 30px; width: 190px">
      <li><a href="http://crossbar.io" target="_blank">Crossbar.io</a></li>
      <li><a href="http://tomcat.apache.org/" target="_blank">Apache Tomcat</a></li>
      <li><a href="https://github.com/Worlize/WebSocket-Node" target="_blank">WebSocket-Node</a></li>
      <li><a href="https://github.com/einaros/ws" target="_blank">WS for node.js</a></li>
      <li><a href="https://github.com/LearnBoost/websocket.io" target="_blank">websocket.io</a></li>
      <li><a href="https://github.com/Lawouach/WebSocket-for-Python" target="_blank">ws4py</a></li>
      <li><a href="https://github.com/facebook/tornado" target="_blank">Facebook Tornado</a></li>
      <li><a href="https://github.com/google/pywebsocket" target="_blank">pywebsocket</a></li>
      <li><a href="http://www.noemax.com/" target="_blank">Noemax PowerWebSockets</a></li>
      <li><a href="http://www.noemax.com/" target="_blank">Noemax WCF-Xtensions</a></li>
      <li><a href="https://github.com/TooTallNate/Java-WebSocket" target="_blank">Java-WebSocket</a></li>
      <li><a href="http://jwebsocket.org/" target="_blank">jWebSocket</a></li>
      <li><a href="https://github.com/aaugustin/websockets" target="_blank">websockets</a></li>
      <li><a href="https://github.com/DamnedFacts/RSWebSocket" target="_blank">RSWebSocket</a></li>
  </ul>
  <ul style="float: left; margin-left: 30px; width: 190px">
      <li><a href="http://cloudsecurity.intel.com/api-management" target="_blank">Intel API Management</a></li>
      <li><a href="http://pusher.com/" target="_blank">Pusher / EM-WebSocket</a></li>
      <li><a href="https://github.com/square/SocketRocket" target="_blank">SocketRocket</a></li>
      <li><a href="https://github.com/DamnedFacts/RSWebSocket" target="_blank">RSWebSocket</a></li>
      <li><a href="http://faye.jcoglan.com/" target="_blank">Faye</a></li>
      <li><a href="https://bitbucket.org/Jeffrey/gevent-websocket/overview" target="_blank">gevent-websocket</a></li>
      <li><a href="https://github.com/extend/cowboy" target="_blank">Cowboy</a></li>
      <li><a href="http://caucho.com/resin-4.0/index.xtp" target="_blank">Resin</a></li>
      <li><a href="http://yaws.hyber.org/" target="_blank">Erlang Yaws</a></li>
      <li><a href="http://wasd.vsm.com.au/wasd/" target="_blank">WASD OpenVMS</a></li>
      <li><a href="http://gitorious.org/qtwebsocket" target="_blank">QtWebSocket</a></li>
      <li><a href="https://github.com/eventlet/eventlet" target="_blank">eventlet</a></li>
      <li><a href="http://code.google.com/p/zaproxy/" target="_blank">zaproxy</a></li>
      <li><a href="https://github.com/boostorg/beast" target="_blank">Boost/Beast</a></li>
      <li><a href="https://github.com/IBM-Swift/Kitura-WebSocket-NIO" target="_blank">Kitura-WebSocket-NIO</a></li>
      <li><a href="https://github.com/machinezone/IXWebSocket" target="_blank">IXWebSocket</a></li>
      <li>... and more (can't keep up)</li>
  </ul>
</div>
<div style="clear: both;"></div>


## Installation

### Using the testsuite Docker image

The testsuite is available as a [Docker image](https://hub.docker.com/r/crossbario/autobahn-testsuite/tags/) which allows
easy and repeatable use both for testing WebSocket clients and WebSocket servers.

By default, the image will run the testsuite in so-called "fuzzingserver" mode. This is the mode used to test your WebSocket _client_ implementations.

To start the testsuite container:

```console
docker run -it --rm \
    -v "${PWD}/config:/config" \
    -v "${PWD}/reports:/reports" \
    -p 9001:9001 \
    --name fuzzingserver \
    crossbario/autobahn-testsuite
```

Above will mount an (included) test configuration from the [docker/config](config) folder, which must include a server test configuration file [docker/config/fuzzingserver.json](docker/config/fuzzingserver.json) like this:

```json
{
    "url": "ws://127.0.0.1:9001",
    "outdir": "./reports/clients",
    "cases": ["*"],
    "exclude-cases": [
        "9.*",
        "12.*",
        "13.*"
    ],
    "exclude-agent-cases": {}
}
```

> This specific config will run all test cases, but exclude the longer running mass/performance test cases 9.*, and exclude the WebSocket compression test cases 12.*/13.* (which only make sense if your client library implements [RFC7692 ("permessage-deflate")](https://tools.ietf.org/html/rfc7692)).

Above command will also mount a host directory/volume [reports](reports) where the generated reports will be placed by the testsuite.

Finally, the config will make the fuzzing server run on port 9001 - and expose that on the host.

> To test multiple clients and generate one big report containing all clients, do NOT stop the testsuite container, but run all your clients, and then stop the container. The generated reports will include all clients.

Here is how to test the Python 3 / asyncio flavor of [AutobahnPython](https://github.com/crossbario/autobahn-python):

```console
pip install autobahn
wget https://raw.githubusercontent.com/crossbario/autobahn-python/master/wstest/testee_client_aio.py
python testee_client_aio.py
```

####

**The following recipe still works, but the new, recommended way is using a Docker toolchain image we provide. Please checkout [this](https://github.com/crossbario/crossbar-docker/tree/master/autobahn-testsuite#usage) - much easier and repeatable.**

The testsuite comes as a single command line tool, `wstest`. You will need Python 2 or PyPy (recommended).

> Right now we only support Python 2 and Python 3 will *not* work. The testsuite is developed and tested on CPython 2 and PyPy. The latter is a high-performance Python implementation.

The recommended way to install `wstest` is into it's own, dedicated [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

> On Debian/Ubuntu systems, you can install virtualenv like `sudo apt-get install python-virtualenv`.

Create a new virtualenv in your HOME and install Autobahn testsuite:

```console
virtualenv ~/wstest
source ~/wstest/bin/activate
pip install autobahntestsuite
```

You will now have the `wstest` tool:


```console
(wstest)oberstet@thinkpad-t430s:~$ which wstest
/home/oberstet/wstest/bin/wstest
(wstest)oberstet@thinkpad-t430s:~$ wstest -a
Autobahn 0.10.9
AutobahnTestSuite 0.7.4
(wstest)oberstet@thinkpad-t430s:~$ wstest --help
Usage: wstest [options]
Options:
  -d, --debug            Debug output [default: off].
  -a, --autobahnversion  Print version information for Autobahn and
                         AutobahnTestSuite.
  -m, --mode=            Test mode, one of: echoserver, echoclient,
                         broadcastclient, broadcastserver, fuzzingserver,
                         fuzzingclient, testeeserver, testeeclient, massconnect,
                         serializer [required]
  -t, --testset=         Run a test set from an import test spec.
  -s, --spec=            Test specification file [required in some modes].
  -o, --outfile=         Output filename for modes that generate testdata.
  -w, --wsuri=           WebSocket URI [required in some modes].
  -u, --webport=         Web port for running an embedded HTTP Web server;
                         defaults to 8080; set to 0 to disable. [optionally used
                         in some modes: fuzzingserver, echoserver,
                         broadcastserver, wsperfmaster]. [default: 8080]
  -i, --ident=           Testee client identifier [optional for client testees].
  -k, --key=             Server private key file for secure WebSocket (WSS)
                         [required in server modes for WSS].
  -c, --cert=            Server certificate file for secure WebSocket (WSS)
                         [required in server modes for WSS].
      --version          Display Twisted version and exit.
      --help             Display this help and exit.

(wstest)oberstet@thinkpad-t430s:~$
```

## How to use

### Testing WebSocket server implementations

To test a **WebSocket server implementation** and generate compliance test reports, first start the WebSocket server that you want to test. Here, we are using a example from Autobahn|Python:

```console
(python279_1)oberstet@thinkpad-t430s:~/scm/crossbario/autobahn-python/examples/twisted/websocket/testee$ python testee_server.py
2015-12-21 21:31:54+0100 [-] Log opened.
2015-12-21 21:31:54+0100 [-] TesteeServerFactory starting on 9001
2015-12-21 21:31:54+0100 [-] Starting factory <__main__.TesteeServerFactory object at 0x7faf23551210>
```

Then, run `wstest` in **fuzzing client mode**:

```console
cd ~
mkdir test
cd test
wstest -m fuzzingclient
```

The testsuite will now start a WebSocket fuzzing client connecting on TCP port 9001 to the WebSocket servers to be tested:

```console
(wstest)oberstet@thinkpad-t430s:~/test$ wstest -m fuzzingclient
Auto-generating spec file 'fuzzingclient.json'
Loading spec from /home/oberstet/test/fuzzingclient.json
...
Autobahn Fuzzing WebSocket Client (Autobahn Version 0.7.4 / Autobahn Testsuite Version 0.10.9)
Ok, will run 521 test cases against 1 servers
...
```

### Testing WebSocket client implementations

To test a **WebSocket client implementation** and generate compliance test reports, start `wstest` in **fuzzing server mode**:

```console
cd ~
mkdir test
cd test
wstest -m fuzzingserver
```

The testsuite will now start a WebSocket fuzzing server listening on TCP port 9001 for WebSocket clients to be tested:

```console
(wstest)oberstet@thinkpad-t430s:~/test$ wstest -m fuzzingserver
Auto-generating spec file 'fuzzingserver.json'
Loading spec from /home/oberstet/test/fuzzingserver.json
...
Autobahn WebSockets 0.7.4/0.10.9 Fuzzing Server (Port 9001)
Ok, will run 521 test cases for any clients connecting
...
```

> Note: The fuzzing server mode will also start a Web server on port 8080 that renders a HTML page for browser WebSocket clients to be tested.


On first run, the tool will auto-generated a test configuration file:

```console
(wstest)oberstet@thinkpad-t430s:~/test$ cat fuzzingserver.json

{
   "url": "ws://127.0.0.1:9001",
   "outdir": "./reports/clients",
   "cases": ["*"],
   "exclude-cases": [],
   "exclude-agent-cases": {}
}
```

You can tweak that file to run only some tests, e.g. `"cases: ["1.*", "2.1.*"]"` will run only the tests under section 1.* and subsection 2.1.*.


## More Information

For more information take a look at the following information

* [usage instructions](/doc/usage.rst)


## Get in Touch

Get in touch on IRC `#autobahn` on `chat.freenode.net` or join an Autobahn [user forum](https://crossbar.discourse.group/).
