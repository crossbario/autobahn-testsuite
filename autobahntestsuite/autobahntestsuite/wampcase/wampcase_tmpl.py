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

__all__ = ['Cases']

## The set of cases we construct and export from this module.
## Everything else is private.
Cases = []

from autobahntestsuite.util import AttributeBag
from wampcase import WampCase, WampCaseFactory, WampCaseProtocol



class WampCase4_1_1_Params(AttributeBag):

   ATTRIBUTES = ['peerCount']


class WampCase4_1_1_Protocol(WampCaseProtocol):

   def test(self):
      ## WAMP session opened and authenticated.

      ## .. may do stuff here ..

      ## Signal the test controller our readiness.
      self.ready()


class WampCase4_1_1_Factory(WampCaseFactory):

   protocol = WampCase4_1_1_Protocol


class WampCase4_1_1(WampCase):

   factory = WampCase4_1_1_Factory
   index = (4, 1, 1, 0)
   description = "A NOP test."
   expectation = "Nothing."
   params = WampCase4_1_1_Params(peerCount = 10)


   def test(self, log, result, clients):
      msg = "NOP test running using %d sessions\n" % len(clients)
      log(msg)
      print msg
      result.passed = True


Cases.append(WampCase4_1_1)
