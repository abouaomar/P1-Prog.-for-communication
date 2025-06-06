# CalcProtocol/1.0 Specification

## Overview
CalcProtocol/1.0 is a simple text-based protocol designed for client-server mathematical operations over TCP/IP networks. This protocol enables clients to send mathematical operations to a server and receive calculated results.

## Protocol Design Principles

### 1. Simplicity
- Human-readable text format
- Simple request-response pattern
- Minimal parsing complexity

### 2. Extensibility
- Easy to add new operations
- Structured error reporting
- Version identification

### 3. Reliability
- Clear status codes
- Comprehensive error messages
- Input validation

## Message Format

### Request Format
```
OPERATION operand1 [operand2]
```

**Components:**
- `OPERATION`: Mathematical operation to perform (case-sensitive)
- `operand1`: First numeric operand (required)
- `operand2`: Second numeric operand (optional, depends on operation)

**Rules:**
- Components separated by single space
- Operands can be integers or floating-point numbers
- No trailing spaces or additional characters

### Response Format
```
STATUS [result_or_error_message]
```

**Components:**
- `STATUS`: Operation result status (OK, ERROR, INVALID)
- `result_or_error_message`: Numeric result or descriptive error message

## Supported Operations

### Binary Operations (require two operands)

#### ADD - Addition
```
Request:  ADD 5 3
Response: OK 8
```

#### SUB - Subtraction
```
Request:  SUB 10 4
Response: OK 6
```

#### MUL - Multiplication
```
Request:  MUL 7 6
Response: OK 42
```

#### DIV - Division
```
Request:  DIV 15 3
Response: OK 5

Request:  DIV 10 0
Response: ERROR Division by zero
```

#### POW - Exponentiation
```
Request:  POW 2 8
Response: OK 256
```

### Unary Operations (require one operand)

#### SQRT - Square Root
```
Request:  SQRT 16
Response: OK 4

Request:  SQRT -4
Response: ERROR Cannot calculate square root of negative number
```

## Status Codes

### OK
- **Meaning**: Operation completed successfully
- **Format**: `OK result`
- **Example**: `OK 42`

### ERROR
- **Meaning**: Mathematical error occurred (e.g., division by zero)
- **Format**: `ERROR error_description`
- **Example**: `ERROR Division by zero`

### INVALID
- **Meaning**: Protocol or syntax error
- **Format**: `INVALID error_description`
- **Example**: `INVALID Unknown operation: MULTIPLY`

## Error Handling

### Protocol Errors (INVALID status)
1. **Unknown Operation**
   ```
   Request:  MULTIPLY 5 3
   Response: INVALID Unknown operation: MULTIPLY
   ```

2. **Insufficient Operands**
   ```
   Request:  ADD 5
   Response: INVALID ADD requires 2 operands, got 1
   ```

3. **Too Many Operands**
   ```
   Request:  SQRT 16 4
   Response: INVALID SQRT requires 1 operand, got 2
   ```

4. **Invalid Operand Format**
   ```
   Request:  ADD five 3
   Response: INVALID Invalid operand: 'five' is not a number
   ```

5. **Malformed Request**
   ```
   Request:  ADD
   Response: INVALID Malformed request: missing operands
   ```

### Mathematical Errors (ERROR status)
1. **Division by Zero**
   ```
   Request:  DIV 10 0
   Response: ERROR Division by zero
   ```

2. **Square Root of Negative Number**
   ```
   Request:  SQRT -25
   Response: ERROR Cannot calculate square root of negative number
   ```

3. **Overflow/Underflow**
   ```
   Request:  POW 999 999
   Response: ERROR Result overflow: number too large
   ```

## Connection Management

### Session Lifecycle
1. **Connection**: Client establishes TCP connection to server
2. **Communication**: Client sends requests, server responds
3. **Termination**: Either party can close connection

### Keep-Alive
- Connection remains open for multiple operations
- No explicit session management required
- Server should handle client disconnections gracefully

### Timeouts
- Server may implement connection timeouts for idle clients
- Recommended timeout: 300 seconds (5 minutes)

## Implementation Guidelines

### For Server Developers
1. **Input Validation**: Always validate request format and operands
2. **Error Handling**: Provide clear, specific error messages
3. **Resource Management**: Handle memory and connection resources properly
4. **Thread Safety**: Ensure thread-safe operations for multi-client scenarios

### For Client Developers
1. **Request Formatting**: Follow exact protocol format
2. **Response Parsing**: Handle all possible status codes
3. **Error Recovery**: Implement retry logic for network errors
4. **User Interface**: Provide clear feedback to users

## Example Communication Session

```
Client connects to server on port 8080

Client: ADD 15 25
Server: OK 40

Client: DIV 100 4
Server: OK 25

Client: SQRT 81
Server: OK 9

Client: DIV 5 0
Server: ERROR Division by zero

Client: UNKNOWN 1 2
Server: INVALID Unknown operation: UNKNOWN

Client disconnects
```

## Protocol Extensions (Future Versions)

Potential future enhancements:
- Scientific operations (SIN, COS, TAN, LOG)
- Multi-operand operations (SUM 1 2 3 4 5)
- Variable storage (SET x 5, GET x)
- Mathematical constants (PI, E)
- Complex number support

## Security Considerations

1. **Input Validation**: Always validate all inputs
2. **Resource Limits**: Implement limits on operand size and computation time
3. **Denial of Service**: Protect against malicious requests
4. **Error Information**: Don't expose internal system information in errors
