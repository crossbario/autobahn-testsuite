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

__all__ = ['startClient']


import time, sys

from twisted.internet import defer, reactor
from twisted.internet.defer import Deferred, returnValue, inlineCallbacks

from autobahn.twisted.websocket import connectWS, \
                                       WebSocketClientFactory, \
                                       WebSocketClientProtocol


class MassConnectProtocol(WebSocketClientProtocol):

   didHandshake = False

   def onOpen(self):
      ## WebSocket opening handshake complete => log
      self.factory.test.onConnected()
      self.factory.test.protos.append(self)
      self.didHandshake = True


class MassConnectFactory(WebSocketClientFactory):

   protocol = MassConnectProtocol

   def clientConnectionFailed(self, connector, reason):
      if self.test.onFailed():
         reactor.callLater(float(self.retrydelay)/1000., connector.connect)

   def clientConnectionLost(self, connector, reason):
      if self.test.onLost():
         reactor.callLater(float(self.retrydelay)/1000., connector.connect)


class MassConnect:

   def __init__(self, name, uri, connections, batchsize, batchdelay, retrydelay):
      self.name = name
      self.uri = uri
      self.batchsize = batchsize
      self.batchdelay = batchdelay
      self.retrydelay = retrydelay
      self.failed = 0
      self.lost = 0
      self.targetCnt = connections
      self.currentCnt = 0
      self.actual = 0
      self.protos = []

   def run(self):
      self.d = Deferred()
      self.started = time.clock()
      self.connectBunch()
      return self.d

   def onFailed(self):
      self.failed += 1
      sys.stdout.write("!")
      return True

   def onLost(self):
      self.lost += 1
      #sys.stdout.write("*")
      return False
      return True

   def onConnected(self):
      self.actual += 1
      if self.actual % self.batchsize == 0:
         sys.stdout.write(".")
      if self.actual == self.targetCnt:
         self.ended = time.clock()
         duration = self.ended - self.started
         print " connected %d clients to %s at %s in %s seconds (retries %d = failed %d + lost %d)" % (self.currentCnt, self.name, self.uri, duration, self.failed + self.lost, self.failed, self.lost)
         result = {'name': self.name,
                   'uri': self.uri,
                   'connections': self.targetCnt,
                   'retries': self.failed + self.lost,
                   'lost': self.lost,
                   'failed': self.failed,
                   'duration': duration}
         for p in self.protos:
            p.sendClose()
         #self.d.callback(result)

   def connectBunch(self):
      if self.currentCnt + self.batchsize < self.targetCnt:
         c = self.batchsize
         redo = True
      else:
         c = self.targetCnt - self.currentCnt
         redo = False
      for i in xrange(0, c):
         factory = MassConnectFactory(self.uri)
         factory.test = self
         factory.retrydelay = self.retrydelay
         connectWS(factory)
         self.currentCnt += 1
      if redo:
         reactor.callLater(float(self.batchdelay)/1000., self.connectBunch)


class MassConnectTest:
   def __init__(self, spec):
      self.spec = spec

   @inlineCallbacks
   def run(self):
      print self.spec
      res = []
      for s in self.spec['servers']:
         t = MassConnect(s['name'],
                         s['uri'],
                         self.spec['options']['connections'],
                         self.spec['options']['batchsize'],
                         self.spec['options']['batchdelay'],
                         self.spec['options']['retrydelay'])
         r = yield t.run()
         res.append(r)
      returnValue(res)


def startClient(spec, debug = False):
   test = MassConnectTest(spec)
   d = test.run()
   return d
