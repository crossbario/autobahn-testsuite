# Development

Notes specific to **Autobahn|Testsuite**: what may and may not change, the stable interface, and
development setup. The contribution workflow shared by all WAMP projects — GitHub issue first,
red → green tests, and the AI-assistance disclosure — is in [CONTRIBUTING.md](CONTRIBUTING.md).

## The test cases are frozen by design

Autobahn|Testsuite is a conformance and fuzzing tool that other WebSocket implementations are
measured against, release after release. A tool like that has to behave like a **constant**: you
cannot meaningfully test an implementation against a moving oracle. That is why the testsuite is
intentionally hard-pinned to the older Autobahn|Python release that still carries the fuzzing case
classes, and why the **stock test cases are not changed**.

- **The stable, public interface** is the JSON configuration (`fuzzingserver.json`,
  `fuzzingclient.json`) and the `wstest` command line: how you point the suite at an implementation,
  select or exclude cases, and set options such as `failByDrop`.
- **New probes** (for example a new frame sequence) are deliberately *not* part of that interface.
  Build them in your own harness and keep their results separate from the stock ones.
- **A gap in the suite** is demonstrated by a WebSocket wire-level log where an implementation emits
  octets that are **invalid per RFC 6455** while a stock case reports **green**. That is the kind of
  finding that can justify a change to the suite itself. An internal fault that never becomes visible
  on the wire is not something a wire-level oracle can, or should, detect.

The contribution process (issues, pull requests, disclosure) applies to everything else: packaging,
the Docker image, documentation, and tooling.

## Development setup

Development is driven by [`just`](https://github.com/casey/just); run `just` to list all recipes. The
testsuite itself runs on **Python 2.7** (the pinned fuzzing code); the tools around it (docs,
packaging) use a Python 3 environment managed with `uv`.

```bash
git clone https://github.com/crossbario/autobahn-testsuite.git
cd autobahn-testsuite
git submodule update --init --recursive
just install-python2        # Python 2.7, from the distribution or built from source
just create-venv            # Python 2.7 virtual environment
just install                # install the testsuite
just test-version           # sanity checks of the installed package
just test-wstest
```

The recommended way to *use* the testsuite is the Docker image (see README.md):
`just docker-build` and `just docker-test` build and check it locally.

## Documentation

`just docs` builds the documentation (`just docs-serve` for a live server).
