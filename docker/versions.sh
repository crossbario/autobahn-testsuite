#!/bin/sh

#
# CHANGE FOR NEW RELEASES (these need to be proper Git tags in the respective repo):
#
export AUTOBAHN_TESTSUITE_VERSION='0.7.6'
#
# END OF CONFIG
#

#
# Git working directories of all relevant repos must reside
# in parallel (as siblings) to this repository
#
export AUTOBAHN_TESTSUITE_VCS_REF=`git --git-dir="../autobahn-testsuite/.git" rev-list -n 1 v${AUTOBAHN_TESTSUITE_VERSION} --abbrev-commit`
export BUILD_DATE=`date -u +"%Y-%m-%d"`

echo ""
echo "The Crossbar.io Project (build date ${BUILD_DATE})"
echo ""
echo "autobahn-testsuite ${AUTOBAHN_TESTSUITE_VERSION} [${AUTOBAHN_TESTSUITE_VCS_REF}]"
echo ""
