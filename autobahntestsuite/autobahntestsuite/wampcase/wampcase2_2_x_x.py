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


import json

from zope.interface import implementer

from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampCraClientProtocol

from testrun import TestResult
from util import AttributeBag, perf_counter
from interfaces import ITestCase



class WampCase2_2_x_x_Protocol(WampCraClientProtocol):


   def onSessionOpen(self):
      self.test.result.log.append((perf_counter(), self.factory.peerIndex, self.session_id, "WAMP session opened to <strong>%s</strong> at <strong>%s</strong>." % (self.session_server ,self.peerstr)))
      if self.test.testee.auth:
         d = self.authenticate(**self.test.testee.auth)
         d.addCallbacks(self.onAuthSuccess, self.onAuthError)
      else:
         self.main()


   def onAuthSuccess(self, permissions):
      self.test.result.log.append((perf_counter(), self.factory.peerIndex, self.session_id, "WAMP session %s authenticated with credentials: <pre>%s</pre>" % (self.session_id, self.test.testee.auth)))
      self.main()


   def onAuthError(self, e):
      uri, desc, details = e.value.args
      self.test.result.log.append((perf_counter(), self.factory.peerIndex, self.session_id, "WAMP authentication error: %s" % details))
      print "Authentication Error!", uri, desc, details


   def main(self):
      subscribeTopics = self.test.params.peers[self.factory.peerIndex]
      for topic in subscribeTopics:
         self.subscribe(topic, self.onEvent)
         self.test.result.log.append((perf_counter(), self.factory.peerIndex, self.session_id, "Subscribed to <pre>%s</pre>" % topic))
      self.factory.onReady.callback(self.session_id)


   def onEvent(self, topic, event):
      self.test.result.log.append((perf_counter(), self.factory.peerIndex, self.session_id, "Received event for topic <pre>%s</pre> and payload <pre>%s</pre>" % (topic, event)))
      if not self.test.result.observed.has_key(self.session_id):
         self.test.result.observed[self.session_id] = []
      self.test.result.observed[self.session_id].append((topic, event))



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
      reason = str(reason.value)
      if self.proto and hasattr(self.proto, 'session_id'):
         sid = self.proto.session_id
      else:
         sid = None
      self.test.result.log.append((perf_counter(), self.peerIndex, sid, "Client connection lost: %s" % reason))
      self.onGone.callback(None)

   def clientConnectionFailed(self, connector, reason):
      reason = str(reason.value)
      self.test.result.log.append((perf_counter(), self.peerIndex, None, "Client connection failed: %s" % reason))
      self.onGone.callback(reason)



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

   def __init__(self, testee):
      self.testee = testee
      self.result = TestResult()
      self.result.passed = False
      self.result.observed = {}
      self.result.expected = {}
      self.result.log = []


   def run(self):
      self.result.started = perf_counter()
      self.result.log.append((self.result.started, None, None, "Test started."))

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
            self.result.observed[c.proto.session_id] = []

         expectedReceivers = [self.clients[i] for i in self.params.expectedReceivers]
         for r in expectedReceivers:
            for p in self.params.eventPayloads:
               e = (self.params.publicationTopic, p)
               self.result.expected[r.proto.session_id].append(e)

         publisherPeerIndex = 0
         publisher = self.clients[publisherPeerIndex]
         topic = self.params.publicationTopic
         payloads = self.params.eventPayloads
         
         ## map exclude indices to session IDs
         ##
         exclude = []
         for i in self.params.exclude:
            exclude.append(self.clients[i].proto.session_id)

         def plog(topic, pl, opts = None):
            if opts:
               self.result.log.append((perf_counter(),
                                       publisherPeerIndex,
                                       publisher.proto.session_id,
                                       "Published event to topic <pre>%s</pre> with options <pre>%s</pre> and payload <pre>%s</pre>" % (topic, ', '.join(opts), pl)))
            else:
               self.result.log.append((perf_counter(),
                                       publisherPeerIndex,
                                       publisher.proto.session_id,
                                       "Published event to topic <pre>%s</pre> and payload <pre>%s</pre>" % (topic, pl)))

         if self.params.excludeMe is None:
            if len(exclude) > 0:
               for pl in payloads:
                  publisher.proto.publish(topic,
                                          pl,
                                          exclude = exclude)
                  plog(topic, pl, ["exclude=%s" % exclude])
            else:
               for pl in payloads:
                  publisher.proto.publish(topic,
                                          pl)
                  plog(topic, pl)
         else:
            if len(exclude) > 0:
               for pl in payloads:
                  publisher.proto.publish(topic,
                                          pl,
                                          excludeMe = self.params.excludeMe,
                                          exclude = exclude)
                  plog(topic, pl, ["exclude=%s" % exclude, "excludeMe=%s" % self.params.excludeMe])
            else:
               for pl in payloads:
                  publisher.proto.publish(topic,
                                          pl,
                                          excludeMe = self.params.excludeMe)
                  plog(topic, pl, ["excludeMe=%s" % self.params.excludeMe])

         ## After having published everything the test had specified,
         ## we need to _wait_ to receive events on all our WAMP sessions
         ## to compare with our expectation. By default, we wait 3x the
         ## specified/default RTT.
         ##
         wait = 3 * self.testee.options.get("rtt", 0.2)
         def afterwait():
            self.result.log.append((perf_counter(), None, None, "Continuing test .."))
            shutdown()
         self.result.log.append((perf_counter(), None, None, "Sleeping for <strong>%s ms</strong> ..." % (1000. * wait)))
         reactor.callLater(wait, afterwait)


      def launch(_):
         ## After all our clients have signaled "peersready", these
         ## clients will just have sent their subscribe WAMP messages,
         ## and since with WAMPv1, there is no reply (to wait on), the
         ## clients immediately signal readiness and we need to _wait_
         ## here to give the testee time to receive and actually subscribe
         ## the clients. When we don't wait, we might publish test events
         ## before the testee has subscribed all clients as needed.
         ## We need acknowledgement of subscribe for WAMPv2!
         ##
         wait = 3 * self.testee.options.get("rtt", 0.2)
         def afterwait():
            self.result.log.append((perf_counter(), None, None, "Continuing test .."))
            test()
         self.result.log.append((perf_counter(), None, None, "Sleeping for  <strong>%s ms</strong> ..." % (1000. * wait)))
         reactor.callLater(wait, afterwait)


      def error(err):
         ## FIXME
         print "ERROR", err
         shutdown()
         self.finished.errback(err)


      def done(res):
         self.result.ended = perf_counter()
         self.result.log.append((self.result.ended, None, None, "Test ended."))

         clientErrors = []
         for r in res:
            if not r[0]:
               clientErrors.append(str(r[1].value))

         if len(clientErrors) > 0:
            passed = False
            print "Client errors", clientErrors
         else:
            passed = json.dumps(self.result.observed) == json.dumps(self.result.expected)
            if not passed:
               print
               print "EXPECTED"
               print self.result.expected
               print "OBSERVED"
               print self.result.observed
               print

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
the sessions to topics %s, waits 3x <RTT> seconds and \
then publishes %d event%s to the topic %s with payload%s %s from the first session. \
The test then waits 3x <RTT> seconds to receive events dispatched from the testee.
For publishing of test events, the following publication options are used: %s.
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
         index = (2, 2, jc, ic)

         Klass = type(klassname,
                      (object, WampCase2_2_x_x_Base, ),
                      {
                         "__init__": WampCase2_2_x_x_Base.__init__,
                         "run": WampCase2_2_x_x_Base.run,
                         "index": index,
                         "description": description,
                         "expectation": expectation,
                         "params": params
                       })

         res.append(Klass)
         ic += 1
      jc += 1
   return res



Cases.extend(generate_WampCase2_2_x_x_classes())
