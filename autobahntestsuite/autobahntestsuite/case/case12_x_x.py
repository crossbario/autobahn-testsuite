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

__all__ = ['Case12_X_X', 'Case12_X_X_CaseSubCategories']

import copy, os, pkg_resources

from case import Case
from autobahn.compress import *

## list of (payload length, message count, case timeout)
tests = [(16,     1000, 60),
         (64,     1000, 60),
         (256,    1000, 120),
         (1024,   1000, 240),
         (4096,   1000, 480),
         (8192,   1000, 480),
         (16384,  1000, 480),
         (32768,  1000, 480),
         (65536,  1000, 480),
         (131072, 1000, 480),
         ]


WS_COMPRESSION_TESTDATA = {
   'gutenberg_faust':
      {'desc': "Human readable text, Goethe's Faust I (German)",
       'url': 'http://www.gutenberg.org/cache/epub/2229/pg2229.txt',
       'file': 'pg2229.txt',
       'binary': True
       },
   'lena512':
      {'desc': 'Lena Picture, Bitmap 512x512 bw',
       'url': 'http://www.ece.rice.edu/~wakin/images/lena512.bmp',
       'file': 'lena512.bmp',
       'binary': True
       },
   'ooms':
      {'desc': 'A larger PDF',
       'url': 'http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.105.5439',
       'file': '10.1.1.105.5439.pdf',
       'binary': True
       },
   'json_data1':
      {'desc': 'Large JSON data file',
       'url': None,
       'file': 'data1.json',
       'binary': False
       },
   'html_data1':
      {'desc': 'Large HTML file',
       'url': None,
       'file': 'data1.html',
       'binary': False
       }
}


Case12_X_X = []


def __init__(self, protocol):
   Case.__init__(self, protocol)


def init(self):
   self.reportTime = True
   self.reportCompressionRatio = True

   self.expectedClose = {"closedByMe": True,
                         "closeCode": [self.p.CLOSE_STATUS_CODE_NORMAL],
                         "requireClean": True}

   if self.p.factory.isServer:
      def accept(offers):
         for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
               #offer.requestMaxWindowBits = 8
               #offer.requestNoContextTakeover = True
               return PerMessageDeflateOfferAccept(offer)
               #return PerMessageDeflateOfferAccept(offer, True, 8, windowBits = 8)
               #return PerMessageDeflateOfferAccept(offer, True, 8, noContextTakeover = True, windowBits = 8)

            #elif isinstance(offer, PerMessageBzip2Offer):
            #   return PerMessageBzip2OfferAccept(offer)

            #elif isinstance(offer, PerMessageSnappyOffer):
            #   return PerMessageSnappyOfferAccept(offer)

      self.p.perMessageCompressionAccept = accept
   else:
#      self.p.perMessageCompressionOffers = [PerMessageBzip2Offer(), PerMessageSnappyOffer(), PerMessageDeflateOffer()]
      self.p.perMessageCompressionOffers = [PerMessageDeflateOffer()]

      def accept(response):
         if isinstance(response, PerMessageDeflateResponse):
            return PerMessageDeflateResponseAccept(response)

      self.p.perMessageCompressionAccept = accept


   self.payloadRXPtr = 0
   self.payloadTXPtr = 0

   fn = pkg_resources.resource_filename("autobahntestsuite", "testdata/%s" % self.TESTDATA['file'])
   self.testData = open(fn, 'rb').read()
   self.testDataLen = len(self.testData)


def onOpen(self):
   self.p.enableWirelog(False)

   if self.p._perMessageCompress is None:
      self.behavior = Case.UNIMPLEMENTED
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL)
   else:
      self.behavior = Case.FAILED
      self.result = "Case did not finish within %d seconds." % self.WAITSECS
      self.p.closeAfter(self.WAITSECS)
      self.count = 0
      self.sendOne()


def sendOne(self):
   if self.LEN > 0:
      idxFrom = self.payloadRXPtr
      idxTo = (self.payloadRXPtr + self.LEN) % self.testDataLen
      if idxTo > idxFrom:
         msg = self.testData[idxFrom:idxTo]
      else:
         msg = self.testData[idxFrom:] + self.testData[:idxTo]
      self.payloadRXPtr = idxTo
   else:
      msg = ''

   self.p.sendMessage(msg, self.TESTDATA['binary'])
   self.count += 1


def onMessage(self, msg, binary):
   if binary != self.TESTDATA['binary'] or len(msg) != self.LEN:
      self.behavior = Case.FAILED
      self.result = "Echo'ed message type or length differs from what I sent (got binary = %s, payload length = %s)." % (binary, len(msg))
      self.p.enableWirelog(True)
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL)
   elif self.count < self.COUNT:
      self.sendOne()
   else:
      self.behavior = Case.OK
      self.result = "Ok, received all echo'ed messages in time."
      self.trafficStats = copy.deepcopy(self.p.trafficStats)
      self.p.enableWirelog(True)
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL)


Case12_X_X_CaseSubCategories = {}

j = 1
for td in WS_COMPRESSION_TESTDATA:

   isBinary = WS_COMPRESSION_TESTDATA[td]["binary"]
   fn = pkg_resources.resource_filename("autobahntestsuite", "testdata/%s" % WS_COMPRESSION_TESTDATA[td]['file'])
   fileSize = os.path.getsize(fn)

   Case12_X_X_CaseSubCategories['12.%d' % j] = WS_COMPRESSION_TESTDATA[td]["desc"] + (" (%s, %s bytes)" % ("binary" if isBinary else "utf8", fileSize))

   i = 1
   for s in tests:
      cc = "Case12_%d_%d" % (j, i)
      DESCRIPTION = """Send %d messages of payload size %d to measure implementation/network RTT (round trip time) / latency.""" % (s[1], s[0])
      EXPECTATION = """Receive echo'ed messages (with payload as sent). Timeout case after %d secs.""" % (s[2])
      C = type(cc,
                (object, Case, ),
                {"LEN": s[0],
                 "COUNT": s[1],
                 "WAITSECS": s[2],
                 "TESTDATA": WS_COMPRESSION_TESTDATA[td],
                 "DESCRIPTION": """%s""" % DESCRIPTION,
                 "EXPECTATION": """%s""" % EXPECTATION,
                 "__init__": __init__,
                 "init": init,
                 "onOpen": onOpen,
                 "onMessage": onMessage,
                 "sendOne": sendOne,
                 })
      Case12_X_X.append(C)
      i += 1
   j += 1
