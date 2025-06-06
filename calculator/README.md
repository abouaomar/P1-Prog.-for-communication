# Network Calculator System

A comprehensive client-server calculator system implementing CalcProtocol/1.0 for educational purposes in network programming and distributed systems.

## 📋 Table of Contents

- [Overview](#overview)
- [Protocol Specification](#protocol-specification)
- [Components](#components)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Testing](#testing)
- [Learning Objectives](#learning-objectives)
- [Architecture](#architecture)
- [Error Handling](#error-handling)
- [Performance](#performance)
- [Contributing](#contributing)

## 🎯 Overview

This project implements a complete network calculator system that demonstrates fundamental concepts in:

- **Client-Server Architecture**: TCP-based communication
- **Protocol Design**: Custom CalcProtocol/1.0 specification
- **Multi-threading**: Concurrent client handling
- **Error Handling**: Comprehensive error management
- **Testing**: Automated testing frameworks
- **Multi-language Support**: Python, JavaScript, and Java clients

### Key Features

- ✅ **Mathematical Operations**: ADD, SUB, MUL, DIV, POW, SQRT
- ✅ **Single & Multi-threaded Servers**: Progressive complexity
- ✅ **Multi-language Clients**: Python, JavaScript (Node.js), Java
- ✅ **Comprehensive Error Handling**: Protocol, mathematical, and network errors
- ✅ **Performance Testing**: Stress testing and benchmarking
- ✅ **Educational Documentation**: Extensive comments and explanations

## 📖 Protocol Specification

CalcProtocol/1.0 is a simple text-based protocol for mathematical operations:

### Request Format
```
OPERATION operand1 [operand2]
```

### Response Format
```
STATUS [result_or_error_message]
```

### Status Codes
- `OK`: Operation successful
- `ERROR`: Mathematical error (e.g., division by zero)
- `INVALID`: Protocol or syntax error

### Example Communication
```
Client: ADD 5 3
Server: OK 8

Client: DIV 10 0
Server: ERROR Division by zero

Client: SQRT 16
Server: OK 4
```

For complete protocol details, see [PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md).

## 🏗️ Components

### Servers

#### Single-threaded Server (v1.0)
- **File**: `server_v1.py`
- **Purpose**: Basic TCP server handling one client at a time
- **Features**: Core protocol implementation, basic error handling
- **Use Case**: Learning fundamental socket programming

#### Multi-threaded Server (v2.0)
- **File**: `server_v2.py`
- **Purpose**: Advanced server with concurrent client support
- **Features**: Thread pooling, connection management, advanced statistics
- **Use Case**: Production-ready concurrent server implementation

### Clients

#### Python Client
- **File**: `client_python.py`
- **Features**: Interactive CLI, command history, auto-reconnection
- **Requirements**: Python 3.6+
- **Modes**: Interactive and batch processing

#### JavaScript Client (Node.js)
- **File**: `client_javascript.js`
- **Features**: Colorized output, auto-completion, event-driven architecture
- **Requirements**: Node.js 12.0+
- **Modes**: Interactive only

#### Java Client
- **File**: `CalculatorClient.java`
- **Features**: Object-oriented design, exception handling, batch processing
- **Requirements**: Java 8+
- **Modes**: Interactive and batch processing

### Testing & Analysis

#### Error Handling Demo
- **File**: `error_handling_demo.py`
- **Purpose**: Comprehensive error scenario testing
- **Features**: Protocol compliance, mathematical errors, edge cases

#### Test Scenarios
- **File**: `test_scenarios.py`
- **Purpose**: Automated testing framework
- **Features**: Functional, performance, stress, and integration testing

## 🚀 Quick Start

### 1. Start a Server

**Single-threaded server:**
```bash
python3 server_v1.py [port]
```

**Multi-threaded server:**
```bash
python3 server_v2.py [port] [host] [max_workers]
```

**Example:**
```bash
python3 server_v2.py 8080 localhost 10
```

### 2. Connect with a Client

**Python client:**
```bash
python3 client_python.py --host localhost --port 8080
```

**JavaScript client:**
```bash
node client_javascript.js --host localhost --port 8080
```

**Java client:**
```bash
javac CalculatorClient.java
java CalculatorClient --host localhost --port 8080
```

### 3. Perform Calculations

Once connected, you can perform calculations:
```
calc> ADD 5 3
✓ Result: 8

calc> DIV 15 3
✓ Result: 5

calc> SQRT 16
✓ Result: 4
```

## 📚 Detailed Usage

### Server Configuration

#### Single-threaded Server
```bash
# Default (localhost:8080)
python3 server_v1.py

# Custom port
python3 server_v1.py 9000

# Custom host and port (edit source code)
python3 server_v1.py 9000
```

#### Multi-threaded Server
```bash
# Default configuration
python3 server_v2.py

# Custom port
python3 server_v2.py 9000

# Custom host
python3 server_v2.py 9000 192.168.1.100

# Custom worker threads
python3 server_v2.py 9000 localhost 20
```

### Client Usage

#### Python Client Options
```bash
python3 client_python.py --help

# Interactive mode
python3 client_python.py --host localhost --port 8080

# Batch mode
python3 client_python.py --batch "ADD 5 3" "MUL 7 6" "SQRT 16"
```

#### JavaScript Client Options
```bash
node client_javascript.js --help

# Interactive mode with custom server
node client_javascript.js --host 192.168.1.100 --port 9000
```

#### Java Client Options
```bash
java CalculatorClient --help

# Interactive mode
java CalculatorClient --host localhost --port 8080

# Batch mode
java CalculatorClient --batch "ADD 5 3" "MUL 7 6"
```

### Supported Operations

| Operation | Syntax | Description | Example |
|-----------|--------|-------------|---------|
| ADD | `ADD num1 num2` | Addition | `ADD 5 3` → `OK 8` |
| SUB | `SUB num1 num2` | Subtraction | `SUB 10 4` → `OK 6` |
| MUL | `MUL num1 num2` | Multiplication | `MUL 7 6` → `OK 42` |
| DIV | `DIV num1 num2` | Division | `DIV 15 3` → `OK 5` |
| POW | `POW base exp` | Exponentiation | `POW 2 8` → `OK 256` |
| SQRT | `SQRT number` | Square root | `SQRT 16` → `OK 4` |

## 🧪 Testing

### Running Tests

#### Error Handling Tests
```bash
# Test error scenarios
python3 error_handling_demo.py [port] [host]

# Example
python3 error_handling_demo.py 8080 localhost
```

#### Comprehensive Testing
```bash
# Run all tests
python3 test_scenarios.py --host localhost --port 8080

# Run specific test categories
python3 test_scenarios.py --functional
python3 test_scenarios.py --protocol
python3 test_scenarios.py --performance --perf-requests 500
python3 test_scenarios.py --stress --stress-clients 10 --stress-requests 50
```

### Test Categories

1. **Functional Tests**: Core mathematical operations
2. **Protocol Compliance**: CalcProtocol/1.0 adherence
3. **Performance Tests**: Response time measurement
4. **Stress Tests**: Concurrent client simulation
5. **Edge Case Tests**: Boundary conditions and special cases

## 🎓 Learning Objectives

This project is designed to teach:

### Network Programming Concepts
- TCP socket programming (client and server)
- Protocol design and implementation
- Connection management and lifecycle
- Error handling in distributed systems

### Software Engineering Practices
- Multi-threaded programming and synchronization
- Error handling and recovery strategies
- Testing methodologies (unit, integration, stress)
- Documentation and code organization

### Programming Language Skills
- **Python**: Socket programming, threading, object-oriented design
- **JavaScript/Node.js**: Event-driven programming, asynchronous I/O
- **Java**: Object-oriented design, exception handling, concurrency

### System Design
- Client-server architecture patterns
- Protocol specification and compliance
- Performance analysis and optimization
- Scalability considerations

## 🏛️ Architecture

### System Overview
```
┌─────────────────┐    CalcProtocol/1.0    ┌─────────────────┐
│   Client Apps   │ ◄─────────────────────► │     Server      │
│                 │                         │                 │
│ • Python CLI    │    TCP/IP Connection    │ • Single Thread │
│ • JavaScript    │                         │ • Multi Thread  │
│ • Java GUI/CLI  │                         │ • Thread Pool   │
└─────────────────┘                         └─────────────────┘
```

### Server Architecture

#### Single-threaded (v1.0)
```python
while server.running:
    client_socket, address = server_socket.accept()
    handle_client(client_socket)  # Blocking - one client at a time
```

#### Multi-threaded (v2.0)
```python
thread_pool = ThreadPoolExecutor(max_workers=10)
while server.running:
    client_socket, address = server_socket.accept()
    thread_pool.submit(handle_client, client_socket)  # Non-blocking
```

### Protocol Stack
```
┌─────────────────────┐
│   Application       │  Calculator Logic
├─────────────────────┤
│   CalcProtocol/1.0  │  Custom Protocol
├─────────────────────┤
│   TCP               │  Reliable Transport
├─────────────────────┤
│   IP                │  Network Layer
└─────────────────────┘
```

## ⚠️ Error Handling

The system implements comprehensive error handling:

### Error Categories

1. **Protocol Errors (INVALID)**
   - Unknown operations
   - Invalid operand count
   - Malformed requests
   - Non-numeric operands

2. **Mathematical Errors (ERROR)**
   - Division by zero
   - Square root of negative numbers
   - Arithmetic overflow

3. **Network Errors**
   - Connection timeouts
   - Connection lost
   - Server unavailable

### Error Handling Strategies

- **Server-side**: Input validation, exception handling, graceful degradation
- **Client-side**: Retry logic, automatic reconnection, user feedback
- **Protocol-level**: Standardized error codes and messages

## 📊 Performance

### Benchmarks

Typical performance characteristics (tested on localhost):

| Metric | Single-threaded | Multi-threaded |
|--------|----------------|----------------|
| Avg Response Time | ~2ms | ~3ms |
| Max Concurrent Clients | 1 | 10+ |
| Requests/Second | ~500 | ~2000+ |
| Memory Usage | ~10MB | ~15MB |

### Optimization Tips

1. **Server Performance**:
   - Use connection pooling
   - Implement request caching
   - Optimize mathematical operations

2. **Network Performance**:
   - Enable TCP_NODELAY for low latency
   - Use persistent connections
   - Implement request batching

3. **Client Performance**:
   - Implement connection reuse
   - Use asynchronous operations
   - Cache validation results

## 🤝 Contributing

This is an educational project. Students are encouraged to:

1. **Extend the Protocol**: Add new mathematical operations
2. **Improve Performance**: Optimize server or client implementations
3. **Add Features**: Implement new client languages or interfaces
4. **Enhance Testing**: Add more comprehensive test scenarios
5. **Documentation**: Improve explanations and examples

### Development Setup

1. Clone the repository
2. Ensure you have Python 3.6+, Node.js 12+, and Java 8+
3. Run the test suite to verify everything works
4. Make your changes
5. Add tests for new functionality
6. Update documentation

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use modern ES6+ features
- **Java**: Follow standard Java conventions
- **Documentation**: Include comprehensive comments and docstrings