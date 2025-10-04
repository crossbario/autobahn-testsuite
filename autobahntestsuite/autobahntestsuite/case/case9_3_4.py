###############################################################################
##
##  Copyright (c) typedef int GmbH
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

from case9_3_1 import Case9_3_1

class Case9_3_4(Case9_3_1):

   DESCRIPTION = """Send fragmented text message message with message payload of length 4 * 2**20 (4M). Sent out in fragments of 4k."""

   EXPECTATION = """Receive echo'ed text message (with payload as sent)."""

   def init(self):
      self.DATALEN = 4 * 2**20
      self.FRAGSIZE = 4 * 2**10
      self.PAYLOAD = "*" * self.DATALEN
      self.WAITSECS = 100
      self.reportTime = True
