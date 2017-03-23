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

__all__ = ['Cases']

## The set of cases we construct and export from this module.
## Everything else is private.
Cases = []

import random, json
from pprint import pprint

from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList

from autobahntestsuite.util import AttributeBag
from wampcase import WampCase, WampCaseFactory, WampCaseProtocol



class WampCase4_1_1_Params(AttributeBag):

   ATTRIBUTES = ['peerCount',
                 'topicCount',
                 'subsCount',
                 'pubsCount']


class WampCase4_1_1_Protocol(WampCaseProtocol):

   def test(self):
      ## WAMP session opened and authenticated.

      self.factory.result.observed[self.session_id] = {}
      self.factory.result.expected[self.session_id] = {}

      self._topics = []

      expected = self.factory.result.expected
      observed = self.factory.result.observed

      for i in xrange(self.factory.test.params.subsCount):

         topic = "http://example.com/simple#" + str(random.randint(0, self.factory.test.params.topicCount))
         self.subscribe(topic, self.onEvent)

         expected[self.session_id][topic] = 0
         observed[self.session_id][topic] = 0

         self._topics.append(topic)

      ## Signal the test controller our readiness.
      self.ready()

   def monkeyPublish(self, event):
      i = random.randint(0, len(self._topics) - 1)
      topic = self._topics[i]
      self.publish(topic, event, excludeMe = False)
      #print topic

      expected = self.factory.result.expected
      rcnt = 0
      for e in expected:
         if expected[e].has_key(topic):
            expected[e][topic] += 1
            rcnt += 1
      self.factory.totalExpected += rcnt


   def onEvent(self, topic, event):
      observed = self.factory.result.observed[self.session_id]
      if not observed.has_key(topic):
         observed[topic] = 0
      observed[topic] += 1
      self.factory.totalObserved += 1

      print self.factory.totalObserved, self.factory.totalExpected



class WampCase4_1_1_Factory(WampCaseFactory):

   protocol = WampCase4_1_1_Protocol

   def buildProtocol(self, addr):
      proto = WampCaseFactory.buildProtocol(self, addr)
      self.totalExpected = 0
      self.totalObserved = 0
      return proto




class WampCase4_1_1(WampCase):

   index = (4, 1, 1, 0)
   factory = WampCase4_1_1_Factory
   params = WampCase4_1_1_Params(peerCount = 10,
                                 topicCount = 10,
                                 subsCount = 5,
                                 pubsCount = 200)

   description = "A NOP test."
   expectation = "Nothing."



   def test(self, log, result, clients):
      msg = "NOP test running using %d sessions\n" % len(clients)
      log(msg)
      print msg

      for i in xrange(self.params.pubsCount):
         j = random.randint(0, len(clients) - 1)
         clients[j].proto.monkeyPublish("Hello, world!")
      result.passed = True

      d = Deferred()
      wait = 80 * self._rtt

      def afterwait():
         log("Continuing test ..")

         if False:
            print
            print "Expected:"
            for r in result.expected:
               print r
               pprint(result.expected[r])
               print

            print
            print "Observed:"
            for r in result.observed:
               print r
               pprint(result.observed[r])
               print

         result.passed = json.dumps(result.observed) == json.dumps(result.expected)

         d.callback(None)

      def beforewait():
         log("Sleeping for  <strong>%s ms</strong> ..." % (1000. * wait))
         reactor.callLater(wait, afterwait)

      beforewait()
      return d


Cases.append(WampCase4_1_1)
