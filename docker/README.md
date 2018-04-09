# Autobahn Testsuite

This folder contains the build infra for creating Docker toolchain images containing [AutobahnTestsuite](https://github.com/crossbario/autobahn-testsuite).

You can use it to test WebSocket server (and client) implementations.


## Usage

By default, the image will run the testsuite in so-called "fuzzingserver" mode. This is the mode used to test your WebSocket _client_ implementations.

To start the testsuite container:

```console
docker run -it --rm \
    -v ${PWD}/config:/config \
    -v ${PWD}/reports:/reports \
    -p 9001:9001 \
    --name fuzzingserver \
    crossbario/autobahn-testsuite
```

Above will mount an (included) test configuration from the [config](config) folder, which must include a server test configuration file [config/fuzzingserver.json](config/fuzzingserver.json) like this:

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

> Above config will run all test cases, but exclude the longer running mass/performance test cases 9.*, and exclude the WebSocket compression test cases 12.*/13.* (which only make sense if your client library implements [RFC7692 ("permessage-deflate")](https://tools.ietf.org/html/rfc7692)).

Above command will also mount a host directory/volume [reports](reports) where the generated reports will be placed by the testsuite.

Finally, the config will make the fuzzing server run on port 9001 - and expose that on the host.

> To test multiple clients and generate one big report containing all clients, do NOT stop the testsuite container, but run all your clients, and then stop the container. The generated reports will include all clients.


## Example

Here is how to test the Python 3 / asyncio flavor of [AutobahnPython](https://github.com/crossbario/autobahn-python):

```console
pip install autobahn
wget https://raw.githubusercontent.com/crossbario/autobahn-python/master/wstest/testee_client_aio.py
python testee_client_aio.py
```
