# When on Windows and starting GNU make from Git bash, we need to set this:
#ifdef COMSPEC
#   SHELL=C:/Windows/System32/cmd.exe
#endif

all: clean build upload

install:
	python setup.py install

clean:
	rm -rf ./autobahntestsuite.egg-info
	rm -rf ./build
	rm -rf ./dist
	find . -name '*.pyc' -exec rm -f {} \;

build:
	python setup.py bdist_egg

upload:
	scp dist/*.egg www.tavendo.de:/usr/local/www/pypi

publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_egg upload
	python setup.py bdist_wininst upload

test_sql:
	echo "select count(*) from testresult;" | sqlite3 .wstest.db

test_import:
	python autobahntestsuite/wstest.py -m import -s ../examples/fuzzingwampclient/local.json
	python autobahntestsuite/wstest.py -m import -s ../examples/fuzzingwampclient/local_dual.json
	python autobahntestsuite/wstest.py -m import -s ../examples/fuzzingwampclient/local_dual_webmq.json
	python autobahntestsuite/wstest.py -m import -s ../examples/fuzzingwampclient/local_webmq_sse.json

test_run:
	python autobahntestsuite/wstest.py -m fuzzingwampclient -t 'Local WAMP WebMQ SSE'
	#python autobahntestsuite/wstest.py -m fuzzingwampclient -t 'Local WAMP WebMQ'

test_testee_server:
	python -m autobahntestsuite.wstest -m testeeserver -w ws://127.0.0.1:9001

test_testee_client:
	python -m autobahntestsuite.wstest -m testeeclient -w ws://127.0.0.1:9001

test_broadcast_server:
	python -m autobahntestsuite.wstest -m broadcastserver -w ws://127.0.0.1:9001

test_echo_server:
	python -m autobahntestsuite.wstest -m echoserver -w ws://127.0.0.1:9001

test_fuzzing_server:
	python -m autobahntestsuite.wstest -m fuzzingserver

test_fuzzing_client:
	python -m autobahntestsuite.wstest -m fuzzingclient -w ws://127.0.0.1:9001

test_web:
	python -m autobahntestsuite.wstest -m web

test_help:
	python -m autobahntestsuite.wstest --help

test: test_import test_run test_web
