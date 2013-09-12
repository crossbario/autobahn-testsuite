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

from twisted.internet.defer import returnValue, inlineCallbacks

import autobahn
import autobahntestsuite

from zope.interface import implementer

from interfaces import ITestRunner
from testrun import TestRun, Testee



@implementer(ITestRunner)
class FuzzingWampClient(object):
   """
   A test driver for WAMP test cases.

   The test driver takes a test specification and orchestrates the execution of tests
   against the set of testees (as specified in the test spec).
   """

   MODENAME = 'fuzzingwampclient'


   def __init__(self, testDb, caseSet, debug = False):
      self._testDb = testDb
      self._caseSet = caseSet
      self._debug = debug


   @inlineCallbacks
   def run(self, spec, observers = []):

      casesByTestee = self._caseSet.generateCasesByTestee(spec)

      testRuns = []
      for obj in spec['testees']:
         testee = Testee(**obj)
         cases = casesByTestee.get(testee.name, [])
         testRun = TestRun(testee, cases, randomize = spec.get('randomize', False))
         testRuns.append(testRun)

      runId = yield self._testDb.newRun(self.MODENAME, spec)

      print
      print "Autobahn Fuzzing WAMP Client"
      print
      print "Autobahn Version          : %s" % autobahn.version
      print "AutobahnTestsuite Version : %s" % autobahntestsuite.version
      print "WAMP Test Cases           : %d" % len(self._caseSet.Cases)
      print "WAMP Testees              : %d" % len(spec["testees"])
      print
      for testRun in testRuns:
         print "%s @ %s : %d test cases prepared" % (testRun.testee.name, testRun.testee.url, testRun.remaining())
      print

      def progress(runId, testRun, test, result, remaining):
         if test:
            print "%s%s (%d tests remaining)" % ("PASSED   : " if result.passed else "FAILED  : ", test.__class__.__name__, remaining)
            return self._testDb.saveResult(runId, result)
         else:
            print "FINISHED : Test run for testee '%s' ended." % testRun.testee.name

      if spec.get('parallel', False):
         fails, resultIds = yield self._runParallel(runId, testRuns, progress)
      else:
         fails, resultIds = yield self._runSequential(runId, testRuns, progress)

      returnValue((runId, resultIds))


   @inlineCallbacks
   def _runSequential(self, runId, testRuns, progress):
      """
      Execute all test runs sequentially - that is for each
      testee (one after another), run the testee's set of
      test cases sequentially.
      """
      ## we cumulate number of test fails and progress() return values
      ##
      fails = 0
      progressResults = []

      for testRun in testRuns:
         while True:
            ## get next test case _class_ for test run
            ##
            TestCase = testRun.next()

            if TestCase:
               ## run test case, let fire progress() callback and cumulate results
               ##
               testCase = TestCase(testRun.testee)
               #print testCase.description
               #print testCase.expectation
               result = yield testCase.run()
               if not result.passed:
                  fails += 1
               pres = yield progress(runId, testRun, testCase, result, testRun.remaining())
               progressResults.append(pres)
            else:
               ## signal end of test run by firing progress() one last time ..
               ##
               yield progress(runId, testRun, None, None, 0)
               break

      returnValue((fails, progressResults))


   def _runParallel(self, runId, testRuns, progress):
      """
      Execute all test runs in parallel - that is run
      each testee's set of test cases sequentially
      against that testee, but do so for all testees
      in parallel.
      """
      raise Exception("implement me")
