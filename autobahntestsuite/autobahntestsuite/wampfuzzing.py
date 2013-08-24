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

   
   def addTestCase(self, subcat_id, test_case):
      self._testees[test_case.testee] = None
      if subcat_id not in self._sub_categories:
         self._sub_categories[subcat_id] = SubCategory(self.cat_id, subcat_id)
      self._sub_categories[subcat_id].addTestCase( test_case)



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

   
   def addTestCase(self, test_case):
      self._test_cases[test_case.test_name].append(test_case)



class ReportSpec(object):

   def __init__(self, filename, testee, test_name, test_result):
      self.filename = filename
      self.testee = testee
      self.test_name = test_name
      self.test_result = test_result



class FuzzingWampClient(object):
   """
   A test driver for WAMP test cases.
   """


   def __init__(self, spec, debug = False):
      self.spec = spec
      self.debug = debug
      self.report_dir = self.spec["outdir"]
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

      try:
         for server in spec["servers"]:
            if server["agent"] == "AutobahnPython":
               self.url = server["url"]
      except KeyError, ex:
         print "Problem with specification file: Key %s not found." % ex
         reactor.stop()

      # TODO Distinguish between debug modes (using the spec file?)
      self.debugWs = debug
      self.debugWamp = debug
      #
      self.currentCaseIndex = -1 # The 0-based number of the current test case
      self.test = None

      # Basic information about test reports, grouped by category and
      # (inside the category) subcategory
      self.categories = {}

      # TODO: Add a JSON report generator
      self.report_generators = [report.HtmlReportGenerator(self.report_dir)]

      # Start performing tests
      self.next()


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

   @property
   def identifierParts(self):
      identifier = self.currentTestName[8:]
      return [int(x) for x in identifier.split("_")]

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
         # Do not write a line break - this is done after "Pass" or "Fail"
         # is printed in `reportTestResult`.
         sys.stdout.write("Running test %d/%d (%s)... " % (
               self.currentCaseIndex + 1,
               len(Cases),
               self.currentTestName))
         sys.stdout.flush()
         # TODO: Iterate over all servers specified in self.spec
         d = self.test.run()
         d.addCallbacks(self.reportTestResult, self.printError)
      else:
         # No more test cases ==> create index.html
         self.createIndexFile()
         print ("Done. Point your browser to %s/index.html to see the "
                "results.") % self.report_dir
         reactor.stop()


   def reportTestResult(self, res):
      """
      Print a short informational message about test success or failure,
      create a file with detailed test result information.
      """
      status_representation =  "Pass" if res[0] else "Fail"
      print status_representation
      report_filename = self.createFilename()

      # Remember high-level information about the test case that will be
      # needed to create the index page.
      cat_id, subcat_id = self.identifierParts[:2]
      if cat_id not in self.categories:
         # Create new category for the previously unseen `cat_id`.
         category = Category(cat_id, CaseCategories[str(cat_id)])
         self.categories[cat_id] = category

      # Add the test report to the appropriate category / subcategory.
      self.categories[cat_id].addTestCase(subcat_id,
                                          ReportSpec(report_filename,
                                                     "autobahn_python",
                                                     self.readableTestName,
                                                     status_representation))

      for generator in self.report_generators:
         generator.createReport(res, report_filename, self.readableTestName)
      self.next()


   # TODO: Move filename creation to the respective report generators!
   #+ They are format-specific.
   def createFilename(self):
      """
      Create the filename for the current test.
      """
      # TODO: use server agent name from spec to allow for several servers
      return "autobahnpython_%s.html" % self.currentTestName.lower()


   def createIndexFile(self):
      """
      Print a terminating message and stop the script.
      """
      for generator in self.report_generators:
         generator.createIndex([x[1] for x in
                                sorted(self.categories.iteritems())])


   def printError(self, err):
      """
      Print an error message thrown by a test case.
      """
      print err

      

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

   c = FuzzingWampClient(spec)

   reactor.run()
