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

import sys
from pprint import pprint

from twisted.python import log
from twisted.internet import reactor


from wampcase import WampCases


class WampFuzzingClient:

   def __init__(self, url, debugWs = False, debugWamp = False):
      self.url = url
      self.debugWs = debugWs
      self.debugWamp = debugWamp
      self.currentCaseIndex = -1
      self.test = None


   def finished(self):
      print "COMPLETED"
      reactor.stop()


   def logResult(self, res):
      print self.test.__class__, "OK" if res[0] else "FAIL"
      self.next()


   def error(self, err):
      print err


   def next(self):
      self.currentCaseIndex += 1
      if self.currentCaseIndex < len(WampCases):
         self.test = WampCases[self.currentCaseIndex](self.url, self.debugWs, self.debugWamp)
         d = self.test.run()
         d.addCallback(self.logResult)
      else:
         self.finished()



if __name__ == '__main__':

   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
   if debug:
      log.startLogging(sys.stdout)

   c = WampFuzzingClient("ws://localhost:9000", debugWs = debug, debugWamp = debug)
   c.next()

   reactor.run()
