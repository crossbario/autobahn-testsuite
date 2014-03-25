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


## More Information

For more information take a look at the [project documentation](http://autobahn.ws/testsuite). This provides:

 * [test reports](http://autobahn.ws/testsuite#reports)
 * [installation instructions](http://autobahn.ws/testsuite/installation)
 * [usage instructions](http://autobahn.ws/testsuite/usage)


## Get in Touch

Get in touch on IRC `#autobahn` on `chat.freenode.net` or join the [mailing list](http://groups.google.com/group/autobahnws).
