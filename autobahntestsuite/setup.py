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

from setuptools import setup, find_packages

LONGSDESC = """
WebSocket protocol implementation conformance test suite.

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

Protocol Spec:    https://datatracker.ietf.org/doc/html/rfc6455
Source Code:      https://github.com/crossbario/autobahn-testsuite
Release Packages: https://pypi.org/project/autobahntestsuite
Documentation:    https://autobahntestsuite.readthedocs.io
Copyright:        typedef int GmbH (Germany/EU)
License:          Apache License 2.0
"""


## get version string from "autobahntestsuite/_version.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re

VERSIONFILE = "autobahntestsuite/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup(
    name="autobahntestsuite",
    version=verstr,
    description="AutobahnTestSuite - WebSocket protocol implementation conformance test suite.",
    long_description=LONGSDESC,
    license="Apache License 2.0",
    author="typedef int GmbH",
    url="https://github.com/crossbario/autobahn-testsuite",
    platforms=("Any"),
    # pinned dependency set for Python 2.7 / Autobahn 0.10.9
    install_requires=[
        "setuptools==44.0.0",  # pip/setuptools from pre-2020 era
        "txaio==2.1.0",
        "incremental==16.10.1",  # must pin because of use of typing
        "pyOpenSSL==19.1.0",
        "cryptography==3.3.2",  # last version supporting Python 2 and OpenSSL 1.1
        "Twisted==19.10.0",  # pin Twisted 19.10.0., 20.3.0 is technically Python 2.7-compatible, but its packaging metadata triggers installation of newer incremental eggs.
        "zope.interface==4.6.0",  # Twisted dependency compatible with 2.7
        "jinja2==2.11.3",
        "markupsafe==1.1.1",
        "Werkzeug==1.0.1",
        "klein==17.10.0",  # last pre-Python3-only Klein
        "pyopenssl==19.1.0",
        "service_identity==18.1.0",
        "unittest2==1.1.0",
        "six==1.16.0",
        "autobahn[twisted,accelerate]==0.10.9",
    ],
    packages=find_packages(),
    # packages = ['autobahntestsuite'],
    include_package_data=True,
    package_data={
        "": ["templates/*.html"],
    },
    zip_safe=False,
    entry_points={"console_scripts": ["wstest = autobahntestsuite.wstest:run"]},
    ## http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ##
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: Twisted",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Testing",
    ],
    keywords="autobahn websocket wamp realtime test testsuite rfc6455 wstest wsperf",
)
