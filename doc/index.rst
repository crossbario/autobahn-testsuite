|ab|
====

The |ab| provides a fully automated test suite to verify client and server implementations of the `WebSocket Protocol <http://tools.ietf.org/html/rfc6455>`_ for specification conformance and implementation robustness.

|ab| also provides a couple of other tools useful for WebSocket (and `WAMP <http://wamp.ws/>`_) implementors and developers.


For installation, see :ref:`installation`. For usage, please see :ref:`usage`.

.. _reports:

Reports
-------

Check out the test reports:

* older, but more testees

  + `Browsers & Clients <http://autobahn.ws/testsuite/reports/clients/index.html>`_
  + `Mobile <http://autobahn.ws/testsuite/reports/mobileclients/index.html>`_
  + `Servers <http://autobahn.ws/testsuite/reports/servers/index.html>`_

* newer, including WebSocket compression, fewer testees

  + `Browsers & Clients (2013/10) <http://autobahn.ws/testsuite/reports_20131013/clients/index.html>`_
  + `Servers (2013/10) <http://autobahn.ws/testsuite/reports_20131013/servers/index.html>`_
  + `Browsers & Clients (2014/03) <http://autobahn.ws/testsuite/reports_20140314/clients/index.html>`_

`Details on the test setup <https://github.com/tavendo/AutobahnTestSuite/tree/master/examples/publicreports>`_ used with creating the above reports.



Users
-----

Autobahn|Testsuite is used by numerous projects and companies across the industry:

.. raw:: html

   <div class="testsuite_users_table">
      <ul style="float: left; width: 190px">
         <li><a href="http://autobahn.ws">Autobahn</a></li>
         <li><a href="http://www.mozilla.org/" target="_blank">Mozilla Firefox</a></li>
         <li><a href="http://www.chromium.org/Home" target="_blank">Google Chrome / WebKit</a></li>
         <li><a href="http://windows.microsoft.com/en-us/internet-explorer/products/ie/home" target="_blank">Microsoft Internet Explorer</a></li>
         <li><a href="http://www.rim.com/" target="_blank">RIM / Browser</a></li>
         <li><a href="http://www.zaphoyd.com/websocketpp" target="_blank">WebSocket++</a></li>
         <li><a href="http://www.serverframework.com" target="_blank">The Server Framework</a></li>
         <li><a href="http://eclipse.org/jetty/" target="_blank">Jetty</a></li>
         <li><a href="http://netty.io/" target="_blank">Netty</a></li>
         <li><a href="http://grizzly.java.net/" target="_blank">Grizzly</a></li>
         <li><a href="https://github.com/kerryjiang/WebSocket4Net" target="_blank">WebSocket4Net</a></li>
         <li><a href="https://github.com/kerryjiang/SuperWebSocket" target="_blank">SuperWebSocket</a></li>
         <li><a href="https://github.com/webbit/webbit" target="_blank">Webbit</a></li>
         <li><a href="https://github.com/lipp/lua-websockets" target="_blank">lua-websockets</a></li>
      </ul>
      <ul style="float: left; margin-left: 30px; width: 190px">
         <li><a href="http://crossbar.io" target="_blank">Crossbar.io</a></li>
         <li><a href="http://tomcat.apache.org/" target="_blank">Apache Tomcat</a></li>
         <li><a href="https://github.com/Worlize/WebSocket-Node" target="_blank">WebSocket-Node</a></li>
         <li><a href="https://github.com/einaros/ws" target="_blank">WS for node.js</a></li>
         <li><a href="https://github.com/LearnBoost/websocket.io" target="_blank">websocket.io</a></li>
         <li><a href="https://github.com/Lawouach/WebSocket-for-Python" target="_blank">ws4py</a></li>
         <li><a href="https://github.com/facebook/tornado" target="_blank">Facebook Tornado</a></li>
         <li><a href="http://code.google.com/p/pywebsocket/" target="_blank">pywebsocket</a></li>
         <li><a href="http://www.noemax.com/" target="_blank">Noemax PowerWebSockets</a></li>
         <li><a href="http://www.noemax.com/" target="_blank">Noemax WCF-Xtensions</a></li>
         <li><a href="https://github.com/TooTallNate/Java-WebSocket" target="_blank">Java-WebSocket</a></li>
         <li><a href="http://jwebsocket.org/" target="_blank">jWebSocket</a></li>
         <li><a href="https://github.com/aaugustin/websockets" target="_blank">websockets</a></li>
         <li><a href="https://github.com/DamnedFacts/RSWebSocket" target="_blank">RSWebSocket</a></li>
      </ul>
      <ul style="float: left; margin-left: 30px; width: 190px">
         <li><a href="http://cloudsecurity.intel.com/api-management" target="_blank">Intel API Management</a></li>
         <li><a href="http://pusher.com/" target="_blank">Pusher / EM-WebSocket</a></li>
         <li><a href="https://github.com/square/SocketRocket" target="_blank">SocketRocket</a></li>
         <li><a href="https://github.com/DamnedFacts/RSWebSocket" target="_blank">RSWebSocket</a></li>
         <li><a href="http://faye.jcoglan.com/" target="_blank">Faye</a></li>
         <li><a href="https://bitbucket.org/Jeffrey/gevent-websocket/overview" target="_blank">gevent-websocket</a></li>
         <li><a href="https://github.com/extend/cowboy" target="_blank">Cowboy</a></li>
         <li><a href="http://caucho.com/resin-4.0/index.xtp" target="_blank">Resin</a></li>
         <li><a href="http://yaws.hyber.org/" target="_blank">Erlang Yaws</a></li>
         <li><a href="http://wasd.vsm.com.au/wasd/" target="_blank">WASD OpenVMS</a></li>
         <li><a href="http://gitorious.org/qtwebsocket" target="_blank">QtWebSocket</a></li>
         <li><a href="https://github.com/eventlet/eventlet" target="_blank">eventlet</a></li>
         <li><a href="http://code.google.com/p/zaproxy/" target="_blank">zaproxy</a></li>
         <li>... and more (can't keep up)</li>
      </ul>
   </div>
   <div style="clear: both;"></div>


**What users are saying:**


"Autobahn was a huge help during the standardization and early development of WebSocket in `Firefox <http://autobahn.ws/testsuite/www.mozilla.org/firefox>`__. It helped find many nasty corner conditions in a clean and repeatable way.

Interoperation testing like this really moves the Open Web forward."

Patrick McManus, `Mozilla <http://www.mozilla.org/>`_ `Firefox <http://www.mozilla.org/firefox>`_

=================

"The `Jetty project <http://eclipse.org/jetty>`_ has been active in the development of the websocket protocol and lack of a comprehensive test suite was an impediment to the standardisation of the protocol. The Autobahn test suit has filled that void and been warmly embraced by our websocket engineers at `Intalio <http://www.intalio.com/products/jetty/overview/>`__ as it has been invaluable for evaluating the protocol development, improving inter operability and monitoring adoption of new/optional features.

*Our own implementation and the wider websocket 'ecosystem' are significantly better due to the availability of Autobahn*."

Greg Wilkins, `Jetty <http://eclipse.org/jetty>`_ author, Chief Architect at `Intalio <http://www.intalio.com/>`_

==================

"During the time of implementing the latest WebSocket version in `Netty <http://netty.io/>`_ and `Undertow <https://github.com/undertow-io/undertow>`_ we were searching for a way to test our implementations and make sure they are 100% RFC compliant. While we already had unit tests in place there was a lack of good tests for the whole implementation. Using the AutobahnTestsuite for this purpose allowed us to concentrate on the implementation and made it easy to catch regressions as soon as possible."

Norman Maurer, Principal Software Engineer at `Red Hat <http://www.redhat.com/>`_


Test Suite Coverage
-------------------

The test suite will check an implementation by doing basic WebSocket conversations, extensive protocol compliance verification and performance and limits testing.

Contains over 500 test cases covering

* Framing
* Pings/Pongs
* Reserved Bits
* Opcodes
* Fragmentation
* UTF-8 Handling
* Limits/Performance
* Closing Handshake
* Opening Handshake (under development)
* WebSocket compression (`permessage-deflate extension <https://tools.ietf.org/html/draft-ietf-hybi-permessage-compression>`_)


Other Tools
-----------

Besides the automated testsuite (aka "fuzzing" server/client), **wstest** also includes a number of other handy modes that aid WebSocket and WAMP developers:

* WebSocket echo server and client
* WebSocket broadcast server (and client driver)
* Testee modes to test `AutobahnPython <http://autobahn.ws/python>`_ against the test suite
* **wsperf** controller and master (see below for more)
* WAMP server and client, for developing WAMP implementations
* WebSocket Mass-Connect

Please see the :ref:`usage` for further information.


Contact
-------

Get in touch on IRC ``#autobahn`` on ``chat.freenode.net`` or join the `mailing list <http://groups.google.com/group/autobahnws>`_.


.. toctree::
   :hidden:

   installation
   usage
   table_of_contents



Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

