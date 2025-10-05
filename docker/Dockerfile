# =====================================================================
# Copyright (c) typedef int GmbH, Germany, 2025. All rights reserved.
# Licensed under Apache 2.0.
#
# Autobahn|Testsuite "Frozen Image"
#
# This image is pinned to the last viable combination of
# Python 2.7, PyPy, and OpenSSL 1.1 — preserving full
# interoperability with historic WebSocket protocol test tooling.
#
# Base:
#   PyPy 7.3.11 (Python 2.7.18) on Debian Bullseye
#
# DO NOT UPGRADE THIS IMAGE to "bookworm" or newer:
#   → OpenSSL 3.x breaks cryptography<3.4 on PyPy 2.7
#   → No PyPy2 binary wheels are built against OpenSSL 3
# =====================================================================

FROM pypy:2-7-bullseye

# The base image (Debian 11 / pypy:2-7-bullseye) bundles:
#
# - PyPy 7.3.11 (Python 2.7.18)
# - OpenSSL 1.1.1w
#
# safe working combo for PyPy2 on Debian 11:
#
# Package       Version     Reason
#
# pip	        20.3.4	    last version supporting Py2 reliably
# setuptools	44.0.0	    same reason
# wheel	        0.36.2	    safe
# incremental	16.10.1	    Twisted compatibility
# Twisted	    19.10.0	    last Py2 buildable
# pyOpenSSL	    19.1.0	    last Py2 buildable
# cryptography	3.3.2	    last Py2-safe, avoids FIPS symbol

LABEL maintainer="The WAMP/Autobahn/Crossbar.io OSS Project"

# Metadata
ARG BUILD_DATE
ARG AUTOBAHN_TESTSUITE_VERSION
ARG AUTOBAHN_TESTSUITE_VCS_REF

# Metadata labeling
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="AutobahnTestsuite Toolchain Image" \
      org.label-schema.description="Toolchain image that contains the AutobahnTestsuite" \
      org.label-schema.url="http://crossbar.io" \
      org.label-schema.vcs-ref=$AUTOBAHN_TESTSUITE_VCS_REF \
      org.label-schema.vcs-url="https://github.com/crossbario/autobahn-testsuite" \
      org.label-schema.vendor="The WAMP/Autobahn/Crossbar.io OSS Project" \
      org.label-schema.version=$AUTOBAHN_TESTSUITE_VERSION \
      org.label-schema.schema-version="1.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_PATH=/usr/local/lib/node_modules/

# make "pypy" available as "python"
RUN ln -s /usr/local/bin/pypy /usr/local/bin/python

# make sure we use old pip & setuptools that don't isolate builds
RUN pip install 'pip==20.3.4' 'setuptools==44.0.0' 'wheel==0.36.2'

# pre-install old incremental before Twisted even tries setup_requires
RUN pip install 'incremental==16.10.1'

# last version supporting Python 2 and OpenSSL 1.1
RUN pip install 'pyOpenSSL==19.1.0'
RUN pip install 'cryptography==3.3.2'

# pin Twisted 19.10.0., 20.3.0 is technically Python 2.7-compatible,
# but its packaging metadata triggers installation of newer incremental eggs.
RUN pip install --no-build-isolation 'Twisted==19.10.0'

# copy Autobahn|Testsuite wheel
RUN mkdir /wheels
COPY autobahntestsuite-latest-py2-none-any.whl /wheels

# install Autobahn|Testsuite from wheel
RUN pip install --no-build-isolation /wheels/autobahntestsuite-latest-py2-none-any.whl
RUN wstest --version

# make volumes for input configuration and output reports
VOLUME /config
VOLUME /reports

WORKDIR /

# by default, only expose port 9001 (which is used by default in fuzzingserver) from container
EXPOSE 9001 9001

# run wstest by default in fuzzingserver mode
CMD ["wstest", "--mode", "fuzzingserver", "--spec", "/config/fuzzingserver.json"]
