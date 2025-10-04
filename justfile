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
    @just --list

# Check Python 2.7 availability
check-python2:
    #!/usr/bin/env bash
    if ! command -v python2 &> /dev/null; then
        echo "Error: python2 not found. Install with: sudo apt install -y python2"
        exit 1
    fi
    echo "Found Python 2.7: $(python2 --version 2>&1)"

# Create Python 2.7 virtual environment
create-venv: check-python2
    #!/usr/bin/env bash
    set -e
    if [ ! -d "{{VENV_DIR}}/{{VENV_NAME}}" ]; then
        echo "Creating Python 2.7 virtual environment..."
        # Check if virtualenv is available
        if command -v virtualenv &> /dev/null; then
            virtualenv -p python2 "{{VENV_DIR}}/{{VENV_NAME}}"
        else
            echo "Installing virtualenv for Python 2.7..."
            python2 -m pip install --user virtualenv
            python2 -m virtualenv "{{VENV_DIR}}/{{VENV_NAME}}"
        fi
    else
        echo "Virtual environment {{VENV_DIR}}/{{VENV_NAME}} already exists"
    fi

# Install package dependencies
install: create-venv
    #!/usr/bin/env bash
    set -e
    echo "Installing AutobahnTestsuite dependencies..."
    cd {{PACKAGE_DIR}}
    {{VENV_DIR}}/{{VENV_NAME}}/bin/pip install -e .

# Build package
build: install
    #!/usr/bin/env bash
    set -e
    echo "Building AutobahnTestsuite package..."
    cd {{PACKAGE_DIR}}
    rm -rf build/ dist/ *.egg-info/
    {{VENV_DIR}}/{{VENV_NAME}}/bin/python setup.py sdist bdist_wheel

# Clean build artifacts
clean:
    #!/usr/bin/env bash
    echo "Cleaning build artifacts..."
    rm -rf {{PACKAGE_DIR}}/build/
    rm -rf {{PACKAGE_DIR}}/dist/
    rm -rf {{PACKAGE_DIR}}/*.egg-info/
    rm -rf {{VENV_DIR}}/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -delete

# Test installation
test-install: build
    #!/usr/bin/env bash
    set -e
    echo "Testing AutobahnTestsuite installation..."
    cd {{PACKAGE_DIR}}
    {{VENV_DIR}}/{{VENV_NAME}}/bin/wstest --help

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
    {{VENV_DIR}}/{{VENV_NAME}}/bin/pip install twine
    {{VENV_DIR}}/{{VENV_NAME}}/bin/twine upload dist/*

# Publish Docker image (requires credentials)
publish-docker: docker-build
    #!/usr/bin/env bash
    set -e
    echo "Publishing AutobahnTestsuite Docker image..."
    docker push crossbario/autobahn-testsuite:25.10.1
    docker push crossbario/autobahn-testsuite:latest

# Show package info
info:
    #!/usr/bin/env bash
    set -e
    cd {{PACKAGE_DIR}}
    if [ -f "{{VENV_DIR}}/{{VENV_NAME}}/bin/python" ]; then
        echo "Python version:"
        {{VENV_DIR}}/{{VENV_NAME}}/bin/python --version
        echo ""
        echo "AutobahnTestsuite version:"
        {{VENV_DIR}}/{{VENV_NAME}}/bin/python -c "import autobahntestsuite; print(autobahntestsuite.version)"
    else
        echo "Virtual environment not found. Run 'just install' first."
    fi