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

__all__ = ('ITestDb',)

import zope
from zope.interface import Interface, Attribute


class ITestee(Interface):

   name = Attribute("""Testee name""")



class ITestDb(Interface):

   def newRun(mode, spec):
      """
      Create a new testsuite run.

      :param mode: The testsuite mode.
      :type mode: str
      :param spec: The test specification.
      :type spec: object (a JSON serializable test spec)
      :returns Deferred -- The testrun ID.
      """

   def saveResult(runId, result):
      """
      Saves a test result in the database.

      :param runId: The test run ID.
      :type runId: str
      :param result: The test result. An instance of TestResult.
      :type result: object
      :returns Deferred -- The test result ID.
      """

   def closeRun(runId):
      """
      Closes a testsuite run. After a testsuite run is closed,
      the test result data cannot be changed or new data added.

      :param testRunId: ID of test run as previsouly returned by newRun().
      :type testRunId: str
      """

   def getResult(resultId):
      """
      Get result by ID.

      :param resultId: The ID of the test result to retrieve.
      :type resultId: str
      :returns Deferred -- The test result. An instance of TestResult.
      """

   def getResults(runId):
      """
      """

ITestDb.MODE_FUZZING_WAMP_CLIENT = "fuzzingwampclient"



class IReportGenerator(zope.interface.Interface):
   """
   """

   outputDirectory = zope.interface.Attribute("""Default output directory base path.""")

   fileExtension = zope.interface.Attribute("""Default file extension for report files.""")


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
