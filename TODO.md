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