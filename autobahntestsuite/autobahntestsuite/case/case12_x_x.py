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

__all__ = ['Case12_X_X',
           'Case12_X_X_CaseSubCategories',
           'Case13_X_X',
           'Case13_X_X_CaseSubCategories',
           ]

import copy, os, pkg_resources, hashlib, binascii

from case import Case
from autobahn.websocket.compress import *


## list of (payload length, message count, case timeout, auto-fragment size)
##
MSG_SIZES = [
   (16,     1000, 60 , 0),
   (64,     1000, 60 , 0),
   (256,    1000, 120, 0),
   (1024,   1000, 240, 0),
   (4096,   1000, 480, 0),
   (8192,   1000, 480, 0),
   (16384,  1000, 480, 0),
   (32768,  1000, 480, 0),
   (65536,  1000, 480, 0),
   (131072, 1000, 480, 0),

   (8192,   1000, 480, 256),
   (16384,  1000, 480, 256),
   (32768,  1000, 480, 256),
   (65536,  1000, 480, 256),
   (131072, 1000, 480, 256),
   (131072, 1000, 480, 1024),
   (131072, 1000, 480, 4096),
   (131072, 1000, 480, 32768),
]

## test data set
##
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

# explicit iteration order to fix order as it was historically on python 2 (dict order)
WS_COMPRESSION_TESTDATA_KEYS = ['json_data1', 'lena512', 'gutenberg_faust', 'html_data1', 'ooms']


def __init__(self, protocol):
   Case.__init__(self, protocol)


def init(self):
   self.reportTime = True
   self.reportCompressionRatio = True

   self.expectedClose = {"closedByMe": True,
                         "closeCode": [self.p.CLOSE_STATUS_CODE_NORMAL],
                         "requireClean": True}

   ## permessage-deflate setup
   ##
   if self.p.factory.isServer:
      self.p.perMessageCompressionAccept = self.SERVER_ACCEPT

   else:
      self.p.perMessageCompressionOffers = self.CLIENT_OFFERS

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
   self.p.autoFragmentSize = self.AUTOFRAGSIZE

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
   payload = self.testData
   if not self.TESTDATA['binary']:
      # If we're not working with a "binary" payload, treat it as a unicode string
      payload = payload.decode('utf-8')
   if self.LEN > 0:
      idxFrom = self.payloadRXPtr
      idxTo = (self.payloadRXPtr + self.LEN) % len(payload)
      if idxTo > idxFrom:
         msg = payload[idxFrom:idxTo]
      else:
         msg = payload[idxFrom:] + payload[:idxTo]
      self.payloadRXPtr = idxTo
   else:
      msg = ''

   if not self.TESTDATA['binary']:
      msg = msg.encode('utf-8')

   m = hashlib.sha1()
   m.update(msg)
   self._expected_hash = m.digest()

   self.p.sendMessage(msg, self.TESTDATA['binary'])
   self.count += 1


def onMessage(self, msg, binary):
   m = hashlib.sha1()
   m.update(msg)
   received_hash = m.digest()
   if not self.TESTDATA['binary']:
      msg = msg.decode('utf-8')

   if binary != self.TESTDATA['binary'] or len(msg) != self.LEN or received_hash != self._expected_hash:

      self.behavior = Case.FAILED
      self.p.enableWirelog(True)
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL)

      if binary != self.TESTDATA['binary']:
         self.result = "Echo'ed message type differs from what I sent (got binary {0}, expected binary {1}).".format(binary, self.TESTDATA['binary'])

      elif len(msg) != self.LEN:
         self.result = "Echo'ed message length differs from what I sent (got length {0}, expected length {1}).".format(len(msg), self.LEN)

      elif received_hash != self._expected_hash:
         self.result = "Echo'ed message contents differs from what I sent (got SHA1 {0}, expected SHA1 {1}).".format(binascii.hexlify(received_hash), binascii.hexlify(self._expected_hash))

      else:
         ## should not arrive here
         raise Exception("logic error")

   elif self.count < self.COUNT:
      self.sendOne()

   else:
      self.behavior = Case.OK
      self.result = "Ok, received all echo'ed messages in time."
      self.trafficStats = copy.deepcopy(self.p.trafficStats)
      self.p.enableWirelog(True)
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL)



##
## Cases 12.x.x
##
Case12_X_X = []
Case12_X_X_CaseSubCategories = {}

def accept_deflate(self, offers):
   for offer in offers:
      if isinstance(offer, PerMessageDeflateOffer):
         return PerMessageDeflateOfferAccept(offer)

j = 1
for td in WS_COMPRESSION_TESTDATA_KEYS:

   isBinary = WS_COMPRESSION_TESTDATA[td]["binary"]
   fn = pkg_resources.resource_filename("autobahntestsuite", "testdata/%s" % WS_COMPRESSION_TESTDATA[td]['file'])
   fileSize = os.path.getsize(fn)

   Case12_X_X_CaseSubCategories['12.%d' % j] = WS_COMPRESSION_TESTDATA[td]["desc"] + (" (%s, %s bytes)" % ("binary" if isBinary else "utf8", fileSize))

   i = 1
   for s in MSG_SIZES:
      cc = "Case12_%d_%d" % (j, i)
      DESCRIPTION = """Send %d compressed messages each of payload size %d, auto-fragment to %s octets. Use default permessage-deflate offer.""" % (s[1], s[0], s[3])
      EXPECTATION = """Receive echo'ed messages (with payload as sent). Timeout case after %d secs.""" % (s[2])
      C = type(cc,
                (object, Case, ),
                {"LEN": s[0],
                 "COUNT": s[1],
                 "WAITSECS": s[2],
                 "AUTOFRAGSIZE": s[3],
                 "CLIENT_OFFERS": [PerMessageDeflateOffer()],
                 "SERVER_ACCEPT": accept_deflate,
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




##
## Cases 13.x.x
##
Case13_X_X = []
Case13_X_X_CaseSubCategories = {}


def accept1(self, offers):
   """
   server accept (requestNoContextTakeover, requestMaxWindowBits): [(False, 0)]
   """
   for offer in offers:
      if isinstance(offer, PerMessageDeflateOffer):
         return PerMessageDeflateOfferAccept(offer)

def accept2(self, offers):
   """
   server accept (requestNoContextTakeover, requestMaxWindowBits): [(True, 0)]
   """
   for offer in offers:
      if isinstance(offer, PerMessageDeflateOffer):
         if offer.acceptNoContextTakeover:
            return PerMessageDeflateOfferAccept(offer, requestNoContextTakeover = True)

def accept3(self, offers):
   """
   server accept (requestNoContextTakeover, requestMaxWindowBits): [(False, 8)]
   """
   for offer in offers:
      if isinstance(offer, PerMessageDeflateOffer):
         if offer.acceptMaxWindowBits:
            return PerMessageDeflateOfferAccept(offer, requestMaxWindowBits = 8)

def accept4(self, offers):
   """
   server accept (requestNoContextTakeover, requestMaxWindowBits): [(False, 15)]
   """
   for offer in offers:
      if isinstance(offer, PerMessageDeflateOffer):
         if offer.acceptMaxWindowBits:
            return PerMessageDeflateOfferAccept(offer, requestMaxWindowBits = 15)

def accept5(self, offers):
   """
   server accept (requestNoContextTakeover, requestMaxWindowBits): [(True, 8)]
   """
   for offer in offers:
      if isinstance(offer, PerMessageDeflateOffer):
         if offer.acceptNoContextTakeover and offer.acceptMaxWindowBits:
            return PerMessageDeflateOfferAccept(offer, requestMaxWindowBits = 8, requestNoContextTakeover = True)

def accept6(self, offers):
   """
   server accept (requestNoContextTakeover, requestMaxWindowBits): [(True, 15)]
   """
   for offer in offers:
      if isinstance(offer, PerMessageDeflateOffer):
         if offer.acceptNoContextTakeover and offer.acceptMaxWindowBits:
            return PerMessageDeflateOfferAccept(offer, requestMaxWindowBits = 15, requestNoContextTakeover = True)

def accept7(self, offers):
   """
   server accept (requestNoContextTakeover, requestMaxWindowBits): [(True, 8), (True, 0), (False, 0)]
   """
   a = accept5(self, offers)
   if a:
      return a
   else:
      a = accept2(self, offers)
      if a:
         return a
      else:
         return accept1(self, offers)


DEFLATE_PARAMS = [
   (accept1, [PerMessageDeflateOffer()]),
   (accept2, [PerMessageDeflateOffer(requestNoContextTakeover = True, requestMaxWindowBits = 0)]),
   (accept3, [PerMessageDeflateOffer(requestNoContextTakeover = False, requestMaxWindowBits = 8)]),
   (accept4, [PerMessageDeflateOffer(requestNoContextTakeover = False, requestMaxWindowBits = 15)]),
   (accept5, [PerMessageDeflateOffer(requestNoContextTakeover = True, requestMaxWindowBits = 8)]),
   (accept6, [PerMessageDeflateOffer(requestNoContextTakeover = True, requestMaxWindowBits = 15)]),
   (accept7, [PerMessageDeflateOffer(requestNoContextTakeover = True, requestMaxWindowBits = 8), PerMessageDeflateOffer(requestNoContextTakeover = True), PerMessageDeflateOffer()])
]


TEST_DATA = WS_COMPRESSION_TESTDATA['json_data1']


j = 1
for dp in DEFLATE_PARAMS:

   sa = dp[0]
   co = dp[1]

   isBinary = TEST_DATA["binary"]
   fn = pkg_resources.resource_filename("autobahntestsuite", "testdata/%s" % TEST_DATA['file'])
   fileSize = os.path.getsize(fn)

   co_desc = "client offers (requestNoContextTakeover, requestMaxWindowBits): {0}".format([(x.requestNoContextTakeover, x.requestMaxWindowBits) for x in co])
   sa_desc = sa.__doc__.strip()

   Case13_X_X_CaseSubCategories['13.%d' % j] = TEST_DATA["desc"] + (" (%s, %s bytes)" % ("binary" if isBinary else "utf8", fileSize)) + " - " + co_desc + " / " + sa_desc

   i = 1
   for s in MSG_SIZES:
      cc = "Case13_%d_%d" % (j, i)
      DESCRIPTION = """Send %d compressed messages each of payload size %d, auto-fragment to %s octets. Use permessage-deflate %s""" % (s[1], s[0], s[3], co_desc)
      EXPECTATION = """Receive echo'ed messages (with payload as sent). Timeout case after %d secs.""" % (s[2])
      C = type(cc,
                (object, Case, ),
                {"LEN": s[0],
                 "COUNT": s[1],
                 "WAITSECS": s[2],
                 "AUTOFRAGSIZE": s[3],
                 "CLIENT_OFFERS": co,
                 "SERVER_ACCEPT": sa,
                 "TESTDATA": TEST_DATA,
                 "DESCRIPTION": """%s""" % DESCRIPTION,
                 "EXPECTATION": """%s""" % EXPECTATION,
                 "__init__": __init__,
                 "init": init,
                 "onOpen": onOpen,
                 "onMessage": onMessage,
                 "sendOne": sendOne,
                 })
      Case13_X_X.append(C)
      i += 1
   j += 1
