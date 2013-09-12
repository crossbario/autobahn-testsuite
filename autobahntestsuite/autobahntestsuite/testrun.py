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

__all__ = ("TestRun", "Testee", "TestResult",)


import random, json
from collections import deque

from twisted.python import log

from zope.interface import implementer
from interfaces import ITestRun


class AttributeBag:

   def __init__(self, **args):

      for attr in self.ATTRIBUTES:
         setattr(self, attr, None)

      self.set(args)


   def serialize(self):
      obj = {}
      for attr in self.ATTRIBUTES:
         obj[attr] = getattr(self, attr)
      return json.dumps(obj)


   def deserialize(self, data):
      obj = json.loads(data)
      self.set(obj)


   def set(self, obj):
      for attr in obj.keys():
         if attr in self.ATTRIBUTES:
            setattr(self, attr, obj[attr])
         else:
            if self.debug:
               log.msg("Warning: skipping unknown attribute '%s'" % attr)


   def __repr__(self):
      s = []
      for attr in self.ATTRIBUTES:
         s.append("%s = %s" % (attr, getattr(self, attr)))
      return self.__class__.__name__ + '(' + ', '.join(s) + ')'



class Testee(AttributeBag):

   ATTRIBUTES = ['name',
                 'url',
                 'auth',
                 'debug']



class TestResult(AttributeBag):

   ATTRIBUTES = ['passed',
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
