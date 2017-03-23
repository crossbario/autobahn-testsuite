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

__all__ = ("TestRun", "Testee", "TestResult",)


import random
from collections import deque

from zope.interface import implementer
from interfaces import ITestRun

from util import AttributeBag


class Testee(AttributeBag):

   ATTRIBUTES = ['id',
                 'name',
                 'url',
                 'auth',
                 'options',
                 'debug']



class TestResult(AttributeBag):

   ATTRIBUTES = ['id',
                 'runId',
                 'passed',
                 'description',
                 'expectation',
                 'expected',
                 'observed',
                 'log',
                 'started',
                 'ended']


@implementer(ITestRun)
class TestRun:
   """
   A TestRun contains an ordered sequence of test case classes.
   A test runner instantiates tests from these test case classes.
   The test case classes must derive from WampCase or Case.
   """

   def __init__(self, testee, cases, randomize = False):
      assert(isinstance(testee, Testee))
      self.testee = testee
      _cases = cases[:]
      if randomize:
         random.shuffle(_cases)
      _cases.reverse()
      self._len = len(_cases)
      self._cases = deque(_cases)

   def next(self):
      try:
         return self._cases.pop()
      except IndexError:
         return None

   def remaining(self):
      return len(self._cases)

   def __len__(self):
      return self._len;
