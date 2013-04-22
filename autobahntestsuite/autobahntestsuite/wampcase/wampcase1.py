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

__all__ = ["WampCase1_x_x"]


import sys, pickle, json, time
from pprint import pprint


from twisted.python import log
from twisted.internet import reactor

from twisted.internet.defer import Deferred, DeferredList

from autobahn.websocket import WebSocketClientProtocol, connectWS

from autobahn.wamp import WampClientFactory, \
                          WampClientProtocol



class WampCase1_x_x_Base:

   class TestProtocol(WampClientProtocol):

      def sendMessage(self, payload, binary = False):
         session_id = self.session_id if hasattr(self, 'session_id') else None
         now = round(1000000 * (time.clock() - self.factory.case.started))
         rec = (now, session_id, "TX", payload)
         self.factory.case.wampLog.append(rec)
         WebSocketClientProtocol.sendMessage(self, payload, binary)

      def onMessage(self, payload, binary):
         session_id = self.session_id if hasattr(self, 'session_id') else None
         now = round(1000000 * (time.clock() - self.factory.case.started))
         rec = (now, session_id, "RX", payload)
         self.factory.case.wampLog.append(rec)
         WampClientProtocol.onMessage(self, payload, binary)


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
         self.proto = WampCase1_x_x_Base.TestProtocol()
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
      self.wampLog = []

      self.sentIndex = 0


   def done(self, _):
      res = (json.dumps(self.received) == json.dumps(self.expected), self.expected, self.received, self.wampLog)
      self.finished.callback(res)


   def shutdown(self):
      for c in self.clients:
         c.proto.sendClose()


   def run(self):
      debug = False
      self.started = time.clock()

      self.clients = []
      fireOnConnected = []
      fireOnClosed = []
      i = 1
      for c in self.settings.PEERS:
         d = Deferred()
         g = Deferred()
         c = WampCase1_x_x_Base.TestFactory(self, d, g, subscribeTopics = c)
         c.name = "Peer %d" % i
         self.clients.append(c)
         fireOnConnected.append(d)
         fireOnClosed.append(g)
         connectWS(c)
         i += 1

      def dotest():
         if self.sentIndex < len(self.payloads):

            publisher = self.clients[0]
            #print "publish from ", publisher.proto.session_id

            ## map exclude indices to session IDs
            ##
            exclude = []
            for i in self.settings.EXCLUDE:
               exclude.append(self.clients[i].proto.session_id)

            if self.settings.EXCLUDE_ME is None:
               if len(exclude) > 0:
                  publisher.proto.publish(self.settings.PUBLICATION_TOPIC, self.payloads[self.sentIndex], exclude = exclude)
               else:
                  publisher.proto.publish(self.settings.PUBLICATION_TOPIC, self.payloads[self.sentIndex])
            else:
               if len(exclude) > 0:
                  publisher.proto.publish(self.settings.PUBLICATION_TOPIC, self.payloads[self.sentIndex], excludeMe = self.settings.EXCLUDE_ME, exclude = exclude)
               else:
                  publisher.proto.publish(self.settings.PUBLICATION_TOPIC, self.payloads[self.sentIndex], excludeMe = self.settings.EXCLUDE_ME)
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

         receivers = [self.clients[i] for i in self.settings.RECEIVERS]

         for c in receivers:
            for d in self.payloads:
               self.expected[c.proto.session_id].append((self.settings.PUBLICATION_TOPIC, d))

         reactor.callLater(0.1, dotest)
         #dotest()

      def error(err):
         print err

      DeferredList(fireOnConnected).addCallbacks(connected, error)
      DeferredList(fireOnClosed).addCallbacks(self.done, error)

      self.finished = Deferred()
      return self.finished


## the set of cases we construct and export from this module
##
WampCase1_x_x = []

class Settings:
   def __init__(self, peers, publicationTopic, excludeMe, exclude, eligible, receivers):
      self.PEERS = peers
      self.PUBLICATION_TOPIC = publicationTopic
      self.EXCLUDE_ME = excludeMe
      self.EXCLUDE = exclude
      self.ELIGIBLE = eligible
      self.RECEIVERS = receivers


## the topic our test publisher will publish to
##
TOPIC_PUBLISHED_TO = "http://example.com/simple"

## some topic the test publisher will NOT publish to
##
TOPIC_NOT_PUBLISHED_TO = "http://example.com/foobar"


## for each peer, list of topics the peer subscribes to
## the publisher is always the first peer in this list
##
PEERSET1 = [
              [TOPIC_PUBLISHED_TO],
              [TOPIC_PUBLISHED_TO]
           ]

## these settings control the options the publisher uses
## during publishing
##
SETTINGS1 = [Settings(PEERSET1, TOPIC_PUBLISHED_TO, None, [], None, [1]),
             Settings(PEERSET1, TOPIC_PUBLISHED_TO, True, [], None, [1]),
             Settings(PEERSET1, TOPIC_PUBLISHED_TO, False, [], None, [0, 1]),
             Settings(PEERSET1, TOPIC_PUBLISHED_TO, False, [0], None, [1]),
             Settings(PEERSET1, TOPIC_PUBLISHED_TO, None, [1,], None, [0]),
             Settings(PEERSET1, TOPIC_PUBLISHED_TO, None, [0, 1], None, []),
            ]

PEERSET2 = [
              [TOPIC_PUBLISHED_TO],
              [TOPIC_PUBLISHED_TO],
              [TOPIC_PUBLISHED_TO, TOPIC_NOT_PUBLISHED_TO],
              [TOPIC_NOT_PUBLISHED_TO],
              []
           ]

SETTINGS2 = [Settings(PEERSET2, TOPIC_PUBLISHED_TO, None, [], None, [1, 2]),
             Settings(PEERSET2, TOPIC_PUBLISHED_TO, True, [], None, [1, 2]),
             Settings(PEERSET2, TOPIC_PUBLISHED_TO, False, [], None, [0, 1, 2]),
             Settings(PEERSET2, TOPIC_PUBLISHED_TO, False, [0], None, [1, 2]),
             Settings(PEERSET2, TOPIC_PUBLISHED_TO, None, [2], None, [0, 1]),
             Settings(PEERSET2, TOPIC_PUBLISHED_TO, None, [1, 2], None, [0]),
             Settings(PEERSET2, TOPIC_PUBLISHED_TO, None, [0, 1, 2], None, []),
            ]

## the event payload the publisher sends in one session
##
PAYLOADS = [[None],
            [100],
            [0.1234],
            [-1000000],
            ["hello"],
            [True],
            [False],
            [666, 23, 999],
            [{}],
            [100, "hello", {u'foo': u'bar'}, [1, 2, 3], ["hello", 20, {'baz': 'poo'}]]
            ]

## now dynamically create case classes
##
j = 1
for s in SETTINGS1:
   i = 1
   for d in PAYLOADS:
      DESCRIPTION = ""
      EXPECTATION = ""
      C = type("WampCase1_%d_%d" % (j, i),
               (object, WampCase1_x_x_Base, ),
               {"__init__": WampCase1_x_x_Base.__init__,
                "run": WampCase1_x_x_Base.run,
                "DESCRIPTION": """%s""" % DESCRIPTION,
                "EXPECTATION": """%s""" % EXPECTATION,
                "payloads": d,
                "settings": s})
      WampCase1_x_x.append(C)
      i += 1
   j += 1
