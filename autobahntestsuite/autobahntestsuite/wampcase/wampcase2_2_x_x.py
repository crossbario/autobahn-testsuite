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

__all__ = ['Cases']

## The set of cases we construct and export from this module.
## Everything else is private.
Cases = []


#### BEGIN OF CONFIG

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
## during publishing - see WampCase2_2_x_x_Params
## and what the test case expects for success
##
SETTINGS1 = [
# (peers, publicationTopic, excludeMe, exclude, eligible, expectedReceivers)
   (PEERSET1, TOPIC_PUBLISHED_TO, None, [], None, [1]),
   (PEERSET1, TOPIC_PUBLISHED_TO, True, [], None, [1]),
   (PEERSET1, TOPIC_PUBLISHED_TO, False, [], None, [0, 1]),
   (PEERSET1, TOPIC_PUBLISHED_TO, False, [0], None, [1]),
   (PEERSET1, TOPIC_PUBLISHED_TO, None, [1,], None, [0]),
   (PEERSET1, TOPIC_PUBLISHED_TO, None, [0, 1], None, []),
]

PEERSET2 = [
   [TOPIC_PUBLISHED_TO],
   [TOPIC_PUBLISHED_TO],
   [TOPIC_PUBLISHED_TO, TOPIC_NOT_PUBLISHED_TO],
   [TOPIC_NOT_PUBLISHED_TO],
   []
]

SETTINGS2 = [
   (PEERSET2, TOPIC_PUBLISHED_TO, None, [], None, [1, 2]),
   (PEERSET2, TOPIC_PUBLISHED_TO, True, [], None, [1, 2]),
   (PEERSET2, TOPIC_PUBLISHED_TO, False, [], None, [0, 1, 2]),
   (PEERSET2, TOPIC_PUBLISHED_TO, False, [0], None, [1, 2]),
   (PEERSET2, TOPIC_PUBLISHED_TO, None, [2], None, [0, 1]),
   (PEERSET2, TOPIC_PUBLISHED_TO, None, [1, 2], None, [0]),
   (PEERSET2, TOPIC_PUBLISHED_TO, None, [0, 1, 2], None, []),
]

SETTINGS = SETTINGS1 + SETTINGS2

## The event payloads the publisher sends in one session.
##
## Note: be aware of JSON roundtripping "issues" like
##    (ujson.loads(ujson.dumps(0.1234)) == 0.1234) => False
##
PAYLOADS = [
   [None],
   [100],
   [-0.248], # value has exact representation in _binary_ float (JSON is IEEE binary)
   [-1000000],
   ["hello"],
   [True],
   [False],
   [666, 23, 999],
   [{}],
   [100, "hello", {u'foo': u'bar'}, [1, 2, 3], ["hello", 20, {'baz': 'poo'}]]
]

#### END OF CONFIG


import json, time

from zope.interface import implementer

from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampCraClientProtocol

from testrun import TestResult
from util import AttributeBag
from interfaces import ITestCase


# http://docs.python.org/dev/library/time.html#time.perf_counter
# http://www.python.org/dev/peps/pep-0418/
# until time.perf_counter becomes available in Python 2 we do:
if not hasattr(time, 'perf_counter'):
   import os
   if os.name == 'nt':
      time.perf_counter = time.clock
   else:
      time.perf_counter = time.time



class WampCase2_2_x_x_Protocol(WampCraClientProtocol):


   def onSessionOpen(self):
      if self.test.testee.auth:
         d = self.authenticate(**self.test.testee.auth)
         d.addCallbacks(self.onAuthSuccess, self.onAuthError)
      else:
         self.main()


   def onAuthSuccess(self, permissions):
      self.main()


   def onAuthError(self, e):
      uri, desc, details = e.value.args
      print "Authentication Error!", uri, desc, details


   def main(self):
      subscribeTopics = self.test.params.peers[self.factory.peerIndex]
      for topic in subscribeTopics:
         self.subscribe(topic, self.onEvent)
      self.factory.onReady.callback(self.session_id)


   def onEvent(self, topic, event):
      if not self.test.result.received.has_key(self.session_id):
         self.test.result.received[self.session_id] = []
      self.test.result.received[self.session_id].append((topic, event))



class WampCase2_2_x_x_Factory(WampClientFactory):

   protocol = WampCase2_2_x_x_Protocol

   def __init__(self, test, peerIndex, onReady, onGone):
      WampClientFactory.__init__(self, test.testee.url)
      self.test = test
      self.peerIndex = peerIndex
      self.onReady = onReady
      self.onGone = onGone
      self.proto = None

   def buildProtocol(self, addr):
      proto = self.protocol()
      proto.factory = self
      proto.test = self.test
      self.proto = proto
      return proto

   def clientConnectionLost(self, connector, reason):
      self.onGone.callback(None)

   def clientConnectionFailed(self, connector, reason):
      self.onGone.callback(None)



class WampCase2_2_x_x_Params(AttributeBag):
   """
   Test parameter set for configuring instances of WampCase2_*_*.

   peers: a list with one item per WAMP session run during the test, where each item contains a list of topics each peer _subscribes_ to. The publisher that publishes during the test is always the first item in the list.

   publicationTopic, excludeMe, exclude, eligible: paramters controlling how events are published during the test.

   eventPayloads: a list of payloads each tested as event payload to the test at hand.

   expectedReceivers: a list of session indices, where each index references a WAMP session created for the list in `peers`.
   """

   ATTRIBUTES = ['peers',
                 'publicationTopic',
                 'excludeMe',
                 'exclude',
                 'eligible',
                 'eventPayloads',
                 'expectedReceivers']



@implementer(ITestCase)
class WampCase2_2_x_x_Base:

   DESCRIPTION = "Undefined."
   EXPECTATION = "Undefined."

   def __init__(self, testee):
      self.testee = testee
      self.result = TestResult()
      self.result.received = {}
      self.result.expected = {}
      self.result.log = []


   def run(self):
      self.result.started = time.perf_counter()

      self.clients = []
      peersready = []
      peersgone = []
      i = 1
      for peerIndex in xrange(len(self.params.peers)):
         ready = Deferred()
         gone = Deferred()
         client = WampCase2_2_x_x_Factory(self, peerIndex, ready, gone)
         self.clients.append(client)
         peersready.append(ready)
         peersgone.append(gone)
         connectWS(client)
         i += 1


      def shutdown():
         for c in self.clients:
            c.proto.sendClose()


      def test():
         ## setup what we expected, and what we actually received
         ##
         for c in self.clients:
            self.result.expected[c.proto.session_id] = []
            self.result.received[c.proto.session_id] = []

         expectedReceivers = [self.clients[i] for i in self.params.expectedReceivers]
         for r in expectedReceivers:
            for p in self.params.eventPayloads:
               e = (self.params.publicationTopic, p)
               self.result.expected[r.proto.session_id].append(e)

         publisher = self.clients[0]
         topic = self.params.publicationTopic
         payloads = self.params.eventPayloads
         
         ## map exclude indices to session IDs
         ##
         exclude = []
         for i in self.params.exclude:
            exclude.append(self.clients[i].proto.session_id)

         if self.params.excludeMe is None:
            if len(exclude) > 0:
               for pl in payloads:
                  publisher.proto.publish(topic,
                                          pl,
                                          exclude = exclude)
            else:
               for pl in payloads:
                  publisher.proto.publish(topic, pl)
         else:
            if len(exclude) > 0:
               for pl in payloads:
                  publisher.proto.publish(topic,
                                          pl,
                                          excludeMe = self.params.excludeMe,
                                          exclude = exclude)
            else:
               for pl in payloads:
                  publisher.proto.publish(topic,
                                          pl,
                                          excludeMe = self.params.excludeMe)

         ## after having published everything the test had specified,
         ## we need to _wait_ for events on all our WAMP sessions to
         ## compare with our expectation. by default, we wait 3x the
         ## specified/default RTT
         wait = 3 * self.testee.options.get("rtt", 0.2)
         reactor.callLater(wait, shutdown)


      def launch(_):
         ## FIXME: explain why the following needed, since
         ## without the almost zero delay (which triggers a
         ## reactor loop), the code will not work as expected!

         #test() # <= does NOT work
         reactor.callLater(0.00001, test)


      def error(err):
         ## FIXME
         print "ERROR", err
         shutdown()
         self.finished.errback(err)


      def done(_):
         self.result.ended = time.perf_counter()
         passed = json.dumps(self.result.received) == json.dumps(self.result.expected)
         if not passed:
            print "EXPECTED", self.result.expected
            print "RECEIVED", self.result.received
         self.result.passed = passed
         self.finished.callback(self.result)

      DeferredList(peersready).addCallbacks(launch, error)
      DeferredList(peersgone).addCallbacks(done, error)

      self.finished = Deferred()
      return self.finished



def generate_WampCase2_2_x_x_classes():
   ## dynamically create case classes
   ##
   res = []
   jc = 1
   for setting in SETTINGS:
      ic = 1
      for payload in PAYLOADS:

         params = WampCase2_2_x_x_Params(peers = setting[0],
                                       publicationTopic = setting[1],
                                       excludeMe = setting[2],
                                       exclude = setting[3],
                                       eligible = setting[4],
                                       eventPayloads = payload,
                                       expectedReceivers = setting[5])

         pl = len(params.eventPayloads)
         plc = "s" if pl else ""

         s = []
         i = 0
         for p in params.peers:
            if len(p) > 0:
               s.append("%d: %s" % (i, ' & '.join(p)))
            else:
               s.append("%d: %s" % (i, '-'))
            i += 1
         s = ', '.join(s)

         o = []
         if params.excludeMe is not None:
            o.append("excludeMe = %s" % params.excludeMe)
         if params.exclude is not None:
            o.append("exclude = %s" % params.exclude)
         if params.eligible is not None:
            o.append("eligible = %s" % params.eligible)
         if len(o) > 0:
            o = ', '.join(o)
         else:
            o = "-"

         description = """The test connects %d WAMP clients to the testee, subscribes \
the sessions to topics %s and \
then publishes %d event%s to the topic %s with payload%s %s from the first session. \
The test sets the following publication options: %s.
""" % (len(params.peers),
       s,
       pl,
       plc,
       params.publicationTopic,
       plc,
       ', '.join(['"' + str(x) + '"' for x in params.eventPayloads]),
       o)

         expectation = """We expect the testee to dispatch the events to us on \
the sessions %s""" % (params.expectedReceivers,)

         klassname = "WampCase2_2_%d_%d" % (jc, ic)

         Klass = type(klassname,
                      (object, WampCase2_2_x_x_Base, ),
                      {
                         "__init__": WampCase2_2_x_x_Base.__init__,
                         "run": WampCase2_2_x_x_Base.run,
                         "description": description,
                         "expectation": expectation,
                         "params": params
                       })

         res.append(Klass)
         ic += 1
      jc += 1
   return res



Cases.extend(generate_WampCase2_2_x_x_classes())
