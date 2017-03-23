###############################################################################
##
##  Copyright (c) Crossbar.io Technologies GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

__all__ = ('WampCase', 'WampCaseProtocol', 'WampCaseFactory',)


import json, random

from zope.interface import implementer

from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList, maybeDeferred

from autobahn.twisted.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampCraClientProtocol

from autobahntestsuite.testrun import TestResult
from autobahntestsuite.util import AttributeBag, perf_counter
from autobahntestsuite.interfaces import ITestCase



class WampCaseProtocol(WampCraClientProtocol):


   def sendMessage(self, payload):
      self.factory.log('<pre class="wamp">TX => %s</pre>' % payload)
      WampCraClientProtocol.sendMessage(self, payload)


   def onMessage(self, payload, binary):
      self.factory.log('<pre class="wamp">RX <= %s</pre>' % payload)
      WampCraClientProtocol.onMessage(self, payload, binary)


   def onSessionOpen(self):
      self.factory.log("WAMP session opened to <strong>%s</strong> at <strong>%s</strong>." % (self.session_server, self.peer))

      self.factory.result.observed[self.session_id] = []

      if self.factory.test.testee.auth:
         d = self.authenticate(**self.factory.test.testee.auth)
         d.addCallbacks(self.onAuthSuccess, self.onAuthError)
      else:
         self.test()


   def onAuthSuccess(self, permissions):
      self.factory.log("WAMP session %s authenticated with credentials: <pre>%s</pre>" % (self.session_id, self.factory.test.testee.auth))
      self.test()


   def onAuthError(self, e):
      uri, desc, details = e.value.args
      self.factory.log("WAMP authentication error: %s" % details)
      self.sendClose()


   def test(self):
      raise Exception("not implemented")


   def ready(self):
      self.factory.log("Test client prepared and ready.")
      self.factory.onReady.callback(self.session_id)


   def onEvent(self, topic, event):
      self.factory.log("Received event for topic <pre>%s</pre> and payload <pre>%s</pre>" % (topic, event))
      self.factory.result.observed[self.session_id].append((topic, event))


class WampCaseParams(AttributeBag):
   """
   """

   ATTRIBUTES = ['peerCount']


class WampCaseFactory(WampClientFactory):

   protocol = None

   def __init__(self, peerIndex, onReady, onGone, test, result):
      assert(self.protocol)
      WampClientFactory.__init__(self, test.testee.url)
      self.peerIndex = peerIndex
      self.onReady = onReady
      self.onGone = onGone
      self.test = test
      self.result = result
      self.proto = None

   def buildProtocol(self, addr):
      proto = self.protocol()
      proto.factory = self
      proto.session_id = None
      self.proto = proto
      return proto

   def log(self, msg):
      ts = perf_counter()
      sessionId = self.proto.session_id if self.proto else None
      self.result.log.append((ts, self.peerIndex, sessionId, msg.encode('utf8')))
      return ts

   def clientConnectionLost(self, connector, reason):
      reason = str(reason.value)
      self.log("Client connection lost: %s" % reason)
      self.onGone.callback(None)

   def clientConnectionFailed(self, connector, reason):
      reason = str(reason.value)
      self.log("Client connection failed: %s" % reason)
      self.onGone.callback(reason)



@implementer(ITestCase)
class WampCase:

   factory = None
   index = None
   description = None
   expectation = None
   params = None


   def __init__(self, testee, spec):
      self.testee = testee
      self.spec = spec

      self._uriSuffix = '#' + str(random.randint(0, 1000000))

      if self.testee.options.has_key('rtt'):
         self._rtt = self.testee.options['rtt']
      elif self.spec.has_key('options') and self.spec['options'].has_key('rtt'):
         self._rtt = self.spec['options']['rtt']
      else:
         self._rtt = 0.2


   def test(self, result, clients):
      raise Exception("not implemented")


   def run(self):
      assert(self.factory)
      assert(self.index)
      assert(self.params)

      result = TestResult()
      finished = Deferred()

      result.passed = None
      result.observed = {}
      result.expected = {}
      result.log = []

      def log(msg, sessionIndex = None, sessionId = None):
         ts = perf_counter()
         result.log.append((ts, sessionIndex, sessionId, msg.encode('utf8')))
         return ts

      result.started = log("Test started.")

      clients = []
      peersready = []
      peersgone = []
      i = 1
      for peerIndex in xrange(self.params.peerCount):
         ready = Deferred()
         gone = Deferred()
         client = self.factory(peerIndex, ready, gone, self, result)
         clients.append(client)
         peersready.append(ready)
         peersgone.append(gone)
         connectWS(client)
         i += 1

      def shutdown(_):
         for client in clients:
            client.proto.sendClose()
            log("Test client closing ...", client.peerIndex, client.proto.session_id)

      def launch(_):
         wait = 2.5 * self._rtt

         def afterwait():
            log("Continuing test ..")
            d = maybeDeferred(self.test, log, result, clients)
            d.addCallback(shutdown)

         def beforewait():
            log("Sleeping for  <strong>%s ms</strong> ..." % (1000. * wait))
            reactor.callLater(wait, afterwait)

         beforewait()

      def error(err):
         ## FIXME
         print "ERROR", err
         shutdown()
         finished.errback(err)


      def done(res):
         result.ended = log("Test ended.")

         for r in res:
            if not r[0]:
               log("Client error: %s" % r[1].value)

         #assert(result.passed is not None)

         finished.callback(result)

      DeferredList(peersready).addCallbacks(launch, error)
      DeferredList(peersgone).addCallbacks(done, error)

      return finished
