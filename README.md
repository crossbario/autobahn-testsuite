# Autobahn|Testsuite

The **Autobahn**|Testsuite provides a fully automated test suite to verify client and server implementations of [The WebSocket Protocol](http://tools.ietf.org/html/rfc6455) for specification conformance and implementation robustness.

**Autobahn**|Testsuite also provides a couple of other tools useful for WebSocket
(and [WAMP](http://wamp.ws)) implementors and developers.


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


## How to install

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

To test a **WebSocket server implementation** and generate compliance test reports, start `wstest` in **fuzzing client mode**:

```console
cd ~
mkdir test
cd test
wstest -m fuzzingclient -m
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

> Note: The fuzzingserver mode will also start a Web server on port 8080 which renders a HTML page that allows browser WebSocket clients to be tested.


## More Information

For more information take a look at the [project documentation](http://autobahn.ws/testsuite). This provides:

* [test reports](http://autobahn.ws/testsuite#reports)
* [installation instructions](http://autobahn.ws/testsuite/installation.html)
* [usage instructions](http://autobahn.ws/testsuite/usage.html)


## Get in Touch

Get in touch on IRC `#autobahn` on `chat.freenode.net` or join the [mailing list](http://groups.google.com/group/autobahnws).
