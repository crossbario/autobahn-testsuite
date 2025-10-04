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

from _version import __version__

version = __version__  # backward compat.

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings(
    "ignore", message="Python 2 is no longer supported by the Python core team.*"
)

import choosereactor  # This MUST BE the FIRST file imported here! Do NOT touch.
import wstest
import echo
import broadcast
import testee

# import wsperfcontrol
# import wsperfmaster
import case
import caseset
import report
import spectemplate
import fuzzing

# import wampfuzzing
# import wamptestserver
import massconnect
