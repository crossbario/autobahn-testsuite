# Copyright (c) typedef int GmbH, Germany, 2025. All rights reserved.
#

# -----------------------------------------------------------------------------
# -- just global configuration
# -----------------------------------------------------------------------------

set unstable := true
set positional-arguments := true
set script-interpreter := ['uv', 'run', '--script']

# uv env vars
# see: https://docs.astral.sh/uv/reference/environment/

# project base directory = directory of this justfile
PROJECT_DIR := justfile_directory()

# Default Python 2.7 environment for AutobahnTestsuite packaging
PYTHON := "python2"
VENV_DIR := ".venvs"
VENV_NAME := "py27"

# Package directory
PACKAGE_DIR := "autobahntestsuite"

# Default recipe - show available commands
default:
    @echo ""
    @echo "==============================================================================="
    @echo "                             Autobahn|Testsuite                                "
    @echo ""
    @echo "          WebSocket Protocol Implementation Conformance Testsuite              "
    @echo ""
    @echo "   Protocol Specification: https://datatracker.ietf.org/doc/html/rfc6455       "
    @echo "   Documentation:          https://autobahntestsuite.readthedocs.io            "
    @echo "   Package Releases:       https://pypi.org/project/autobahntestsuite/         "
    @echo "   Source Code:            https://github.com/crossbario/autobahn-testsuite    "
    @echo "   Copyright:              typedef int GmbH (Germany/EU)                       "
    @echo "   License:                Apache License 2.0                                  "
    @echo ""
    @echo "      >>>   Created by The WAMP/Autobahn/Crossbar.io OSS Project   <<<         "
    @echo "==============================================================================="
    @echo ""
    @just --list
    @echo ""

# -----------------------------------------------------------------------------
# -- General/global helper recipes
# -----------------------------------------------------------------------------

# Setup bash tab completion for the current user (to activate: `source ~/.config/bash_completion`).
setup-completion:
    #!/usr/bin/env bash
    set -e

    COMPLETION_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/bash_completion"
    MARKER="# --- Just completion ---"

    echo "==> Setting up bash tab completion for 'just'..."

    # Check if we have already configured it.
    if [ -f "${COMPLETION_FILE}" ] && grep -q "${MARKER}" "${COMPLETION_FILE}"; then
        echo "--> 'just' completion is already configured."
        exit 0
    fi

    echo "--> Configuration not found. Adding it now..."

    # 1. Ensure the directory exists.
    mkdir -p "$(dirname "${COMPLETION_FILE}")"

    # 2. Add our marker comment to the file.
    echo "" >> "${COMPLETION_FILE}"
    echo "${MARKER}" >> "${COMPLETION_FILE}"

    # 3. CRITICAL: Run `just` and append its raw output directly to the file.
    #    No `echo`, no `eval`, no quoting hell. Just run and redirect.
    just --completions bash >> "${COMPLETION_FILE}"

    echo "--> Successfully added completion logic to ${COMPLETION_FILE}."

    echo ""
    echo "==> Setup complete. Please restart your shell or run the following command:"
    echo "    source \"${COMPLETION_FILE}\""

# Clean build artifacts
clean:
    #!/usr/bin/env bash
    set -e
    echo "Cleaning build artifacts..."
    rm -rf {{PACKAGE_DIR}}/build/
    rm -rf {{PACKAGE_DIR}}/dist/
    rm -rf {{PACKAGE_DIR}}/*.egg-info/
    rm -rf docs/_build/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -delete

# Clean everything including custom Python 2.7 installation
distclean: clean
    #!/usr/bin/env bash
    set -e
    echo "==============================================================================="
    echo "Cleaning all artifacts including custom Python 2.7..."

    rm -rf {{VENV_DIR}}/

    if [ -d "/tmp/python2-build" ]; then
        echo "Removing Python 2.7 build directory..."
        rm -rf /tmp/python2-build
        echo "Build directory removed"
    fi

    rm -f /tmp/get-pip.py

    if [ -d "docker/reports/" ]; then
        echo "Removing reports directory for Docker image baking ..."
        rm -rf docker/reports/
        mkdir docker/reports/
        echo "Reports directory for Docker image baking removed"
    fi

    echo "==> Distclean complete. The project is now pristine."

# -----------------------------------------------------------------------------
# -- General/global helper recipes
# -----------------------------------------------------------------------------

# Install Python 2.7 (development), either from distro package or build from source.
install-python2:
    #!/usr/bin/env bash
    set -e
    echo "==============================================================================="
    echo "Checking for Python 2.7 ..."
    if ! command -v python2 >/dev/null 2>&1; then
        echo "python2 not found!"

        echo "Checking for python2-dev package availability..."
        if ! apt-cache show python2-dev >/dev/null 2>&1; then
            echo "python2-dev not available on this distro, will instead build Python 2.7 from upstream source ..."
            just install-python2-from-source
        else
            echo "Installing python2 and development packages from distro ..."
            sudo apt install -y python2 python2-dev python-setuptools
            echo "python2 development package installed successfully from distro package."
        fi
    fi
    echo ""
    echo "python2 found at $(command -v python2) with version $$(python2 -V 2>&1)"

# Build Python 2.7 from upstream source into `~/.local/python2.7`
install-python2-from-source:
    #!/usr/bin/env bash
    set -e
    set -o pipefail

    PREFIX="${HOME}/.local/python2.7"
    SRC_DIR="/tmp/python2-build"
    VERSION="2.7.18"

    echo "==============================================================================="
    echo "🔧 Building CPython ${VERSION} into ${PREFIX}"

    # --- Install build dependencies ---------------------------------------------------------
    echo "Installing build dependencies (requires sudo)..."
    sudo apt-get update -qq
    sudo apt-get install -y \
        build-essential wget curl \
        zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev \
        libreadline-dev libffi-dev libsqlite3-dev libbz2-dev liblzma-dev tk-dev uuid-dev

    # --- Prepare source --------------------------------------------------------------------
    mkdir -p "${SRC_DIR}"
    cd "${SRC_DIR}"

    if [ ! -f Python-${VERSION}.tgz ]; then
        echo "Downloading Python ${VERSION} source..."
        wget -q https://www.python.org/ftp/python/${VERSION}/Python-${VERSION}.tgz
    fi

    if [ ! -d Python-${VERSION} ]; then
        tar xf Python-${VERSION}.tgz
    fi
    cd Python-${VERSION}

    # --- Configure & build -----------------------------------------------------------------
    echo "Configuring build..."
    ./configure \
        --prefix="${PREFIX}" \
        --enable-optimizations \
        --enable-shared \
        CFLAGS="-fPIC"

    echo "Building (this may take a few minutes)..."
    make -j"$(nproc)"

    echo "Installing to ${PREFIX}..."
    make install

    # --- Post-install ----------------------------------------------------------------------
    echo "Updating runtime linker path..."
    mkdir -p "${PREFIX}/lib"
    echo "${PREFIX}/lib" > "${PREFIX}/lib/python2.7.conf"
    sudo sh -c "echo '${PREFIX}/lib' > /etc/ld.so.conf.d/python2.7-local.conf"
    sudo ldconfig

    # --- Environment integration -----------------------------------------------------------
    if ! grep -q "${PREFIX}/bin" "${HOME}/.bashrc" 2>/dev/null; then
        echo "export PATH=\"${PREFIX}/bin:\$PATH\"" >> "${HOME}/.bashrc"
        echo "PATH updated in ~/.bashrc"
    fi

    echo
    echo "✅ Python ${VERSION} built successfully!"
    echo "   Installed at: ${PREFIX}"
    echo "   Binary:       ${PREFIX}/bin/python2.7"
    echo "   To activate immediately:  export PATH=\"${PREFIX}/bin:\$PATH\""
    echo

    # Create a convenient symlink so "python2" works
    ln -sf "${PREFIX}/bin/python2.7" "${PREFIX}/bin/python2"
    echo "Created symlink: ${PREFIX}/bin/python2 -> python2.7"

    "${PREFIX}/bin/python2" --version
    echo "Note: You may need to add ~/${PREFIX}/bin to your PATH"

# Install Python 2.7 package dependencies (pip2 & virtualenv)
install-python2-deps: install-python2
    #!/usr/bin/env bash
    echo "==============================================================================="
    echo "Checking for Python 2.7 package dependencies ..."
    echo ""
    if ! python2 -m pip --version &> /dev/null; then
        echo "Error: pip2 not found. Downloading get-pip.py for Python 2.7..."
        curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o /tmp/get-pip.py
        python2 /tmp/get-pip.py
    else
        echo "pip2 already installed."
    fi
    echo ""
    echo "Found pip2: $(python2 -m pip --version 2>&1)"

    if ! python2 -m virtualenv --version &> /dev/null; then
        echo "Error: virtualenv not found. Installing via pip2 ..."
        python2 -m pip install virtualenv
    else
        echo "virtualenv already installed."
    fi
    echo ""
    echo "Found virtualenv: $(python2 -m virtualenv --version 2>&1)"

# -----------------------------------------------------------------------------
# -- General/global helper recipes
# -----------------------------------------------------------------------------

# Create Python 2.7 virtual environment
create-venv: install-python2-deps
    #!/usr/bin/env bash
    set -e
    echo "==============================================================================="
    echo "Checking for Python 2.7 virtual environment ..."
    echo ""
    if [ ! -d "{{VENV_DIR}}/{{VENV_NAME}}" ]; then
        echo "Creating Python 2.7 virtual environment..."
        mkdir -p "{{VENV_DIR}}"
        python2 -m virtualenv "{{VENV_DIR}}/{{VENV_NAME}}"
        echo "Virtual environment created at {{VENV_DIR}}/{{VENV_NAME}}"
    else
        echo "Virtual environment {{VENV_DIR}}/{{VENV_NAME}} already exists."
    fi
    echo ""
    echo "To activate, run: source {{VENV_DIR}}/{{VENV_NAME}}/bin/activate"

# Install package with dependencies
install: create-venv
    #!/usr/bin/env bash
    set -e
    echo "==============================================================================="
    echo "Checking for AutobahnTestsuite installed package ..."
    echo ""
    if ! python2 -m pip show autobahntestsuite &> /dev/null; then
        echo "Installing AutobahnTestsuite ..."
        cd {{PACKAGE_DIR}}
        ../{{VENV_DIR}}/{{VENV_NAME}}/bin/pip install -e .
    else
        echo "AutobahnTestsuite already installed."
    fi

# Build package
build: install
    #!/usr/bin/env bash
    set -e
    echo "==============================================================================="
    echo "Checking for AutobahnTestsuite built package ..."
    echo ""
    if [ ! "{{PACKAGE_DIR}}/dist/" ]; then
        echo "Building AutobahnTestsuite package..."
        cd {{PACKAGE_DIR}}
        rm -rf build/ dist/ *.egg-info/
        ../{{VENV_DIR}}/{{VENV_NAME}}/bin/python setup.py sdist bdist_wheel
        cd ..
    else
        echo "AutobahnTestsuite package already built."
    fi
    echo ""
    echo "{{PACKAGE_DIR}}/dist/:"
    ls -la {{PACKAGE_DIR}}/dist/

# -----------------------------------------------------------------------------
# -- Test recipes
# -----------------------------------------------------------------------------

# Test AutobahnTestsuite package show version
test-version:
    #!/usr/bin/env bash
    set -e
    if [ -f "{{VENV_DIR}}/{{VENV_NAME}}/bin/python" ]; then
        {{VENV_DIR}}/{{VENV_NAME}}/bin/python --version
        echo ""
        echo "AutobahnTestsuite package version:"
        cd {{PACKAGE_DIR}}
        ../{{VENV_DIR}}/{{VENV_NAME}}/bin/python -c "import autobahntestsuite; print(autobahntestsuite.version)"
    else
        echo "Virtual environment not found. Run 'just install' first."
    fi

# Test AutobahnTestsuite package installed scripts (`wstest`)
test-wstest:
    #!/usr/bin/env bash
    set -e
    if [ -f "{{VENV_DIR}}/{{VENV_NAME}}/bin/python" ]; then
        "{{VENV_DIR}}/{{VENV_NAME}}"/bin/python --version
        echo ""
        echo "AutobahnTestsuite package installed scripts (wstest):"
        cd {{PACKAGE_DIR}}
        "../{{VENV_DIR}}/{{VENV_NAME}}/bin/wstest" --help
        "../{{VENV_DIR}}/{{VENV_NAME}}/bin/wstest" --autobahnversion
    else
        echo "Virtual environment not found. Run 'just install' first."
    fi

# -----------------------------------------------------------------------------
# -- Docker image recipes
# -----------------------------------------------------------------------------

# Build Docker image
docker-build:
    #!/usr/bin/env bash
    set -e
    echo "Building AutobahnTestsuite Docker image..."
    cd docker
    docker build \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg AUTOBAHN_TESTSUITE_VERSION=25.10.1 \
        --build-arg AUTOBAHN_TESTSUITE_VCS_REF=$(git rev-parse --short HEAD) \
        -t crossbario/autobahn-testsuite:25.10.1 \
        -t crossbario/autobahn-testsuite:latest \
        .

# Test Docker image
docker-test: docker-build
    #!/usr/bin/env bash
    set -e
    echo "Testing AutobahnTestsuite Docker image..."
    docker run --rm crossbario/autobahn-testsuite:25.10.1 wstest --help

# -----------------------------------------------------------------------------
# -- Publish recipes
# -----------------------------------------------------------------------------

# Publish to PyPI (requires credentials)
publish-pypi: build
    #!/usr/bin/env bash
    set -e
    echo "Publishing AutobahnTestsuite to PyPI..."
    cd {{PACKAGE_DIR}}
    ../{{VENV_DIR}}/{{VENV_NAME}}/bin/pip install twine
    ../{{VENV_DIR}}/{{VENV_NAME}}/bin/twine upload dist/*

# Publish Docker image (requires credentials)
publish-docker: docker-build
    #!/usr/bin/env bash
    set -e
    echo "Publishing AutobahnTestsuite Docker image..."
    docker push crossbario/autobahn-testsuite:25.10.1
    docker push crossbario/autobahn-testsuite:latest

# -----------------------------------------------------------------------------
# -- Documentation recipes
# -----------------------------------------------------------------------------

# Build AutobahnTestsuite documentation
docs:
    #!/usr/bin/env bash
    set -e
    echo "Building documentation..."

    # Check if docs directory exists, create basic structure if not
    if [ ! -d "docs" ]; then
        echo "Creating docs directory structure..."
        mkdir -p docs/_static docs/_templates
    fi

    # Install documentation dependencies
    pip3 install sphinx sphinx-rtd-theme

    # Build HTML documentation
    cd docs
    sphinx-build -b html . _build/html
    echo "Documentation built in docs/_build/html/"

# Clean documentation
docs-clean:
    #!/usr/bin/env bash
    echo "Cleaning documentation build artifacts..."
    rm -rf docs/_build/

# Live documentation server
docs-serve: docs
    #!/usr/bin/env bash
    set -e
    echo "Starting documentation server..."
    cd docs/_build/html
    python3 -m http.server 8080
