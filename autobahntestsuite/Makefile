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
	find . -name "*.pyc" -exec rm -f {} \;

build:
	python setup.py bdist_egg

upload:
	scp dist/*.egg www.tavendo.de:/usr/local/www/pypi

publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_egg upload
	python setup.py bdist_wininst upload

test:
	echo "select count(*) from testresult;" | sqlite3 .wstest.db
