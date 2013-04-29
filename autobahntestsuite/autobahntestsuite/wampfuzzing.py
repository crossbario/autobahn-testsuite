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

__all__ = ("FuzzingWampClient",)


import sys, os
from pprint import pprint

from twisted.python import log
from twisted.internet import reactor

# for versions
import autobahn
import autobahntestsuite

from wampcase import Cases, \
                     CaseCategories, \
                     CaseSubCategories, \
                     CaseBasename

from caseset import CaseSet


CSS_WAMPSUMMARY = """
.wamplog {
   font-family: Consolas, monospace;
}
"""

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
      print self.test.__class__.__name__, "OK" if res[0] else "FAIL"

      fn = os.path.join('reports', self.test.__class__.__name__ + ".html")
      f = open(fn, 'w')
      f.write(self.formatResultAsHtml(res))
      f.close()

      #pprint(res[3])
      #print self.formatResultAsHtml(res)
      #if not res[0]:
      #   pprint(res[1])
      #   pprint(res[2])
      self.next()


   def error(self, err):
      print err


   def next(self):
      self.currentCaseIndex += 1
      if self.currentCaseIndex < len(Cases):
         self.test = Cases[self.currentCaseIndex](self.url, self.debugWs, self.debugWamp)
         d = self.test.run()
         d.addCallbacks(self.logResult, self.error)
      else:
         self.finished()


   def formatResultAsHtml(self, res):
      hlog = "".join(["<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>" % l for l in res[3]])
      s = """<DOCTYPE html>
<html>
   <head>
      <style>%s</style>
   </head>
   <body>
      <table class="wamplog">
         %s
      </table>
   </body>
</html>      
      """ % (CSS_WAMPSUMMARY, hlog)
      return s



class FuzzingWampClient:
   def __init__(self, spec, debug = False):
      self.spec = spec
      self.debug = debug

      self.CaseSet = CaseSet(CaseBasename, Cases, CaseCategories, CaseSubCategories)

      self.specCases = self.CaseSet.parseSpecCases(self.spec)
      self.specExcludeAgentCases = self.CaseSet.parseExcludeAgentCases(self.spec)

      print "Autobahn Fuzzing WAMP Client (Autobahn Version %s / Autobahn Testsuite Version %s)" % (autobahntestsuite.version, autobahn.version)
      print "Ok, will run %d test cases against %d servers" % (len(self.specCases), len(spec["servers"]))
      print "Cases = %s" % str(self.specCases)
      print "Servers = %s" % str([x["url"] + "@" + x["agent"] for x in spec["servers"]])



if __name__ == '__main__':

   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
   if debug:
      log.startLogging(sys.stdout)

   c = WampFuzzingClient("ws://localhost:9000", debugWs = debug, debugWamp = debug)
   c.next()

   reactor.run()
