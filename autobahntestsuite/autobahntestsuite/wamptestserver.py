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

import math, shelve, decimal

from twisted.internet import reactor, defer

from autobahn.wamp1.protocol import exportRpc, \
                                    exportSub, \
                                    exportPub, \
                                    WampServerFactory, \
                                    WampServerProtocol


class Simple:
   """
   A simple calc service we will export for Remote Procedure Calls (RPC).

   All you need to do is use the @exportRpc decorator on methods
   you want to provide for RPC and register a class instance in the
   server factory (see below).

   The method will be exported under the Python method name, or
   under the (optional) name you can provide as an argument to the
   decorator (see asyncSum()).
   """

   @exportRpc
   def add(self, x, y):
      return x + y

   @exportRpc
   def sub(self, x, y):
      return x - y

   @exportRpc
   def square(self, x):
      if x > 1000:
         ## raise a custom exception
         raise Exception("http://example.com/error#number_too_big",
                         "number %d too big to square" % x)
      return x * x

   @exportRpc
   def sum(self, list):
      return reduce(lambda x, y: x + y, list)

   @exportRpc
   def pickySum(self, list):
      errs = []
      for i in list:
         if i % 3 == 0:
            errs.append(i)
      if len(errs) > 0:
         raise Exception("http://example.com/error#invalid_numbers",
                         "one or more numbers are multiples of 3", errs)
      return reduce(lambda x, y: x + y, list)

   @exportRpc
   def sqrt(self, x):
      return math.sqrt(x)

   @exportRpc("asum")
   def asyncSum(self, list):
      ## Simulate a slow function.
      d = defer.Deferred()
      reactor.callLater(3, d.callback, self.sum(list))
      return d


class KeyValue:
   """
   Simple, persistent key-value store.
   """

   def __init__(self, filename):
      self.store = shelve.open(filename)

   @exportRpc
   def set(self, key = None, value = None):
      if key is not None:
         k = str(key)
         if value is not None:
            self.store[k] = value
         else:
            if self.store.has_key(k):
               del self.store[k]
      else:
         self.store.clear()

   @exportRpc
   def get(self, key = None):
      if key is None:
         return self.store.items()
      else:
         return self.store.get(str(key), None)

   @exportRpc
   def keys(self):
      return self.store.keys()



class Calculator:
   """
   Woooohoo. Simple decimal arithmetic calculator.
   """

   def __init__(self):
      self.clear()

   def clear(self, arg = None):
      self.op = None
      self.current = decimal.Decimal(0)

   @exportRpc
   def calc(self, arg):

      op = arg["op"]

      if op == "C":
         self.clear()
         return str(self.current)

      num = decimal.Decimal(arg["num"])
      if self.op:
         if self.op == "+":
            self.current += num
         elif self.op == "-":
            self.current -= num
         elif self.op == "*":
            self.current *= num
         elif self.op == "/":
            self.current /= num
         self.op = op
      else:
         self.op = op
         self.current = num

      res = str(self.current)
      if op == "=":
         self.clear()

      return res


class MyTopicService:

   def __init__(self, allowedTopicIds):
      self.allowedTopicIds = allowedTopicIds
      self.serial = 0


   @exportSub("foobar", True)
   def subscribe(self, topicUriPrefix, topicUriSuffix):
      """
      Custom topic subscription handler.
      """
      print "client wants to subscribe to %s%s" % (topicUriPrefix, topicUriSuffix)
      try:
         i = int(topicUriSuffix)
         if i in self.allowedTopicIds:
            print "Subscribing client to topic Foobar %d" % i
            return True
         else:
            print "Client not allowed to subscribe to topic Foobar %d" % i
            return False
      except:
         print "illegal topic - skipped subscription"
         return False


   @exportPub("foobar", True)
   def publish(self, topicUriPrefix, topicUriSuffix, event):
      """
      Custom topic publication handler.
      """
      print "client wants to publish to %s%s" % (topicUriPrefix, topicUriSuffix)
      try:
         i = int(topicUriSuffix)
         if type(event) == dict and event.has_key("count"):
            if event["count"] > 0:
               self.serial += 1
               event["serial"] = self.serial
               print "ok, published enriched event"
               return event
            else:
               print "event count attribute is negative"
               return None
         else:
            print "event is not dict or misses count attribute"
            return None
      except:
         print "illegal topic - skipped publication of event"
         return None



class WampTestServerProtocol(WampServerProtocol):

   def onSessionOpen(self):
      self.initSimpleRpc()
      self.initKeyValue()
      self.initCalculator()
      self.initSimplePubSub()
      self.initPubSubAuth()

   def initSimpleRpc(self):
      ## Simple RPC
      self.simple = Simple()
      self.registerForRpc(self.simple, "http://example.com/simple/calc#")

   def initKeyValue(self):
      ## Key-Value Store
      self.registerForRpc(self.factory.keyvalue, "http://example.com/simple/keyvalue#")

   def initCalculator(self):
      ## Decimal Calculator
      self.calculator = Calculator()
      self.registerForRpc(self.calculator, "http://example.com/simple/calculator#")

   def initSimplePubSub(self):
      ## register a single, fixed URI as PubSub topic
      self.registerForPubSub("http://example.com/simple")

      ## register a URI and all URIs having the string as prefix as PubSub topic
      self.registerForPubSub("http://example.com/event#", True)

      ## register any URI (string) as topic
      #self.registerForPubSub("", True)

   def initPubSubAuth(self):
      ## register a single, fixed URI as PubSub topic
      self.registerForPubSub("http://example.com/event/simple")

      ## register a URI and all URIs having the string as prefix as PubSub topic
      #self.registerForPubSub("http://example.com/event/simple", True)

      ## register any URI (string) as topic
      #self.registerForPubSub("", True)

      ## register a topic handler to control topic subscriptions/publications
      self.topicservice = MyTopicService([1, 3, 7])
      self.registerHandlerForPubSub(self.topicservice, "http://example.com/event/")



class WampTestServerFactory(WampServerFactory):

   protocol = WampTestServerProtocol

   def __init__(self, url, debug = False):
      WampServerFactory.__init__(self, url, debugWamp = debug)
      self.setProtocolOptions(allowHixie76 = True)

      ## the key-value store resides on the factory object, since it is to
      ## be shared among all client connections
      self.keyvalue = KeyValue("keyvalue.dat")

      decimal.getcontext().prec = 20
