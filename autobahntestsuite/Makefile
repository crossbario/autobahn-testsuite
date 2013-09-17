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

test_run:
	python autobahntestsuite/wstest.py -m fuzzingwampclient -t 'Local WAMP 1'

test_web:
	python autobahntestsuite/wstest.py -m web

test: test_import test_run test_web
