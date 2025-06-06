# Makefile for Network Calculator System
# =====================================
# 
# This Makefile provides convenient commands for building, testing,
# and running the calculator system components.
#
# Author: Network Programming Course
# Version: 1.0

# Configuration
PYTHON = python3
NODE = node
JAVA = java
JAVAC = javac
HOST = localhost
PORT = 8080

# Default target
.PHONY: help
help:
	@echo "Network Calculator System - Makefile"
	@echo "===================================="
	@echo ""
	@echo "Available targets:"
	@echo ""
	@echo "Build targets:"
	@echo "  build-java          - Compile Java client"
	@echo "  build-all           - Build all components"
	@echo ""
	@echo "Server targets:"
	@echo "  server-v1           - Run single-threaded server"
	@echo "  server-v2           - Run multi-threaded server"
	@echo "  server-v1-custom    - Run server v1 with custom port"
	@echo "  server-v2-custom    - Run server v2 with custom settings"
	@echo ""
	@echo "Client targets:"
	@echo "  client-python       - Run Python client"
	@echo "  client-js           - Run JavaScript client"
	@echo "  client-java         - Run Java client"
	@echo ""
	@echo "Testing targets:"
	@echo "  test-functional     - Run functional tests"
	@echo "  test-protocol       - Run protocol compliance tests"
	@echo "  test-performance    - Run performance tests"
	@echo "  test-stress         - Run stress tests"
	@echo "  test-errors         - Run error handling tests"
	@echo "  test-all            - Run all tests"
	@echo ""
	@echo "Demo targets:"
	@echo "  demo-basic          - Basic demonstration"
	@echo "  demo-concurrent     - Concurrent clients demo"
	@echo "  demo-errors         - Error handling demo"
	@echo ""
	@echo "Utility targets:"
	@echo "  clean               - Clean generated files"
	@echo "  install-deps        - Install dependencies"
	@echo "  check-deps          - Check if dependencies are available"
	@echo ""
	@echo "Configuration:"
	@echo "  HOST = $(HOST)"
	@echo "  PORT = $(PORT)"
	@echo ""
	@echo "Examples:"
	@echo "  make server-v2"
	@echo "  make client-python"
	@echo "  make test-all"
	@echo "  make PORT=9000 server-v1"

# Build targets
.PHONY: build-java build-all
build-java:
	@echo "Compiling Java client..."
	$(JAVAC) CalculatorClient.java
	@echo "Java client compiled successfully"

build-all: build-java
	@echo "All components built successfully"

# Server targets
.PHONY: server-v1 server-v2 server-v1-custom server-v2-custom
server-v1:
	@echo "Starting single-threaded server on port $(PORT)..."
	$(PYTHON) server_v1.py $(PORT)

server-v2:
	@echo "Starting multi-threaded server on $(HOST):$(PORT)..."
	$(PYTHON) server_v2.py $(PORT) $(HOST)

server-v1-custom:
	@echo "Starting single-threaded server with custom settings..."
	@read -p "Enter port [$(PORT)]: " port; \
	$(PYTHON) server_v1.py $${port:-$(PORT)}

server-v2-custom:
	@echo "Starting multi-threaded server with custom settings..."
	@read -p "Enter port [$(PORT)]: " port; \
	read -p "Enter host [$(HOST)]: " host; \
	read -p "Enter max workers [10]: " workers; \
	$(PYTHON) server_v2.py $${port:-$(PORT)} $${host:-$(HOST)} $${workers:-10}

# Client targets
.PHONY: client-python client-js client-java client-python-batch client-java-batch
client-python:
	@echo "Starting Python client..."
	$(PYTHON) client_python.py --host $(HOST) --port $(PORT)

client-js:
	@echo "Starting JavaScript client..."
	$(NODE) client_javascript.js --host $(HOST) --port $(PORT)

client-java: build-java
	@echo "Starting Java client..."
	$(JAVA) CalculatorClient --host $(HOST) --port $(PORT)

client-python-batch:
	@echo "Running Python client in batch mode..."
	$(PYTHON) client_python.py --host $(HOST) --port $(PORT) --batch "ADD 5 3" "MUL 7 6" "SQRT 16" "DIV 10 2"

client-java-batch: build-java
	@echo "Running Java client in batch mode..."
	$(JAVA) CalculatorClient --host $(HOST) --port $(PORT) --batch "ADD 5 3" "MUL 7 6" "SQRT 16" "DIV 10 2"

# Testing targets
.PHONY: test-functional test-protocol test-performance test-stress test-errors test-all
test-functional:
	@echo "Running functional tests..."
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT) --functional

test-protocol:
	@echo "Running protocol compliance tests..."
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT) --protocol

test-performance:
	@echo "Running performance tests..."
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT) --performance --perf-requests 200

test-stress:
	@echo "Running stress tests..."
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT) --stress --stress-clients 5 --stress-requests 10

test-errors:
	@echo "Running error handling tests..."
	$(PYTHON) error_handling_demo.py $(PORT) $(HOST)

test-all:
	@echo "Running comprehensive test suite..."
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT)

# Demo targets
.PHONY: demo-basic demo-concurrent demo-errors
demo-basic:
	@echo "Starting basic demonstration..."
	@echo "This demo will:"
	@echo "1. Start the multi-threaded server"
	@echo "2. Run a Python client with sample calculations"
	@echo ""
	@echo "Starting server in background..."
	@$(PYTHON) server_v2.py $(PORT) $(HOST) &
	@SERVER_PID=$$!; \
	echo "Server PID: $$SERVER_PID"; \
	sleep 2; \
	echo "Running client demo..."; \
	$(PYTHON) client_python.py --host $(HOST) --port $(PORT) --batch "ADD 10 5" "SUB 20 8" "MUL 6 7" "DIV 15 3" "POW 2 8" "SQRT 25"; \
	echo "Stopping server..."; \
	kill $$SERVER_PID 2>/dev/null || true

demo-concurrent:
	@echo "Starting concurrent clients demonstration..."
	@echo "This demo shows multiple clients connecting simultaneously"
	@echo ""
	@$(PYTHON) server_v2.py $(PORT) $(HOST) &
	@SERVER_PID=$$!; \
	echo "Server PID: $$SERVER_PID"; \
	sleep 2; \
	echo "Starting 3 concurrent Python clients..."; \
	$(PYTHON) client_python.py --host $(HOST) --port $(PORT) --batch "ADD 1 1" "MUL 2 2" & \
	$(PYTHON) client_python.py --host $(HOST) --port $(PORT) --batch "SUB 5 3" "DIV 8 2" & \
	$(PYTHON) client_python.py --host $(HOST) --port $(PORT) --batch "POW 3 2" "SQRT 16" & \
	wait; \
	echo "All clients completed. Stopping server..."; \
	kill $$SERVER_PID 2>/dev/null || true

demo-errors:
	@echo "Starting error handling demonstration..."
	@$(PYTHON) server_v2.py $(PORT) $(HOST) &
	@SERVER_PID=$$!; \
	echo "Server PID: $$SERVER_PID"; \
	sleep 2; \
	echo "Running error scenarios..."; \
	$(PYTHON) error_handling_demo.py $(PORT) $(HOST); \
	echo "Stopping server..."; \
	kill $$SERVER_PID 2>/dev/null || true

# Utility targets
.PHONY: clean install-deps check-deps lint
clean:
	@echo "Cleaning generated files..."
	@rm -f *.class
	@rm -f *.log
	@rm -f test_results_*.json
	@rm -f error_test_results_*.json
	@rm -f .calc_client_history
	@echo "Clean complete"

install-deps:
	@echo "Installing dependencies..."
	@echo "Note: This project uses only standard libraries"
	@echo "Ensuring Python 3 is available..."
	@$(PYTHON) --version
	@echo "Ensuring Node.js is available..."
	@$(NODE) --version
	@echo "Ensuring Java is available..."
	@$(JAVA) -version
	@$(JAVAC) -version
	@echo "All dependencies are available"

check-deps:
	@echo "Checking dependencies..."
	@echo -n "Python 3: "
	@$(PYTHON) --version 2>/dev/null && echo "✓ Available" || echo "✗ Not found"
	@echo -n "Node.js: "
	@$(NODE) --version 2>/dev/null && echo "✓ Available" || echo "✗ Not found"
	@echo -n "Java: "
	@$(JAVA) -version 2>/dev/null && echo "✓ Available" || echo "✗ Not found"
	@echo -n "Java Compiler: "
	@$(JAVAC) -version 2>/dev/null && echo "✓ Available" || echo "✗ Not found"

# Development targets
.PHONY: lint format
lint:
	@echo "Running code quality checks..."
	@echo "Note: Install pylint, eslint, checkstyle for full linting"
	@echo "Python files:"
	@find . -name "*.py" -exec echo "  {}" \;
	@echo "JavaScript files:"
	@find . -name "*.js" -exec echo "  {}" \;
	@echo "Java files:"
	@find . -name "*.java" -exec echo "  {}" \;

# Documentation targets
.PHONY: docs
docs:
	@echo "Documentation files:"
	@echo "  README.md              - Main documentation"
	@echo "  PROTOCOL_SPECIFICATION.md - Protocol details"
	@echo "  Makefile               - Build system"
	@echo ""
	@echo "Generated documentation:"
	@echo "  *.log files            - Execution logs"
	@echo "  test_results_*.json    - Test results"
	@echo "  error_test_results_*.json - Error test results"

# Advanced testing targets
.PHONY: test-integration test-regression benchmark
test-integration:
	@echo "Running integration tests..."
	@echo "Testing server v1 + Python client:"
	@$(PYTHON) server_v1.py $(PORT) &
	@SERVER_PID=$$!; \
	sleep 2; \
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT) --functional; \
	kill $$SERVER_PID 2>/dev/null || true; \
	echo "Testing server v2 + Java client:"; \
	$(PYTHON) server_v2.py $(PORT) $(HOST) &
	@SERVER_PID=$$!; \
	sleep 2; \
	$(MAKE) client-java-batch; \
	kill $$SERVER_PID 2>/dev/null || true

test-regression:
	@echo "Running regression tests..."
	@echo "Testing both server versions with same test suite..."
	@echo "Server v1 regression test:"
	@$(PYTHON) server_v1.py $(PORT) &
	@SERVER_PID=$$!; \
	sleep 2; \
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT) --functional --protocol; \
	kill $$SERVER_PID 2>/dev/null || true; \
	echo "Server v2 regression test:"; \
	$(PYTHON) server_v2.py $(PORT) $(HOST) &
	@SERVER_PID=$$!; \
	sleep 2; \
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT) --functional --protocol; \
	kill $$SERVER_PID 2>/dev/null || true

benchmark:
	@echo "Running performance benchmarks..."
	@$(PYTHON) server_v2.py $(PORT) $(HOST) &
	@SERVER_PID=$$!; \
	sleep 2; \
	echo "Benchmarking with 1000 requests..."; \
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT) --performance --perf-requests 1000; \
	echo "Stress testing with 10 concurrent clients..."; \
	$(PYTHON) test_scenarios.py --host $(HOST) --port $(PORT) --stress --stress-clients 10 --stress-requests 50; \
	kill $$SERVER_PID 2>/dev/null || true

# Special targets for different environments
.PHONY: dev prod debug
dev: clean build-all
	@echo "Development environment ready"
	@echo "Start developing with: make server-v2 (in one terminal)"
	@echo "Then: make client-python (in another terminal)"

prod: clean build-all test-all
	@echo "Production build complete"
	@echo "All tests passed - ready for deployment"

debug:
	@echo "Debug information:"
	@echo "Working directory: $(PWD)"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Node.js version: $$($(NODE) --version)"
	@echo "Java version: $$($(JAVA) -version 2>&1 | head -1)"
	@echo "Available files:"
	@ls -la *.py *.js *.java *.md 2>/dev/null || echo "Some files missing"

# Platform-specific targets
.PHONY: windows macos linux
windows:
	@echo "Windows-specific setup not implemented"
	@echo "Use WSL or install Python, Node.js, and Java manually"

macos:
	@echo "macOS-specific setup:"
	@echo "Install with Homebrew:"
	@echo "  brew install python node openjdk"

linux:
	@echo "Linux-specific setup:"
	@echo "Install with package manager:"
	@echo "  Ubuntu/Debian: sudo apt install python3 nodejs default-jdk"
	@echo "  CentOS/RHEL: sudo yum install python3 nodejs java-11-openjdk-devel"

# Help for specific components
.PHONY: help-server help-client help-testing
help-server:
	@echo "Server Help"
	@echo "==========="
	@echo ""
	@echo "Single-threaded Server (server_v1.py):"
	@echo "  - Handles one client at a time"
	@echo "  - Good for learning basic concepts"
	@echo "  - Usage: make server-v1"
	@echo ""
	@echo "Multi-threaded Server (server_v2.py):"
	@echo "  - Handles multiple clients concurrently"
	@echo "  - Production-ready implementation"
	@echo "  - Usage: make server-v2"
	@echo ""
	@echo "Configuration:"
	@echo "  - Default port: $(PORT)"
	@echo "  - Default host: $(HOST)"
	@echo "  - Customize: make PORT=9000 server-v2"

help-client:
	@echo "Client Help"
	@echo "==========="
	@echo ""
	@echo "Python Client (client_python.py):"
	@echo "  - Interactive command-line interface"
	@echo "  - Command history and auto-completion"
	@echo "  - Batch mode support"
	@echo "  - Usage: make client-python"
	@echo ""
	@echo "JavaScript Client (client_javascript.js):"
	@echo "  - Node.js implementation"
	@echo "  - Colorized output"
	@echo "  - Event-driven architecture"
	@echo "  - Usage: make client-js"
	@echo ""
	@echo "Java Client (CalculatorClient.java):"
	@echo "  - Object-oriented design"
	@echo "  - Exception handling"
	@echo "  - Batch processing"
	@echo "  - Usage: make client-java"

help-testing:
	@echo "Testing Help"
	@echo "============"
	@echo ""
	@echo "Test Categories:"
	@echo "  functional   - Core mathematical operations"
	@echo "  protocol     - CalcProtocol/1.0 compliance"
	@echo "  performance  - Response time measurement"
	@echo "  stress       - Concurrent client simulation"
	@echo "  errors       - Error handling scenarios"
	@echo ""
	@echo "Usage Examples:"
	@echo "  make test-functional"
	@echo "  make test-all"
	@echo "  make test-performance"
	@echo "  make test-stress"
	@echo ""
	@echo "Custom Testing:"
	@echo "  make PORT=9000 test-all"
	@echo "  python3 test_scenarios.py --help"