# Changelog

## Unreleased

* Adopt the contribution workflow shared by all WAMP projects: `CONTRIBUTING.md`, the pull request template and `.audit/README.md` are deployed byte-identically from wamp-cicd (GitHub issue first, red → green tests, AI-assistance disclosure) and kept in sync by a CI drift check; project-specific notes moved to a new `DEVELOPMENT.md`. `.cicd` and `.ai` are pinned to the same commits across the WAMP fleet, and the shared workflow recipes (`just where`, `new-branch`, `publish`, `land`) are imported (#163)

## v0.6.3

* maintenance release

## v0.6.2

* new mode for generating WAMP message serializations

## v0.6.1

* permessage-deflate tests with different parameters and fragmentation
 
## v0.6.0

* compatibility with Autobahn|Python 0.8.1

## v0.5.7

* compatibility with Autobahn|Python 0.7.0

## v0.5.6

* compatibility with AutobahnPython 0.6.3
* new test section for testing WebSocket compression extension (`permessage-deflate` etc)
* beginning of WAMP testsuite
* more UTF8 test strings

## v0.5.5

* do not include invalid UTF8 test strings in report result pages (html/json)

## v0.5.4

* make Jython happy (now runs on Jython 2.7b1 with slightly patched Twisted)
* add detailed description of how we generate public reports
* log UTF8 and XOR masker classes in use

## v0.5.3

* add JSON output for test results
* WSS testing support
* more UTF-8 tests

