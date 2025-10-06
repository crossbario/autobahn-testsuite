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

import io
import os
import re
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
VERSIONFILE = "autobahntestsuite/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


def read_requirements(filename):
    """
    Read requirements.txt from source or from inside a built package.
    Compatible with Python 2.7 (uses pkg_resources fallback).
    """
    import os
    import io

    here = os.path.abspath(os.path.dirname(__file__))
    candidates = [
        os.path.join(here, filename),
        os.path.join(here, "autobahntestsuite", filename),
    ]

    for path in candidates:
        if os.path.exists(path):
            with io.open(path, encoding="utf-8") as f:
                return [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]

    # --- Fallback: load via pkg_resources (when running from wheel / installed dist) ---
    try:
        import pkg_resources

        data = pkg_resources.resource_string("autobahntestsuite", filename)
        text = data.decode("utf-8")
        return [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.startswith("#")
        ]
    except Exception as e:
        print("Warning: requirements file not found ({}) => {}".format(filename, e))
        return []


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
    install_requires=read_requirements("requirements.txt"),
    packages=find_packages(),
    # packages = ['autobahntestsuite'],
    include_package_data=True,
    package_data={
        "autobahntestsuite": ["requirements.txt", "templates/*.html"],
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
