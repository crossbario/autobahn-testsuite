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


import sys, collections, os, json

from twisted.python import log
from twisted.internet import reactor, defer
from twisted.internet.defer import Deferred, returnValue, inlineCallbacks

# for versions
import autobahn
import autobahntestsuite
import report

from wampcase import Cases, \
                     CaseCategories, \
                     CaseSubCategories, \
                     CaseBasename

from caseset import CaseSet

WS_URI = "ws://localhost:9000"


def subCategoryName(cat_id, subcat_id):
   try:
      return CaseSubCategories["%d.%d" % (cat_id, subcat_id)]
   except KeyError:
      return "Unspecified"

   
class Category(object):

   def __init__(self, cat_id, name):
      self.cat_id = cat_id
      self.name = name
      self._sub_categories = {}
      self._testees = {}


   @property
   def sub_categories(self):
      return [x[1] for x in sorted(self._sub_categories.iteritems())]


   @property
   def testees(self):
      return sorted(self._testees.iterkeys())

   
   def addTestCase(self, subcat_id, agent, test_case):
      self._testees[test_case.testee] = None
      if subcat_id not in self._sub_categories:
         self._sub_categories[subcat_id] = SubCategory(self.cat_id, subcat_id)
      self._sub_categories[subcat_id].addTestCase(agent, test_case)



class SubCategory(object):


   def __init__(self, cat_id, subcat_id):
      self.cat_id = cat_id
      self.subcat_id = subcat_id
      self.name = subCategoryName(cat_id, subcat_id)
      # A dictionary with server names as keys and test case lists as values
      self._test_cases = collections.defaultdict(list)

   @property
   def test_cases(self):
      return sorted(self._test_cases.iteritems())

   
   def addTestCase(self, agent, test_case):
      self._test_cases[test_case.test_name].append((agent, test_case))



class TestResult(object):

   def __init__(self, filename, testee, test_name, test_result, agent, url,
                description):
      self.filename = filename
      self.testee = testee
      self.test_name = test_name
      self.test_result = test_result
      self.agent = agent
      self.url = url
      self.description = description



class FuzzingWampClient(object):
   """
   A test driver for WAMP test cases.

   The test driver takes a test specification and orchestrates the execution of tests
   against the set of testees (as specified in the test spec).
   """

   def __init__(self, testDb, debug = False):
      self._testDb = testDb
      self._debug = debug


   def run(self, runId, agentsCases):
      finished = Deferred()

      # runningTests = []

      # for server in agentsCases:
      #    for testCls in agent['cases']:
      #       test = testCls(server["url"], server["auth"])
      #       d = test.run()
      #       d.addCallback(self.reportTestResult, test, server)
      #       runningTests.append(d)


      finished.callback(None)
      return finished


   def run2(self, runId, spec):
      self._runId = runId
      self._runFinished = Deferred()
      self.spec = spec

      self.CaseSet = CaseSet(CaseBasename, Cases, CaseCategories, CaseSubCategories)

      self.specCases = self.CaseSet.parseSpecCases(self.spec)
      self.specExcludeAgentCases = self.CaseSet.parseExcludeAgentCases(self.spec)
      print (("Autobahn Fuzzing WAMP Client (Autobahn Version %s / " "Autobahn Testsuite Version %s)") % (autobahntestsuite.version, autobahn.version))
      print "Ok, will run %d test cases against %d servers" % (len(self.specCases), len(spec["servers"]))
      print "Cases = %s" % str(self.specCases)
      print "Servers = %s" % str(["%s@%s" % (x["url"], x["agent"]) for x in spec["servers"]])

      self.currentCaseIndex = -1 # The 0-based number of the current test case
      self.test = None

      # Basic information about test reports, grouped by category and
      # (inside the category) subcategory
      self.categories = {}

      # TODO: Add a JSON report generator
      self.report_generators = [report.HtmlReportGenerator(self.spec["outdir"])]

      # Start performing tests
      self.next()

      return self._runFinished


   def readableTestName(self, test):
      """
      Provide the name of the current test case as presented in the reports.
      """
      name = test.__class__.__name__
      return " ".join([name[:8], name[8:].replace("_", ".")])


   def identifierParts(self, test):
      identifier = test.__class__.__name__[8:]
      sys.stdout.flush()
      return [int(x) for x in identifier.split("_")]

   def next(self, result=None):
      """
      Execute the next available test.
      """
      self.currentCaseIndex += 1
      if self.currentCaseIndex < len(self.specCases):

         # Fetch the next test case from wampcases.Cases. This list is
         # initialized in the wampcases.wampcases1.py and assigned to
         # `Cases` in wampcases' __init__.py.
         print self.specCases
         print self.specCases[self.currentCaseIndex] 
         #testCls = self.specCases[self.currentCaseIndex] 
         testCls = Cases[self.currentCaseIndex] 

         # Run test case against all agents and gather the resulting
         # deferreds in a list.
         runningTests = []
         print "Running test %d/%d (%s)" % (self.currentCaseIndex + 1,
                                            len(self.specCases),
                                            testCls.__name__)
         for server in self.spec["servers"]:
            test = testCls(server["url"], server["auth"], debugWs = self.spec.get('debugWs', False), debugWamp = self.spec.get('debugWamp', False))
            d = test.run()
            d.addCallback(self.reportTestResult, test, server)
            d.addErrback(self.printError)
            runningTests.append(d)

         # Create a DeferredList from runningTests and attach a callback
         # to start the next test case when all agents have finished.
         d = defer.DeferredList(runningTests)
         d.addCallback(self.next)
      else:
         self.createIndexFile()
         self._runFinished.callback(None)
         self._runFinished = None


   def reportTestResult(self, res, test, server):
      print "reportTestResult"
      print res
      print test
      print server
      print self._testDb
      if self._testDb:
         self._testDb.saveResult(self._runId, res)

   def reportTestResult2(self, res, test, agent, url):
      """
      Print a short informational message about test success or failure,
      create a file with detailed test result information.
      """
      # Remember high-level information about the test case that will be
      # needed to create the index page.
      cat_id, subcat_id = self.identifierParts(test)[:2]

      if cat_id not in self.categories:
         # Create new category for the previously unseen `cat_id`.
         category = Category(cat_id, CaseCategories[str(cat_id)])
         self.categories[cat_id] = category
      status_representation =  "Pass" if res[0] else "Fail"
      report_filename = self.createFilename(agent, test)

      # Add the test report to the appropriate category / subcategory.
      self.categories[cat_id].addTestCase(subcat_id, agent,
                                          TestResult(report_filename,
                                                     agent,
                                                     self.readableTestName(test),
                                                     status_representation,
                                                     agent,
                                                     url,
                                                     test.DESCRIPTION))
      for generator in self.report_generators:
         generator.createReport(res, report_filename,
                                self.readableTestName(test), agent,
                                test.DESCRIPTION)


   # TODO: Move filename creation to the respective report generators!
   #+ They are format-specific.
   def createFilename(self, agent, test):
      """
      Create the filename for the current test.
      """
      # TODO: use server agent name from spec to allow for several servers
      return "%s_%s.html" % (agent, test.__class__.__name__.lower())


   def createIndexFile(self):
      """
      Print a terminating message and stop the script.
      """
      for generator in self.report_generators:
         generator.createIndex([x[1] for x in
                                sorted(self.categories.iteritems())])
      print "Done"


   def printError(self, err):
      """
      Print an error message thrown by a test case.
      """
      print err
      print "Error for test case %s reported" % self.readableTestName(test)
      
      

if __name__ == '__main__':
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
   if debug:
      log.startLogging(sys.stdout)

   spec = "fuzzingwampclient.json"
   if not os.path.exists(spec):
      from spectemplate import SPEC_FUZZINGWAMPCLIENT
      with open(spec, "w") as f:
         f.write(SPEC_FUZZINGWAMPCLIENT)
   with open(spec) as f:
      spec = json.loads(f.read())

   c = FuzzingWampClient(spec, debug)

   reactor.run()
