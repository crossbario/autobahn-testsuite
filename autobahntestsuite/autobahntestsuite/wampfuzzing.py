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


import sys, collections
import jinja2

from twisted.python import log
from twisted.internet import reactor

# for versions
import autobahn
import autobahntestsuite
import report

from wampcase import Cases, \
                     CaseCategories, \
                     CaseSubCategories, \
                     CaseBasename

from caseset import CaseSet

# Specification of report directory
REPORT_DIR = "reports"

WS_URI = "ws://localhost:9000"

ReportSpec = collections.namedtuple("ReportSpec",
                                    ["filename", "test_name", "test_result"])

class WampFuzzingClient(object):
   """
   A test driver for WAMP test cases.
   """


   def __init__(self, url, debugWs = False, debugWamp = False):
      """
      Initialize test driver.
      """
      self.url = url
      self.debugWs = debugWs
      self.debugWamp = debugWamp
      self.currentCaseIndex = -1 # The 0-based number of the current test case
      self.test = None

      self.reports = [] # Basic information about test reports

      # TODO: Add a JSON report generator
      self.report_generators = [report.HtmlReportGenerator(REPORT_DIR)]


   @property
   def currentTestName(self):
      """
      Provide the name of the current test case.
      """
      return self.test.__class__.__name__


   @property
   def readableTestName(self):
      """
      Provide the name of the current test case as presented in the reports.
      """
      return " ".join([self.currentTestName[:8],
                         self.currentTestName[8:].replace("_", ".")])


   def next(self):
      """
      Execute the next available test.
      """
      self.currentCaseIndex += 1
      if self.currentCaseIndex < len(Cases):
         # Fetch the next test case from wampcases.Cases. This list is
         # initialized in the wampcases.wampcases1.py and assigned to
         # `Cases` in wampcases' __init__.py.
         self.test = Cases[self.currentCaseIndex](self.url, self.debugWs,
                                                  self.debugWamp)
         # Write information about the current test to stdout and make sure
         # that the information is presented on the screen instantly.
         # Do not write a line break - this is done after "PASS" or "FAIL"
         # is printed in `logResult`.
         sys.stdout.write("Running test %d/%d (%s)... " % (
               self.currentCaseIndex + 1,
               len(Cases),
               self.currentTestName))
         sys.stdout.flush()
         d = self.test.run()
         d.addCallbacks(self.logResult, self.printError)
      else:
         # No more test cases ==> stop the reactor...
         self.finished()


   def logResult(self, res):
      """
      Print a short informational message about test success or failure,
      create a file with detailed test result information.
      """
      print "PASS" if res[0] else "FAIL"
      report_filename = self.createFilename()
      # Remember high-level information about the test case that will be
      # needed to create the index page.
      self.reports.append(ReportSpec(report_filename, self.readableTestName,
                                     "PASS" if res[0] else "FAILED"))
      for generator in self.report_generators:
         generator.createReport(res, report_filename, self.readableTestName)
      self.next()


   # TODO: Move filename creation to the respective report generators!
   #+ They are format-specific.   
   def createFilename(self):
      """
      Create the filename for the current test.
      """
      return "%s.html" % self.currentTestName


   def finished(self):
      """
      Print a terminating message and stop the script.
      """
      for generator in self.report_generators:
         generator.createIndex(self.reports)
      print ("Done. Point your browser to %s/index.html to see the results." %
             REPORT_DIR)
      reactor.stop()


   def printError(self, err):
      """
      Print an error message thrown by a test case.
      """
      print err



class FuzzingWampClient(object):


   def __init__(self, spec, debug = False):
      self.spec = spec
      self.debug = debug

      self.CaseSet = CaseSet(CaseBasename, Cases, CaseCategories,
                             CaseSubCategories)

      self.specCases = self.CaseSet.parseSpecCases(self.spec)
      self.specExcludeAgentCases = self.CaseSet.parseExcludeAgentCases(
         self.spec)

      print (("Autobahn Fuzzing WAMP Client (Autobahn Version %s / "
              "Autobahn Testsuite Version %s)") % (autobahntestsuite.version,
                                                   autobahn.version))
      print "Ok, will run %d test cases against %d servers" % (
            len(self.specCases), len(spec["servers"]))
      print "Cases = %s" % str(self.specCases)
      print "Servers = %s" % str(["%s@%s" % (x["url"], x["agent"])
                                  for x in spec["servers"]])



if __name__ == '__main__':
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
   if debug:
      log.startLogging(sys.stdout)

   c = WampFuzzingClient(WS_URI, debugWs = debug, debugWamp = debug)
   c.next()

   reactor.run()
