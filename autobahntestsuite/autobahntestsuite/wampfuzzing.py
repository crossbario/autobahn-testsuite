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


import sys, os, collections
import jinja2
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

# Specification of report directory
REPORT_DIR = "reports"
REPORT_DIR_PERMISSIONS = 0770

CSS_WAMPSUMMARY = """
.wamplog {
   font-family: Consolas, monospace;
}
"""

WS_URI = "ws://localhost:9000"

ReportSpec = collections.namedtuple("ReportSpec",
                                    ["filename", "test_name", "test_result"])

class WampFuzzingClient(object):
   """A test driver for WAMP test cases.
   """


   def __init__(self, url, debugWs = False, debugWamp = False):
      """Initialize test driver.
      """
      self.url = url
      self.debugWs = debugWs
      self.debugWamp = debugWamp
      self.currentCaseIndex = -1
      self.test = None
      self.reports = []
      env = jinja2.Environment(
         loader=jinja2.PackageLoader("autobahntestsuite", "templates"),
         line_statement_prefix="#")
      self.wamp_details_tpl = env.get_template("wamp_details.html")
      self.wamp_index_tpl = env.get_template("wamp_overview.html")
      
      # Check if the 'reports' directory exists; try to create it otherwise.
      if not os.path.isdir(REPORT_DIR):
         self.createReportDir()


   def createReportDir(self):
      """Create the directory for storing the reports. If this is not possible,
         terminate the script.
      """
      try:
         os.mkdir(REPORT_DIR, REPORT_DIR_PERMISSIONS)
      except OSError, exc:
         print "Could not create directory: %s" % exc
         sys.exit(1)


   @property
   def currentTestName(self):
      """Provide the name of the current test case.
      """
      return self.test.__class__.__name__

   
   @property
   def readableTestName(self):
      return " ".join([self.currentTestName[:8],
                         self.currentTestName[8:].replace("_", ".")])

   
   def next(self):
      """Execute the next available test.
      """
      self.currentCaseIndex += 1
      if self.currentCaseIndex < len(Cases):
         # Fetch the next test case from wampcases.Cases. This list is
         # initialized in the wampcases.wampcases1.py and assigned to
         # `Cases` in wampcases' __init__.py.
         self.test = Cases[self.currentCaseIndex](self.url, self.debugWs,
                                                  self.debugWamp)
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
      """Print a short informational message about test success or failure,
         create a file with detailed test result information.
      """
      print "PASS" if res[0] else "FAIL"
      self.createHtmlReport(res)
      self.next()


   def createFilename(self):
      """Create the filename for the current test.
      """
      return "%s.html" % self.currentTestName


   ### TODO: Move the creation of reports to a separate class.
   def createHtmlReport(self, res):
      """Create an HTML file in the `REPORT_DIR` with details about the
         test case.
      """
      report_filename = self.createFilename()
      self.reports.append(ReportSpec(report_filename, self.readableTestName,
                                     "PASS" if res[0] else "FAILED"))
      report_path = os.path.join(REPORT_DIR, report_filename)
      try:
         f = open(report_path, "w")
      except IOError:
         print "Could not create file", report_path
         reactor.stop()
      f.write(self.formatResultAsHtml(res))
      f.close()


   def formatResultAsHtml(self, res):
      """Create an HTML document with a table containing information about
         the test outcome.
      """
      html = self.wamp_details_tpl.render(style=CSS_WAMPSUMMARY,
                                          record_list=res[3],
                                          test_name = self.readableTestName,
                                          expected=res[1],
                                          observed=res[2],
                                          outcome="Pass" if res[0] else "Fail")
      return html


   def finished(self):
      """Print a terminating message and stop the script.
      """
      try:
         with open(os.path.join(REPORT_DIR, "index.html"), "w") as f:
            html = self.wamp_index_tpl.render(style=CSS_WAMPSUMMARY,
                                              reports=self.reports)
            f.write(html)
      except Exception, ex:
         print "Exception %s occurred" % ex
      print ("Done. Point your browser to %s/index.html to see the results." %
             REPORT_DIR)
      reactor.stop()


   def printError(self, err):
      """Print an error message thrown by a test case.
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
