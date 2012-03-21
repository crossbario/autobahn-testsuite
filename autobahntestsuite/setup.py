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

from setuptools import setup, find_packages

LONGSDESC = """
Twisted-based WebSocket/WAMP protocol implementation test suite.

AutobahnTestSuite provides a fully automated test suite to verify client and
server implementations of the WebSocket protocol.

The test suite will check an implementation by doing basic WebSocket
conversations, extensive protocol compliance verification and
performance and limits testing.

Contains about 300 test cases covering

   * Framing
   * Pings/Pongs
   * Reserved Bits
   * Opcodes
   * Fragmentation
   * UTF-8 Handling
   * Limits/Performance
   * Closing Handshake
   * Opening Handshake (under development)

More information:

   * http://autobahn.ws/testsuite
   * http://tools.ietf.org/html/rfc6455
   * http://wamp.ws
"""

setup (
   name = 'autobahntestsuite',
   version = '0.5.0',
   description = 'AutobahnTestSuite - WebSocket/WAMP protocol implementation test suite.',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Tavendo GmbH',
   author_email = 'autobahnws@googlegroups.com',
   url = 'http://autobahn.ws/testsuite',
   platforms = ('Any'),
   install_requires = ['setuptools', 'Autobahn>=0.5', 'Twisted>=11.1'],
   packages = find_packages(),
   #packages = ['autobahntestsuite'],
   include_package_data = True,
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
   keywords = 'autobahn autobahn.ws websocket wamp realtime test testsuite rfc6455'
)
