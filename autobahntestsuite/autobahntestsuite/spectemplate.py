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

__all__= ("SPEC_FUZZINGSERVER",
          "SPEC_FUZZINGCLIENT",
          "SPEC_FUZZINGWAMPSERVER",
          "SPEC_FUZZINGWAMPCLIENT",
          "SPEC_WSPERFCONTROL",
          "SPEC_MASSCONNECT",)


SPEC_FUZZINGSERVER = """
{
   "url": "ws://127.0.0.1:9001",
   "outdir": "./reports/clients",
   "cases": ["*"],
   "exclude-cases": [],
   "exclude-agent-cases": {}
}
"""

SPEC_FUZZINGCLIENT = """
{
   "outdir": "./reports/servers",
   "servers": [
      {
         "url": "ws://127.0.0.1:9001"
      }
   ],
   "cases": ["*"],
   "exclude-cases": [],
   "exclude-agent-cases": {}
}
"""

SPEC_FUZZINGWAMPSERVER = """
{
   "url": "ws://127.0.0.1:9001",
   "options": {},
   "outdir": "./reports/wampclients",
   "cases": ["*"],
   "exclude-cases": [],
   "exclude-agent-cases": {}
}
"""

SPEC_FUZZINGWAMPCLIENT = """
{
   "options": {},
   "outdir": "./reports/wampservers",

   "testees": [
                  {
                     "name": "AutobahnPython",
                     "url": "ws://127.0.0.1:9001",
                     "options": {},
                     "auth": null
                  }
               ],

   "cases": ["*"],
   "exclude-cases": [],
   "exclude-agent-cases": {}
}
"""

SPEC_WSPERFCONTROL = """
{
   "options": {
      "debug": false
   },
   "servers":  [
                  {
                     "name": "AutobahnPython",
                     "uri": "ws://127.0.0.1:9000",
                     "desc": "Autobahn WebSocket Python on localhost"
                  }
               ],
   "testsets": [
      {
         "mode": "echo",
         "options": {
            "outfile": "report_echo.txt",
            "digits": 0,
            "sep": "\\t",
            "rtts": false,
            "quantile_count": 10,

            "count": 1000,
            "timeout": 100000,
            "binary": false,
            "sync": true,
            "verify": false
         },
         "cases": [
                     {"size": 0},
                     {"size": 64},
                     {"size": 1024},
                     {"count": 100, "size": 524288}
                  ]
      }
   ]
}
"""

SPEC_MASSCONNECT = """
{
   "options": {
      "connections": 10000,
      "batchsize": 100,
      "batchdelay": 10,
      "retrydelay": 10
   },
   "servers":  [
                  {
                     "name": "AutobahnPython",
                     "uri": "ws://127.0.0.1:9000",
                     "desc": "Autobahn WebSocket Python on localhost"
                  }
               ]
}
"""
