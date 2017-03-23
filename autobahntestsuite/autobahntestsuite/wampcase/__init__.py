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

__all__ = ("WampCaseSet",
           "Cases",
           "CaseCategories",
           "CaseSubCategories",
           "CaseBasename",)

from autobahntestsuite.caseset import CaseSet

CaseSetname = "wamp"

CaseBasename = "WampCase"


CaseCategories = {"0": "Message format",
                  "1": "Sessions",
                  "2": "Publish and Subscribe",
                  "3": "Remote Procedure Calls",
                  "4": "Authentication and Authorization",
                  "5": "Reflection",
                  "6": "Performance"}

CaseSubCategories = {

   ## Publish and Subscribe
   ##
   "2.1": "Topics and payloads",
   "2.2": "Exclude and eligible",
   "2.3": "Unsubscribe",
   "2.4": "Peer initiated events",

   "2.5": "Publisher identification (WAMPv2)",
   "2.6": "Pattern-based subscriptions (WAMPv2)",
   "2.7": "Metaevents (WAMPv2)",

   ## Remote Procedure Calls
   ##
   "3.1": "Argument and return types",
   "3.2": "Exceptions",
   "3.3": "Reverse calls",
   "3.3": "Call timeouts (WAMPv2)",
   "3.4": "Cancel calls (WAMPv2)",
   "3.5": "Progressive results (WAMPv2)",
   "3.6": "Partitioned calls (WAMPv2)",
}


import wampcase2_2_x_x
import wampcase3_1_x_x

## all WAMP test cases
##
Cases = []
#Cases.extend(wampcase2_2_x_x.Cases)
#Cases.extend(wampcase3_1_x_x.Cases)

import wampcase2_5_x_x
Cases.extend(wampcase2_5_x_x.Cases)


class WampCaseSet(CaseSet):

   def __init__(self):
      CaseSet.__init__(self, CaseSetname, CaseBasename, Cases, CaseCategories, CaseSubCategories)
