	7.28076860152 zhPFDGHq6nYYGMwx WAMP session opened.
	7.28087985356 zhPFDGHq6nYYGMwx Subscribed to http://example.com/simple
	7.2811200656 gza8OkMLy6OELEv2 WAMP session opened.
	7.28123824684 gza8OkMLy6OELEv2 Subscribed to http://example.com/simple, http://example.com/foobar
	7.2814060873 HePw8IieAMtUEdk6 WAMP session opened.
	7.28147845887 HePw8IieAMtUEdk6 Subscribed to http://example.com/foobar
	7.28165130375 VgcggREjPE_0kzTr WAMP session opened.
	7.28165361348 VgcggREjPE_0kzTr Subscribed to
	7.28181029024 c-g4xbnEe_5vXsel WAMP session opened.
	7.28187611757 c-g4xbnEe_5vXsel Subscribed to http://example.com/simple
	7.28189575029 None Waiting 30.0 ms ...
	7.31130055183 c-g4xbnEe_5vXsel Sent event for topic http://example.com/simple: -0.248
	7.31131094562 None Waiting 30.0 ms ...
	7.31212127628 zhPFDGHq6nYYGMwx Received event for topic http://example.com/simple: -0.248
	7.31226178492 gza8OkMLy6OELEv2 Received event for topic http://example.com/simple: -0.248
	7.34231023153 zhPFDGHq6nYYGMwx Client connection lost: Connection was closed cleanly.
	7.34271520438 gza8OkMLy6OELEv2 Client connection lost: Connection was closed cleanly.
	7.34292692973 HePw8IieAMtUEdk6 Client connection lost: Connection was closed cleanly.
	7.34328416814 VgcggREjPE_0kzTr Client connection lost: Connection was closed cleanly.
	7.34359598184 c-g4xbnEe_5vXsel Client connection lost: Connection was closed cleanly.
	PASSED   : WampCase2_2_8_3 (57 tests remaining)



 * case log
 * parallel
 * webmq test cases: configure webmq over admin session, test over test session

# Code Structure

The principle steps the `wstest` tool needs to perform are:

 1. parse and check the command line args
 2. if no spec file is there, auto-generate one
 3. load the spec file
 4. given a spec file, generate a list of test runs
 5. a test run contains a list of test classes


    [TestRun, TestRun]

# WAMP Testing

## Modes

We want to test:

 * WAMP client (libraries)
 * WAMP server (frameworks)
 * WAMP integration servers (Tavendo WebMQ, PGV8)
 * federated/clustered setups

## Functional

Tests which verify and cover every functional aspect of WAMP.

## Compliance

Tests which send invalid WAMP messages. Test if the peer recognizes those and bails out.

 * message structure
 * message types
 * message element types

## Performance

Tests which measure throughput, latency and so on.