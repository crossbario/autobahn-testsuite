.PHONY: clean build

all: clean install build publish

clean:
	rm -rf ./autobahntestsuite.egg-info
	rm -rf ./build
	rm -rf ./dist
	find . -name '*.pyc' -exec rm -f {} \;
	rm -f ./*.json
	rm -rf ./reports
	rm -f ./.wstest.db

install:
	python setup.py install

build:
	# use py 2 to build
	python setup.py sdist bdist_wheel --universal

publish:
	# use py 3 to upload
	~/cpy365_11/bin/twine upload dist/*


# Usage: wstest [options]
# Options:
#   -a, --autobahnversion  Print version information for Autobahn and
#                          AutobahnTestSuite.
#   -c, --cert=            Server certificate file for secure WebSocket (WSS)
#                          [required in server modes for WSS].
#   -d, --debug            Debug output [default: off].
#       --help             Display this help and exit.
#   -i, --ident=           Testee client identifier [optional for client testees].
#   -k, --key=             Server private key file for secure WebSocket (WSS)
#                          [required in server modes for WSS].
#   -m, --mode=            Test mode, one of: echoserver, echoclient,
#                          broadcastclient, broadcastserver, fuzzingserver,
#                          fuzzingclient, testeeserver, testeeclient, massconnect,
#                          serializer [required]
#   -o, --outfile=         Output filename for modes that generate testdata.
#   -s, --spec=            Test specification file [required in some modes].
#   -t, --testset=         Run a test set from an import test spec.
#   -u, --webport=         Web port for running an embedded HTTP Web server;
#                          defaults to 8080; set to 0 to disable. [optionally used
#                          in some modes: fuzzingserver, echoserver,
#                          broadcastserver, wsperfmaster]. [default: 8080]
#       --version          Display Twisted version and exit.
#   -w, --wsuri=           WebSocket URI [required in some modes].

test_testee_server:
	python -m autobahntestsuite.wstest -m testeeserver -w ws://127.0.0.1:9001

test_testee_client:
	python -m autobahntestsuite.wstest -m testeeclient -w ws://127.0.0.1:9001

test_fuzzing_server:
	python -m autobahntestsuite.wstest -m fuzzingserver

test_fuzzing_client:
	python -m autobahntestsuite.wstest -m fuzzingclient -w ws://127.0.0.1:9001


test_echo_server:
	python -m autobahntestsuite.wstest -m echoserver -w ws://127.0.0.1:9001

test_echo_client:
	python -m autobahntestsuite.wstest -m echoclient -w ws://127.0.0.1:9001


test_broadcast_server:
	python -m autobahntestsuite.wstest -m broadcastserver -w ws://127.0.0.1:9001

test_broadcast_client:
	python -m autobahntestsuite.wstest -m broadcastclient -w ws://127.0.0.1:9001


test_web:
	python -m autobahntestsuite.wstest -m web


test_help:
	python -m autobahntestsuite.wstest --help
