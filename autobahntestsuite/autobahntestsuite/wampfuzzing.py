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

from zope.interface import implementer
from zope.interface.verify import verifyObject, verifyClass

from twisted.internet.defer import returnValue, \
                                   inlineCallbacks

import autobahn
import autobahntestsuite

from autobahn.wamp import exportRpc

from interfaces import ITestRunner, ITestDb
from rinterfaces import RITestDb, RITestRunner
from testrun import TestRun, Testee



@implementer(ITestRunner)
@implementer(RITestRunner)
class FuzzingWampClient(object):
   """
   A test driver for WAMP test cases.

   The test driver takes a test specification and orchestrates the execution of tests
   against the set of testees (as specified in the test spec).
   """

   MODENAME = 'fuzzingwampclient'


   def __init__(self, testDb, debug = False):

      assert(verifyObject(ITestDb, testDb))
      assert(verifyObject(RITestDb, testDb))

      self._testDb = testDb
      self._debug = debug
      self.dispatch = None


   @exportRpc
   def run(self, specName, saveResults = True):
      return self.runAndObserve(specName, saveResults = saveResults)


   @inlineCallbacks
   def runAndObserve(self, specName, observers_ = [], saveResults = True):

      specId, spec = yield self._testDb.getSpecByName(specName)
      casesByTestee = yield self._testDb.generateCasesByTestee(specId)
      _observers = observers_[:]

      ## publish WAMP event on test case finished
      ##
      def notify(runId, testRun, testCase, result, remaining):
         if testCase:
            evt = {
               'testee': testRun.testee.name,
               'runId': runId,
               'index': testCase.index,
               'passed': result.passed,
               'remaining': remaining
            }
            topic = "http://api.testsuite.wamp.ws/testrun#onResult"
         else:
            evt = {
               'testee': testRun.testee.name,
               'runId': runId
            }
            topic = "http://api.testsuite.wamp.ws/testrun#onComplete"

         self.dispatch(topic, evt)
         #if result and not result.passed:
         #   print topic, evt

      if self.dispatch:
         _observers.append(notify)

      ## save test results to test database
      ##
      def save(runId, testRun, testCase, result, remaining):
         if testCase:
            self._testDb.saveResult(runId, testRun, testCase, result, saveResults)

      if saveResults:
         _observers.append(save)

      testRuns = []
      for obj in spec['testees']:
         testee = Testee(**obj)
         cases = casesByTestee.get(testee.name, [])
         if testee.options.has_key('randomize') and testee.options['randomize'] is not None:
            randomize = testee.options['randomize']
         elif spec.has_key('options') and spec['options'].has_key('randomize') and spec['options']['randomize'] is not None:
            randomize = spec['options']['randomize']
         else:
            randomize = False
         testRun = TestRun(testee, cases, randomize = randomize)
         testRuns.append(testRun)

      runId = yield self._testDb.newRun(specId)

      print
      print "Autobahn Fuzzing WAMP Client"
      print
      print "Autobahn Version          : %s" % autobahn.version
      print "AutobahnTestsuite Version : %s" % autobahntestsuite.version
      #print "WAMP Test Cases           : %d" % len(self._caseSet.Cases)
      print "WAMP Testees              : %d" % len(spec["testees"])
      print
      for testRun in testRuns:
         print "%s @ %s : %d test cases prepared" % (testRun.testee.name, testRun.testee.url, testRun.remaining())
      print
      print

      def progress(runId, testRun, testCase, result, remaining):
         for obsv in _observers:
            try:
               obsv(runId, testRun, testCase, result, remaining)
            except Exception, e:
               print e

      if spec.get('parallel', False):
         fails, resultIds = yield self._runParallel(runId, spec, testRuns, progress)
      else:
         fails, resultIds = yield self._runSequential(runId, spec, testRuns, progress)

      yield self._testDb.closeRun(runId)

      returnValue((runId, resultIds))


   @inlineCallbacks
   def _runSequential(self, runId, spec, testRuns, progress):
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
               testCase = TestCase(testRun.testee, spec)
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


   def _runParallel(self, runId, spec, testRuns, progress):
      """
      Execute all test runs in parallel - that is run
      each testee's set of test cases sequentially
      against that testee, but do so for all testees
      in parallel.
      """
      raise Exception("implement me")
