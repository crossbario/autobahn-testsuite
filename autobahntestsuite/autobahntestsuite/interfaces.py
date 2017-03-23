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

__all__ = ('ITestDb', 'IReportGenerator', )

import zope
from zope.interface import Interface, Attribute

class ICaseSet(Interface):
   """
   """
   pass


class ITestDb(Interface):
   """
   A Test database provides storage and query capabilities
   for test cases, results and related data.
   """

   def newRun(specId):
      """
      Create a new testsuite run.

      :param mode: The testsuite mode.
      :type mode: str
      :param spec: The test specification.
      :type spec: object (a JSON serializable test spec)
      :returns Deferred -- The test run ID.
      """


   def closeRun(runId):
      """
      Closes a testsuite run. After a testsuite run is closed,
      the test result data cannot be changed or new data added.

      :param testRunId: ID of test run as previously returned by newRun().
      :type testRunId: str
      """


   def generateCasesByTestee(specId):
      """
      """


   def saveResult(runId, testRun, test, result):
      """
      Saves a test result in the database.

      :param runId: The test run ID.
      :type runId: str
      :param result: The test result. An instance of TestResult.
      :type result: object
      :returns Deferred -- The test result ID.
      """

   # def registerResultFile(resultId, type, sha1, path):
   #    """
   #    When a report file generator has produced it's output
   #    and created (or recreated/modified) a file, it should
   #    register the file location via this function.

   #    :param resultId: The ID of the test result this file was generated for.
   #    :type resultId: str
   #    :param type: The type of file produced (FIXME: ['html', 'json'] ??)
   #    :type type: FIXME
   #    :param sha1: The SHA-1 computed over the generated octet stream.
   #    :type sha1 str
   #    :param path: The filesystem path to the generated file.
   #    :type path: str
   #    """

ITestDb.TESTMODES = set(['fuzzingwampclient', 'fuzzingclient'])
"""
The list of implemented test modes.
"""


class ITestRunner(Interface):
   """
   """

   def runAndObserve(specName, observers = [], saveResults = True):
      """
      :param observers: An iterable of ITestRunObserver instances.
      :type observers: iterable
      """


class IReportGenerator(Interface):
   """
   A Report generator is able to produce report files (in a
   format the generator supports) from test results stored
   in a Test database.
   """

   outputDirectory = Attribute("""Default output directory base path. (e.g. 'reports/wamp/servers')""")

   fileExtension = Attribute("""Default file extension for report files (e.g. '.html').""")

   mimeType = Attribute("""Default MIME type for generated reports (e.g. 'text/html').""")


   def writeReportIndexFile(runId, file = None):
      """
      Generate a test report index and write to file like object or
      to an automatically chosen report file (under the default
      output directory

      :param runId: The test run ID for which to generate the index for.
      :type runId: object
      :param file: A file like object or None (automatic)
      :type file: object
      :returns -- None if file was provided, or the pathname
                  of the created report file (automatic).
      """

   def writeReportFile(resultId, file = None):
      """
      Generate a test report and write to file like object or
      to an automatically chosen report file (under the default
      output directory

      :param resultId: The test result ID for which to generate the report for.
      :type resultId: object
      :param file: A file like object or None (automatic)
      :type file: object
      :returns -- None if file was provided, or the pathname
                  of the created report file (automatic).
      """




class ITestRun(Interface):
   """
   """

   def next():
      """
      Returns the next test case for this run or None when
      the test run is finished.

      :returns ICase -- The next test case or None.
      """

   def remaining():
      """
      Number of remaining test cases in this test run.

      :returns int -- Number of remaining test cases.
      """

   def __len__():
      """
      The length of this test run (note that fetching
      test cases does not change the length).
      """


class ITestRunObserver(Interface):
   """
   """

   def progress(runId, testRun, testCase, result, remaining):
      """
      """


class ITestCase(Interface):
   """
   Tests are instantiated as objects providing this interface.
   They have their run() method called exactly once before
   being disposed.
   """
   index = Attribute("""Test case index - a tuple of ints.""")
   description = Attribute("""Test case description.""")
   expectation = Attribute("""Test case expectation.""")
   params = Attribute("""Test case parameters.""")

   def run():
      """
      Run the test case. Returns a deferred that provides an instance
      of TestResult when successful.
      """
