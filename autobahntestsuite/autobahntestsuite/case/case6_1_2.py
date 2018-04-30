from __future__ import absolute_import
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

from .case import Case

class Case6_1_2(Case):

   DESCRIPTION = """Send fragmented text message, 3 fragments each of length 0."""

   EXPECTATION = """A message is echo'ed back to us (with empty payload)."""

   def onOpen(self):
      self.expected[Case.OK] = [("message", b"", False)]
      self.expectedClose = {"closedByMe": True,
                            "closeCode": [self.p.CLOSE_STATUS_CODE_NORMAL],
                            "requireClean": True}
      self.p.sendFrame(opcode = 1, fin = False, payload = b"")
      self.p.sendFrame(opcode = 0, fin = False, payload = b"")
      self.p.sendFrame(opcode = 0, fin = True, payload = b"")
      self.p.closeAfter(1)
