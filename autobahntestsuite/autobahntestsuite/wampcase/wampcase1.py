###############################################################################
##
##  Copyright 2013 Tavendo GmbH
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

__all__ = ["WampCase1_1", "WampCase1_2", "WampCase1_3"]


import sys, pickle, json
from pprint import pprint


from twisted.python import log
from twisted.internet import reactor

from twisted.internet.defer import Deferred, DeferredList

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, \
                          WampClientProtocol



class WampCase1:

   class TestProtocol(WampClientProtocol):

      def onSessionOpen(self):
         for topic in self.factory.subscribeTopics:
            self.subscribe(topic, self.onEvent)            
         self.factory.onReady.callback(self.session_id)

      def onEvent(self, topic, event):
         if not self.factory.case.received.has_key(self.session_id):
            self.factory.case.received[self.session_id] = []
         self.factory.case.received[self.session_id].append((topic, event))


   class TestFactory(WampClientFactory):

      def __init__(self, case, onReady, onGone, subscribeTopics):
         WampClientFactory.__init__(self, case.url, debug = case.debugWs, debugWamp = case.debugWamp)
         self.case = case
         self.onReady = onReady
         self.onGone = onGone
         self.subscribeTopics = subscribeTopics

      def buildProtocol(self, addr):
         self.proto = WampCase1.TestProtocol()
         self.proto.factory = self
         return self.proto

      def clientConnectionLost(self, connector, reason):
         #print "clientConnectionLost"
         self.onGone.callback(None)


      def clientConnectionFailed(self, connector, reason):
         #print "clientConnectionFailed"
         self.onGone.callback(None)


   def __init__(self, url, debugWs = False, debugWamp = False):
      self.url = url
      self.debugWs = debugWs
      self.debugWamp = debugWamp

      self.received = {}
      self.expected = {}

      self.subscribedTopic = "http://example.com/simple"
      self.notSubscribedTopic = "http://example.com/foobar"

      self.sentIndex = 0
      self.toSend = [None,
                     100,
                     0.1234,
                     -1000000,
                     u"Foobar",
                     True,
                     False,
                     [1, 2, 3],
                     {u'foo': u'bar'},
                     [range(1,10), range(1,10)],
                     ]


   def done(self, _):
      res = (json.dumps(self.received) == json.dumps(self.expected), self.expected, self.received)
      self.finished.callback(res)


   def shutdown(self):
      for c in self.clients:
         c.proto.sendClose()


   def run(self):
      debug = False

      d1 = Deferred()
      g1 = Deferred()
      c1 = WampCase1.TestFactory(self, d1, g1, subscribeTopics = [self.subscribedTopic])
      connectWS(c1)

      d2 = Deferred()
      g2 = Deferred()
      c2 = WampCase1.TestFactory(self, d2, g2, subscribeTopics = [self.subscribedTopic])
      connectWS(c2)

      d3 = Deferred()
      g3 = Deferred()
      c3 = WampCase1.TestFactory(self, d3, g3, subscribeTopics = [self.subscribedTopic, self.notSubscribedTopic])
      connectWS(c3)

      d4 = Deferred()
      g4 = Deferred()
      c4 = WampCase1.TestFactory(self, d4, g4, subscribeTopics = [self.notSubscribedTopic])
      connectWS(c4)

      d5 = Deferred()
      g5 = Deferred()
      c5 = WampCase1.TestFactory(self, d5, g5, subscribeTopics = [])
      connectWS(c5)

      self.clients = [c1, c2, c3, c4, c5]


      def dotest():
         if self.sentIndex < len(self.toSend):
            #print "publish from ", c1.proto.session_id
            if self.EXCLUDE_ME is None:
               c1.proto.publish(self.subscribedTopic, self.toSend[self.sentIndex])
            else:               
               c1.proto.publish(self.subscribedTopic, self.toSend[self.sentIndex], excludeMe = self.EXCLUDE_ME)
            self.sentIndex += 1
            reactor.callLater(0, dotest)
            #dotest()
         else:
            #self.shutdown()
            reactor.callLater(0.5, self.shutdown)

      def connected(res):
         ## setup what we expected, and what we actually received
         ##
         for c in self.clients:
            self.expected[c.proto.session_id] = []
            self.received[c.proto.session_id] = []

         if self.EXCLUDE_ME is None or self.EXCLUDE_ME:
            receivers = [c2, c3]
         else:
            receivers = [c1, c2, c3]

         for c in receivers:
            for d in self.toSend:
               self.expected[c.proto.session_id].append((self.subscribedTopic, d))

         reactor.callLater(0.1, dotest)
         #dotest()


      DeferredList([d1, d2, d3, d4, d5]).addCallback(connected)

      DeferredList([g1, g2, g3, g4, g5]).addCallback(self.done)

      self.finished = Deferred()
      return self.finished


class WampCase1_1(WampCase1):
   EXCLUDE_ME = None

   DESCRIPTION = """Connect 4 consumers. """

   EXPECTATION = """Receive echo'ed text message (with payload as sent). Clean close with normal code."""


class WampCase1_2(WampCase1):
   EXCLUDE_ME = True

class WampCase1_3(WampCase1):
   EXCLUDE_ME = False
