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


from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File

import autobahn

from autobahn.twisted.websocket import connectWS, listenWS

from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol

from autobahn.websocket.compress import *



class TesteeServerProtocol(WebSocketServerProtocol):

   def onMessage(self, payload, isBinary):
      self.sendMessage(payload, isBinary)


class StreamingTesteeServerProtocol(WebSocketServerProtocol):

   def onMessageBegin(self, isBinary):
      #print "onMessageBegin"
      WebSocketServerProtocol.onMessageBegin(self, isBinary)
      self.beginMessage(isBinary = isBinary)

   def onMessageFrameBegin(self, length):
      #print "onMessageFrameBegin"
      WebSocketServerProtocol.onMessageFrameBegin(self, length)
      self.beginMessageFrame(length)

   def onMessageFrameData(self, data):
      #print "onMessageFrameData", len(data)
      self.sendMessageFrameData(data)

   def onMessageFrameEnd(self):
      #print "onMessageFrameEnd"
      pass

   def onMessageEnd(self):
      #print "onMessageEnd"
      self.endMessage()


class TesteeServerFactory(WebSocketServerFactory):

   protocol = TesteeServerProtocol
   #protocol = StreamingTesteeServerProtocol

   def __init__(self, url, debug = False, ident = None):
      if ident is not None:
         server = ident
      else:
         server = "AutobahnPython/%s" % autobahn.version
      WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debug, server = server)
      self.setProtocolOptions(failByDrop = False) # spec conformance
      #self.setProtocolOptions(failByDrop = True) # needed for streaming mode
      #self.setProtocolOptions(utf8validateIncoming = False)

      ## enable permessage-XXX compression extensions
      ##
      def accept(offers):
         for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
               return PerMessageDeflateOfferAccept(offer)

            elif isinstance(offer, PerMessageBzip2Offer):
               return PerMessageBzip2OfferAccept(offer)

            elif isinstance(offer, PerMessageSnappyOffer):
               return PerMessageSnappyOfferAccept(offer)

      self.setProtocolOptions(perMessageCompressionAccept = accept)



class TesteeClientProtocol(WebSocketClientProtocol):

   def onOpen(self):
      if self.factory.endCaseId is None:
         print "Getting case count .."
      elif self.factory.currentCaseId <= self.factory.endCaseId:
         print "Running test case %d/%d as user agent %s on peer %s" % (self.factory.currentCaseId, self.factory.endCaseId, self.factory.agent, self.peer)

   def onMessage(self, msg, binary):
      if self.factory.endCaseId is None:
         self.factory.endCaseId = int(msg)
         print "Ok, will run %d cases" % self.factory.endCaseId
      else:
         self.sendMessage(msg, binary)



class TesteeClientFactory(WebSocketClientFactory):

   protocol = TesteeClientProtocol

   def __init__(self, url, debug = False, ident = None):
      WebSocketClientFactory.__init__(self, url, useragent = ident, debug = debug, debugCodePaths = debug)
      self.setProtocolOptions(failByDrop = False) # spec conformance

      ## enable permessage-XXX compression extensions
      ##
      offers = [PerMessageDeflateOffer()]
      #offers = [PerMessageSnappyOffer(), PerMessageBzip2Offer(), PerMessageDeflateOffer()]
      self.setProtocolOptions(perMessageCompressionOffers = offers)

      def accept(response):
         if isinstance(response, PerMessageDeflateResponse):
            return PerMessageDeflateResponseAccept(response)

         elif isinstance(response, PerMessageBzip2Response):
            return PerMessageBzip2ResponseAccept(response)

         elif isinstance(response, PerMessageSnappyResponse):
            return PerMessageSnappyResponseAccept(response)

      self.setProtocolOptions(perMessageCompressionAccept = accept)


      self.endCaseId = None
      self.currentCaseId = 0

      self.updateReports = True
      if ident is not None:
         self.agent = ident
      else:
         self.agent = "AutobahnPython/%s" % autobahn.version
      self.resource = "/getCaseCount"

   def clientConnectionLost(self, connector, reason):
      self.currentCaseId += 1
      if self.currentCaseId <= self.endCaseId:
         self.resource = "/runCase?case=%d&agent=%s" % (self.currentCaseId, self.agent)
         connector.connect()
      elif self.updateReports:
         self.resource = "/updateReports?agent=%s" % self.agent
         self.updateReports = False
         connector.connect()
      else:
         reactor.stop()

   def clientConnectionFailed(self, connector, reason):
      print "Connection to %s failed (%s)" % (self.url, reason.getErrorMessage())
      reactor.stop()



def startClient(wsuri, ident = None, debug = False):
   factory = TesteeClientFactory(wsuri, ident = ident, debug = debug)
   connectWS(factory)
   return True



def startServer(wsuri, webport = None, sslKey = None, sslCert = None, debug = False):
   factory = TesteeServerFactory(wsuri, debug)
   if sslKey and sslCert:
      sslContext = ssl.DefaultOpenSSLContextFactory(sslKey, sslCert)
   else:
      sslContext = None
   listenWS(factory, sslContext)

   if webport:
      webdir = File(pkg_resources.resource_filename("autobahntestsuite", "web/echoserver"))
      web = Site(webdir)
      reactor.listenTCP(webport, web)

   return True
