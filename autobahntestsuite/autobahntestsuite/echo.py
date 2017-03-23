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


from autobahn.twisted.websocket import connectWS, \
                                       listenWS, \
                                       WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       WebSocketServerFactory, \
                                       WebSocketServerProtocol


class EchoServerProtocol(WebSocketServerProtocol):

   def onMessage(self, payload, isBinary):
      self.sendMessage(payload, isBinary)



class EchoServerFactory(WebSocketServerFactory):

   protocol = EchoServerProtocol

   def __init__(self, url, debug = False):
      WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debug)



class EchoClientProtocol(WebSocketClientProtocol):

   def onMessage(self, payload, isBinary):
      self.sendMessage(payload, isBinary)



class EchoClientFactory(WebSocketClientFactory):

   protocol = EchoClientProtocol

   def __init__(self, url, debug = False):
      WebSocketClientFactory.__init__(self, url, debug = debug, debugCodePaths = debug)



def startClient(wsuri, debug = False):
   factory = EchoClientFactory(wsuri, debug)
   connectWS(factory)
   return True



def startServer(wsuri, sslKey = None, sslCert = None, debug = False):
   factory = EchoServerFactory(wsuri, debug)
   if sslKey and sslCert:
      sslContext = ssl.DefaultOpenSSLContextFactory(sslKey, sslCert)
   else:
      sslContext = None
   listenWS(factory, sslContext)

   return True
