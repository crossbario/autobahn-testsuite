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

__all__ = ['Case12_7_X', 'Case12_8_X']

import copy, os

from case import Case
from autobahn.websocket import PerMessageDeflateOffer, PerMessageDeflateAccept

## list of (payload length, message count, case timeout)
tests = [(0, 1000, 60),
         (16, 1000, 60),
         (64, 1000, 60),
         (256, 1000, 120),
         (1024, 1000, 240),
         (4096, 1000, 480)]

Case12_7_X = []
Case12_8_X = []


def __init__(self, protocol):
   Case.__init__(self, protocol)

def init(self):
   self.reportTime = True
   self.reportCompressionRatio = True

   self.p.perMessageDeflate = True
   if self.p.isServer:
      self.p.perMessageDeflateAccept = lambda protocol, connectionRequest, perMessageDeflateOffer: PerMessageDeflateAccept()
#      self.p.perMessageDeflateAccept = lambda protocol, connectionRequest, perMessageDeflateOffer: PerMessageDeflateAccept(True, 8)
   else:
      self.p.perMessageDeflateOffers = [PerMessageDeflateOffer()]

   #self.payload = "Hello, world!" * 4096
   #self.payload = self.payload[:self.LEN]
   #print self.__class__.__name__
   if self.BINARY:
      self.payload = self.p.factory.testData['ooms']['data'][:self.LEN]
      #self.payload = os.urandom(self.LEN)
   else:
      self.payload = self.p.factory.testData['gutenberg_faust']['data'][:self.LEN]

def onOpen(self):
   self.p.enableWirelog(False)
   self.expectedClose = {"closedByMe": True,
                         "closeCode": [self.p.CLOSE_STATUS_CODE_NORMAL],
                         "requireClean": True}

   if self.p._deflateParams is None:
      self.behavior = Case.UNIMPLEMENTED
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL)
   else:
      self.behavior = Case.FAILED
      self.result = "Case did not finish within %d seconds." % self.WAITSECS
      self.p.closeAfter(self.WAITSECS)
      self.count = 0
      self.sendOne()

def sendOne(self):
   self.p.sendMessage(self.payload, self.BINARY)
   self.count += 1

def onMessage(self, msg, binary):
   if binary != self.BINARY or len(msg) != self.LEN:
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

for b in [False, True]:
   i = 1
   for s in tests:
      if b:
         mt = "binary"
         cc = "Case12_8_%d"
      else:
         mt = "text"
         cc = "Case12_7_%d"
      DESCRIPTION = """Send %d %s messages of payload size %d to measure implementation/network RTT (round trip time) / latency.""" % (s[1], mt, s[0])
      EXPECTATION = """Receive echo'ed %s messages (with payload as sent). Timeout case after %d secs.""" % (mt, s[2])
      C = type(cc % i,
                (object, Case, ),
                {"LEN": s[0],
                 "COUNT": s[1],
                 "WAITSECS": s[2],
                 "BINARY": b,
                 "DESCRIPTION": """%s""" % DESCRIPTION,
                 "EXPECTATION": """%s""" % EXPECTATION,
                 "__init__": __init__,
                 "init": init,
                 "onOpen": onOpen,
                 "onMessage": onMessage,
                 "sendOne": sendOne,
                 })
      if b:
         Case12_7_X.append(C)
      else:
         Case12_8_X.append(C)
      i += 1
