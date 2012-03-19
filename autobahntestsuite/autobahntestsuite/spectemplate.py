###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
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

SPEC_FUZZINGSERVER = """
{
   "url": "ws://localhost:9001",

   "options": {"failByDrop": false},
   "outdir": "./reports/clients",
   "webport": 8080,

   "cases": ["*"],
   "exclude-cases": [],
   "exclude-agent-cases": {}
}
"""

SPEC_FUZZINGCLIENT = """
{
   "options": {"failByDrop": false},
   "outdir": "./reports/clients",

   "servers": [{"agent": "AutobahnServer", "url": "ws://localhost:9001", "options": {"version": 18}}],

   "cases": ["*"],
   "exclude-cases": [],
   "exclude-agent-cases": {}
}
"""

SPEC_WSPERFCONTROL = """
{
   "options": {
      "rtts": false,
      "quantile_count": 10,
      "digits": 0,
      "sep": "\t",
      "outfile": "report.txt",
      "debug": false
   },
   "servers":  [
                  {
                     "name": "AutobahnServer",
                     "uri": "ws://localhost:9000",
                     "desc": "Autobahn Server on Localhost."
                  }
               ],
   "sizes": [
               [100, 128, 100000, true, true, false]
            ]
}
"""
