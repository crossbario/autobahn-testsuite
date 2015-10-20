# Public Testsuite Reports

This document describes how we create the reports [published](http://autobahn.ws/testsuite) on the Autobahn website:

  * [Servers](http://autobahn.ws/testsuite/reports/servers/index.html)
  * [Browsers](http://autobahn.ws/testsuite/reports/clients/index.html)
  * [Mobile](http://autobahn.ws/testsuite/reports/mobileclients/index.html)


## Test Setup

All testing is done between testees and fuzzers running in VMs.

The host system is:

  * Intel Core i7 @ 3.3 GHz, 12 GB Ram
  * Microsoft Windows 7 SP1 Professional 64 Bit
  * Oracle VirtualBox 4.2

The guest systems (VMs) are:

  * Ubuntu 12.04 LTS 64 Bit (Desktop)
  * 4 Cores, 3 GB Ram
  * VT-x / Nested Paging enabled

The VMs are (for testing traffic) connected via a VirtualBox host only network.


## Servers

There are dozens of WebSocket capable servers. We cannot test all, too much work.
Hence, we selected a few (subjective):

 * [Autobahn](https://github.com/crossbario/autobahn-python) - Python/Twisted
 * [Jetty](http://eclipse.org/jetty/) - Java/NIO
 * [Cowboy](https://github.com/extend/cowboy) - Erlang/OTP
 * [WebSocket++](https://github.com/zaphoyd/websocketpp) - C++/ASIO
 * [ws](https://github.com/einaros/ws) - JavaScript/NodeJS


The whole testsuite is run 5x times without restarting servers, only taking the last generated report. This allows JITting VMs to warm up.


### Jetty

[Jetty](http://eclipse.org/jetty/) can act as a WebSocket server.

Current versions of Jetty require a JDK7, so we do

    sudo apt-get install openjdk-7-jdk
    sudo update-alternatives --config java
    sudo update-alternatives --config javac

and add the following to `$HOME/.profile`

    export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-amd64/

and

    source $HOME/.profile

We then clone the testee repo, build and run

    cd $HOME/scm
    git clone git://github.com/jetty-project/jetty-autobahn-websocket-webapp.git
    cd jetty-autobahn-websocket-webapp
    mvn clean install
    mvn exec:exec

The test server will run (by default) on port `9001`.


### WebSocket++

[WebSocket++](https://github.com/zaphoyd/websocketpp) is a C++/ASIO based WebSocket library.

We will build everything from source. First Boost:

    cd $HOME/tarballs
    wget http://downloads.sourceforge.net/project/boost/boost/1.53.0/boost_1_53_0.tar.bz2
    cd ../build
    tar xvjf ../tarballs/boost_1_53_0.tar.bz2
    cd boost_1_53_0
    ./bootstrap.sh
    ./b2

and add the following to `$HOME/.profile`

    export BOOST_ROOT=/home/oberstet/build/boost_1_53_0

and

    source $HOME/.profile

WebSocket++ uses [SCons](http://www.scons.org/) as build tool

    sudo apt-get install scons

We then clone the repo and build

    cd $HOME/scm
    git://github.com/zaphoyd/websocketpp.git
    cd websocketpp
    git checkout experimental
    scons

And start the testee server

    ./build/release/testee_server/testee_server

which will run (by default) on port `9002`.


### ws

[ws](https://github.com/einaros/ws) is a WebSocket library for NodeJS.

The NodeJS packaged with Ubuntu is too old, so we

    cd $HOME/tarballs
    wget http://nodejs.org/dist/v0.10.5/node-v0.10.5-linux-x64.tar.gz
    cd ../local
    tar xvzf ../tarballs/node-v0.10.5-linux-x64.tar.gz

and add the following to `$HOME/.profile`

    export PATH=$HOME/local/node-v0.10.5-linux-x64/bin:$PATH

and

    source $HOME/.profile

We then need

    npm install -g node-gyp

clone the repo and build **ws**

    cd $HOME/scm
    git clone git://github.com/einaros/ws.git
    cd ws
    make
    npm install options

and then start the server

    node test/autobahn-server.js

which will run (by default) on port `8181`.


### Cowboy

The Erlang/OTP packaged with Ubuntu is too old, so we install the build deps

    sudo apt-get install ncurses-dev

and

    cd $HOME/tarballs
    wget http://www.erlang.org/download/otp_src_R16B.tar.gz
    cd ../build
    tar xvzf ../tarballs/otp_src_R16B.tar.gz
    cd otp_src_R16B
    ./configure --prefix=$HOME/local/erlang_otp_R16B
    make
    make install

and add the following to `$HOME/.profile`

    export PATH=$HOME/local/erlang_otp_R16B/bin:$PATH

and

    source $HOME/.profile

Get, build and install `rebar`

    cd $HOME/scm
    git clone git://github.com/rebar/rebar.git
    cd rebar
    ./bootstrap
    cp ./rebar $HOME/local

add the following to `$HOME/.profile`

    export PATH=$HOME/local:$PATH

and

    source $HOME/.profile

Then get and build the Cowboy testee

    cd $HOME/scm
    git://github.com/oberstet/cowboy-autobahn-testee.git
    cd cowboy-autobahn-testee
    cd websocket
    rebar get-deps compile
    ./start.sh

This will run the server on WebSocket URL `ws://localhost:9009/websocket`.


### Autobahn

[Autobahn](https://github.com/crossbario/autobahn-python) is a Python/Twisted based WebSocket/WAMP library.

We will test Autobahn running under 3 run-time environments:

   1. plain CPython
   2. CPython with wsaccel WebSocket acceleration
   3. PyPy


**plain CPython**

Create a virtual env:

    /usr/bin/virtualenv -p /usr/bin/python $HOME/python273_2

Install Setuptools:

    cd ~/build/setuptools-0.6c11
    $HOME/python273_2/bin/python setup.py install

Install AutobahnPython:

    cd $HOME/scm/AutobahnPython/autobahn/
    $HOME/python273_2/bin/python setup.py install

Install AutobahnTestSuite:

    cd $HOME/scm/AutobahnTestSuite/autobahntestsuite
    $HOME/python273_2/bin/python setup.py install

Run:

    $HOME/python273_2/bin/wstest -m testeeserver -w ws://localhost:9006


**CPython with wsaccel**

Create a virtual env:

    /usr/bin/virtualenv -p /usr/bin/python $HOME/python273_1

Install Setuptools:

    cd ~/build/setuptools-0.6c11
    $HOME/python273_1/bin/python setup.py install

Install wsaccel:

    $HOME/python273_1/bin/easy_install wsaccel

Install AutobahnPython:

    cd $HOME/scm/AutobahnPython/autobahn/
    $HOME/python273_1/bin/python setup.py install

Install AutobahnTestSuite:

    cd $HOME/scm/AutobahnTestSuite/autobahntestsuite
    $HOME/python273_1/bin/python setup.py install

Run:

    $HOME/python273_1/bin/wstest -m testeeserver -w ws://localhost:9000


**PyPy**

Get and install PyPy:

    cd $HOME/tarballs
    wget https://bitbucket.org/pypy/pypy/downloads/pypy-2.0-beta2-linux64-libc2.15.tar.bz2
    cd ../local
    tar xvjf ../tarballs/pypy-2.0-beta2-linux64-libc2.15.tar.bz2

add the following to `$HOME/.profile`

    export PATH=$HOME/pypy20b2_1/bin:$PATH

and

    source $HOME/.profile

Create virtualenv:

    $HOME/local/pypy-2.0-beta2/bin/virtualenv -p $HOME/pypy20b2_1/bin/pypy $HOME/pypy20b2_1

Install Setuptools:

    cd ~/build/setuptools-0.6c11
    $HOME/pypy20b2_1/bin/pypy setup.py install

Install AutobahnPython:

    cd $HOME/scm/AutobahnPython/autobahn/
    $HOME/pypy20b2_1/bin/pypy setup.py install

Install AutobahnTestSuite:

    cd $HOME/scm/AutobahnTestSuite/autobahntestsuite
    $HOME/pypy20b2_1/bin/pypy setup.py install

