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

__all__ = ('RITestDb', 'RITestRunner', )

import zope
from zope.interface import Interface, Attribute


class RITestDb(Interface):
   """
   A Test database provides storage and query capabilities for test cases, results and related data.

   This interface is remoted as a set of WAMP endpoints.
   """

   URI = Attribute("The base URI under which methods are exposed for WAMP.")


   def importSpec(spec):
      """
      Import a test specification into the test database.

      Returns a pair `(op, id)`, where `op` specifies the operation that
      actually was carried out:

          - None: unchanged
          - 'U': updated
          - 'I': inserted

      The `id` is the new (or existing) database object ID for the spec.
      """


   def getSpecs(activeOnly = True):
      """
      """


   def getSpec(specId):
      """
      """


   def getSpecByName(name):
      """
      Find a (currently active, if any) test specification by name.
      """


   def getTestRuns(limit = 10):
      """
      Return a list of latest testruns.
      """


   def getTestResult(resultId):
      """
      Get a single test result by ID.

      :param resultId: The ID of the test result to retrieve.
      :type resultId: str
      :returns Deferred -- A single instance of TestResult.
      """


   def getTestRunIndex(runId):
      """
      """


   def getTestRunSummary(runId):
      """
      """



class RITestRunner(Interface):
   """
   """

   def run(specName, saveResults = True):
      """
      """
