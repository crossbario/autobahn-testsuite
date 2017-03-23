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

from setuptools import setup, find_packages

LONGSDESC = """
Twisted-based WebSocket/WAMP protocol implementation test suite.

Autobahn|Testsuite provides a fully automated test suite to verify client and
server implementations of the WebSocket protocol.

The test suite will check an implementation by doing basic WebSocket
conversations, extensive protocol compliance verification and
performance and limits testing.

Contains over 500 test cases covering

* Framing
* Pings/Pongs
* Reserved Bits
* Opcodes
* Fragmentation
* UTF-8 Handling
* Limits/Performance
* Closing Handshake
* Opening Handshake (under development)
* WebSocket compression (permessage-deflate extension)

Besides the automated test suite, wstest also includes a number
of other handy developer tools:

* WebSocket echo server and client
* WebSocket broadcast server (and client driver)
* Testee modes to test Autobahn itself against the test suite
* wsperf controller and master (see http://www.zaphoyd.com/wsperf)
* WAMP server and client, for developing WAMP implementations

More information:

* http://autobahn.ws/testsuite
* https://github.com/crossbario/autobahn-testsuite
* http://tools.ietf.org/html/rfc6455
* http://wamp.ws
"""


## get version string from "autobahntestsuite/_version.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re
VERSIONFILE="autobahntestsuite/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup (
   name = 'autobahntestsuite',
   version = verstr,
   description = 'AutobahnTestSuite - WebSocket/WAMP protocol implementation test suite.',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Crossbar.io Technologies GmbH',
   author_email = 'autobahnws@googlegroups.com',
   url = 'http://autobahn.ws/testsuite',
   platforms = ('Any'),
   install_requires = ['setuptools',
                       'txaio<=2.1.0',
                       'autobahn[twisted,accelerate]==0.10.9',
                       'jinja2>=2.6',
                       'markupsafe>=0.19',
                       'Werkzeug>=0.9.4',
                       'klein>=0.2.1',
                       'pyopenssl>=0.14',
                       'service_identity>=14.0.0',
                       'unittest2>=1.1.0'],
   packages = find_packages(),
   #packages = ['autobahntestsuite'],
   include_package_data = True,
   package_data = {
        '': ['templates/*.html'],
    },
   zip_safe = False,
   entry_points = {
      'console_scripts': [
         'wstest = autobahntestsuite.wstest:run'
      ]},
   ## http://pypi.python.org/pypi?%3Aaction=list_classifiers
   ##
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 5 - Production/Stable",
                  "Environment :: Console",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Topic :: Internet",
                  "Topic :: Software Development :: Testing"],
   keywords = 'autobahn autobahn.ws websocket wamp realtime test testsuite rfc6455 wstest wsperf'
)
