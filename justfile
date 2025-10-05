# AutobahnTestsuite build automation
# https://github.com/casey/just

# Default Python 2.7 environment for AutobahnTestsuite
PYTHON := "python2"
VENV_DIR := ".venvs"
VENV_NAME := "py27"

# Package directory
PACKAGE_DIR := "autobahntestsuite"

# Default recipe - show available commands
default:
    @echo ""
    @echo "==============================================================================="
    @echo "       Autobahn|Testsuite - WebSocket IETF RF6455 Protocol Testsuite           "
    @echo ""
    @echo "      >>>   Created by The WAMP/Autobahn/Crossbar.io OSS Project   <<<         "
    @echo ""
    @echo " Protocol Spec:    https://datatracker.ietf.org/doc/html/rfc6455               "
    @echo " Source Code:      https://github.com/crossbario/autobahn-testsuite            "
    @echo " Release Packages: https://pypi.org/project/autobahntestsuite/                 "
    @echo " Documentation:    https://autobahntestsuite.readthedocs.io                    "
    @echo " Copyright:        typedef int GmbH (Germany/EU)                               "
    @echo " License:          Apache License 2.0                                          "
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

# Install system dependencies
install-system-deps:
    #!/usr/bin/env bash
    echo "Installing system dependencies for Python 2.7..."
    sudo apt update

    # Try to install python2-dev, fallback to building from source if not available
    if ! sudo apt install -y python2 python2-dev python-setuptools 2>/dev/null; then
        echo "python2-dev not available in this Ubuntu version (likely 24.04+)"
        echo "Will build Python 2.7 from source with headers..."
        just build-python2-from-source
    else
        echo "System python2 with headers installed successfully"
    fi

    echo "Downloading get-pip.py for Python 2.7..."
    if [ ! -f get-pip.py ]; then
        curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py
    fi
    echo "Installing pip2..."
    python2 get-pip.py
    echo "Installing virtualenv..."
    pip -V
    python2 -m pip install virtualenv
    virtualenv --version
    echo "System dependencies installed successfully!"
    echo "Note: You may need to add ~/.local/bin to your PATH"

# Build Python 2.7 from source (fallback for Ubuntu 24.04+)
build-python2-from-source:
    #!/usr/bin/env bash
    set -e
    echo "Building Python 2.7.18 from source..."

    # Install build dependencies
    sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
        libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev

    # Create build directory
    mkdir -p /tmp/python2-build
    cd /tmp/python2-build

    # Download Python 2.7.18 source if not already present
    if [ ! -f Python-2.7.18.tgz ]; then
        echo "Downloading Python 2.7.18 source..."
        wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
    fi

    # Extract and build
    if [ ! -d Python-2.7.18 ]; then
        tar xf Python-2.7.18.tgz
    fi

    cd Python-2.7.18

    # Configure with optimizations
    echo "Configuring Python 2.7.18..."
    ./configure --prefix=/opt/python2.7 --enable-optimizations --enable-shared

    # Build and install
    echo "Building Python 2.7.18 (this may take a while)..."
    make -j$(nproc)
    sudo make install

    # Create symlinks for system-wide access
    sudo ln -sf /opt/python2.7/bin/python2.7 /usr/local/bin/python2
    sudo ln -sf /opt/python2.7/bin/python2.7 /usr/local/bin/python2.7

    # Update library path
    echo '/opt/python2.7/lib' | sudo tee /etc/ld.so.conf.d/python2.7.conf
    sudo ldconfig

    echo "Python 2.7.18 built and installed to /opt/python2.7"
    echo "Symlinks created: /usr/local/bin/python2 -> /opt/python2.7/bin/python2.7"

    # Verify installation
    /opt/python2.7/bin/python2.7 --version

    # Clean up build directory (optional)
    read -p "Clean up build directory /tmp/python2-build? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf /tmp/python2-build
        echo "Build directory cleaned up"
    fi

# Check Python 2.7 and pip2 availability
check-python2:
    #!/usr/bin/env bash
    if ! command -v python2 &> /dev/null; then
        echo "Error: python2 not found. Run 'just install-system-deps' first."
        exit 1
    fi
    echo "Found Python 2.7: $(python2 --version 2>&1)"

    if ! python2 -m pip --version &> /dev/null; then
        echo "Error: pip2 not found. Run 'just install-system-deps' first."
        exit 1
    fi
    echo "Found pip2: $(python2 -m pip --version)"

    if ! python2 -c "import virtualenv" &> /dev/null; then
        echo "Error: virtualenv not found. Run 'just install-system-deps' first."
        exit 1
    fi
    echo "Found virtualenv: OK"

# Create Python 2.7 virtual environment
create-venv: check-python2
    #!/usr/bin/env bash
    set -e
    if [ ! -d "{{VENV_DIR}}/{{VENV_NAME}}" ]; then
        echo "Creating Python 2.7 virtual environment..."
        mkdir -p "{{VENV_DIR}}"
        python2 -m virtualenv "{{VENV_DIR}}/{{VENV_NAME}}"
        echo "Virtual environment created at {{VENV_DIR}}/{{VENV_NAME}}"
    else
        echo "Virtual environment {{VENV_DIR}}/{{VENV_NAME}} already exists"
    fi

# Install package dependencies
install: create-venv
    #!/usr/bin/env bash
    set -e
    echo "Installing AutobahnTestsuite dependencies..."
    cd {{PACKAGE_DIR}}
    ../{{VENV_DIR}}/{{VENV_NAME}}/bin/pip install -e .

# Build package
build: install
    #!/usr/bin/env bash
    set -e
    echo "Building AutobahnTestsuite package..."
    cd {{PACKAGE_DIR}}
    rm -rf build/ dist/ *.egg-info/
    ../{{VENV_DIR}}/{{VENV_NAME}}/bin/python setup.py sdist bdist_wheel

# Clean build artifacts
clean:
    #!/usr/bin/env bash
    echo "Cleaning build artifacts..."
    rm -rf {{PACKAGE_DIR}}/build/
    rm -rf {{PACKAGE_DIR}}/dist/
    rm -rf {{PACKAGE_DIR}}/*.egg-info/
    rm -rf {{VENV_DIR}}/
    rm -rf docs/_build/
    rm -f get-pip.py
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -delete

# Clean everything including custom Python 2.7 installation
distclean: clean
    #!/usr/bin/env bash
    echo "Cleaning all artifacts including custom Python 2.7..."

    # Remove custom Python 2.7 installation
    if [ -d "/opt/python2.7" ]; then
        echo "Removing custom Python 2.7 installation..."
        sudo rm -rf /opt/python2.7
        sudo rm -f /usr/local/bin/python2 /usr/local/bin/python2.7
        sudo rm -f /etc/ld.so.conf.d/python2.7.conf
        sudo ldconfig
        echo "Custom Python 2.7 installation removed"
    fi

    # Clean up build directory if it exists
    if [ -d "/tmp/python2-build" ]; then
        echo "Removing Python 2.7 build directory..."
        rm -rf /tmp/python2-build
        echo "Build directory removed"
    fi

    echo "==> Distclean complete. The project is now pristine."

test-version: install
    #!/usr/bin/env bash
    set -e
    echo "Testing AutobahnTestsuite version..."
    {{VENV_DIR}}/{{VENV_NAME}}/bin/python -c "from autobahntestsuite import __version__; print(__version__)"

# Test installation
test-install: install
    #!/usr/bin/env bash
    set -e
    echo "Testing AutobahnTestsuite installation..."
    cd {{PACKAGE_DIR}}
    ../{{VENV_DIR}}/{{VENV_NAME}}/bin/wstest --help
    ../{{VENV_DIR}}/{{VENV_NAME}}/bin/wstest --autobahnversion

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

# Build documentation
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

# Show package info
info:
    #!/usr/bin/env bash
    set -e
    cd {{PACKAGE_DIR}}
    if [ -f "../{{VENV_DIR}}/{{VENV_NAME}}/bin/python" ]; then
        echo "Python version:"
        ../{{VENV_DIR}}/{{VENV_NAME}}/bin/python --version
        echo ""
        echo "AutobahnTestsuite version:"
        ../{{VENV_DIR}}/{{VENV_NAME}}/bin/python -c "import autobahntestsuite; print(autobahntestsuite.version)"
    else
        echo "Virtual environment not found. Run 'just install' first."
    fi
