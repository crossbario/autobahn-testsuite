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

from twisted.python import log
import json


class WampCase:

   FAILED = "FAILED"
   OK = "OK"
   
   SUBCASES = []

   def __init__(self, protocol):
      self.p = protocol
      self.init()

   def getSubcaseCount(self):
      return len(Case.SUBCASES)

   def setSubcase(self, subcase):
      self.subcase = subcase

   def init(self):
      pass

   def compare(self, obj1, obj2):
      return json.dumps(obj1) == json.dumps(obj2)
