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

__all__ = ['startClient', 'startServer']

import pkg_resources
import os, socket, binascii

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import connectWS, \
                                       listenWS, \
                                       WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       WebSocketServerFactory, \
                                       WebSocketServerProtocol


class BroadcastServerProtocol(WebSocketServerProtocol):

   def onOpen(self):
      self.factory.register(self)

   def onClose(self, wasClean, code, reason):
      self.factory.unregister(self)

   def onMessage(self, payload, isBinary):
      self.factory.broadcast(payload, isBinary)



class BroadcastServerFactory(WebSocketServerFactory):

   protocol = BroadcastServerProtocol

   def __init__(self, url, debug = False):
      WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debug)

   def startFactory(self):
      self.clients = set()
      self.tickcount = 0
      self.tick()

   def register(self, client):
      self.clients.add(client)

   def unregister(self, client):
      self.clients.discard(client)

   def broadcast(self, payload, isBinary = False):
      for c in self.clients:
         c.sendMessage(payload, isBinary)

   def tick(self):
      self.tickcount += 1
      self.broadcast("tick %d" % self.tickcount)
      reactor.callLater(1, self.tick)



class BroadcastClientProtocol(WebSocketClientProtocol):

   def sendHello(self):
      self.sendMessage("hello from %s[%d]" % (socket.gethostname(), os.getpid()))
      reactor.callLater(2, self.sendHello)

   def onOpen(self):
      self.sendHello()

   def onMessage(self, payload, isBinary):
      if isBinary:
         print "received: ", binascii.b2a_hex(payload)
      else:
         print "received: ", payload



class BroadcastClientFactory(WebSocketClientFactory):

   protocol = BroadcastClientProtocol

   def __init__(self, url, debug = False):
      WebSocketClientFactory.__init__(self, url, debug = debug, debugCodePaths = debug)



def startClient(wsuri, debug = False):
   factory = BroadcastClientFactory(wsuri, debug)
   connectWS(factory)
   return True



def startServer(wsuri, webport, sslKey = None, sslCert = None, debug = False):
   factory = BroadcastServerFactory(wsuri, debug)
   if sslKey and sslCert:
      sslContext = ssl.DefaultOpenSSLContextFactory(sslKey, sslCert)
   else:
      sslContext = None
   listenWS(factory, sslContext)

   if webport:
      webdir = File(pkg_resources.resource_filename("autobahntestsuite", "web/broadcastserver"))
      web = Site(webdir)
      reactor.listenTCP(webport, web)

   return True
