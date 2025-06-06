#!/usr/bin/env python3
"""
Single-Threaded Calculator Server (v1.0)
=============================================

This is a simple, single-threaded implementation of the CalcProtocol/1.0 server.
It handles one client at a time and demonstrates basic socket programming concepts.

Learning Objectives:
- Understand TCP server socket programming
- Learn request parsing and response formatting
- Practice error handling in network applications
- Implement a custom protocol

Version: 1.0
Protocol: CalcProtocol/1.0
"""

import socket
import sys
import math
import logging
from typing import Tuple, Optional

# Configure logging for educational purposes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calculator_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class CalculatorServer:
    """
    Single-threaded calculator server implementing CalcProtocol/1.0
    
    This server:
    1. Accepts one client connection at a time
    2. Processes mathematical operations
    3. Returns results according to the protocol specification
    4. Handles errors gracefully
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        """
        Initialize the calculator server
        
        Args:
            host (str): Server hostname or IP address
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
        # Define supported operations and their requirements
        self.operations = {
            'ADD': {'operands': 2, 'function': self._add},
            'SUB': {'operands': 2, 'function': self._subtract},
            'MUL': {'operands': 2, 'function': self._multiply},
            'DIV': {'operands': 2, 'function': self._divide},
            'POW': {'operands': 2, 'function': self._power},
            'SQRT': {'operands': 1, 'function': self._square_root}
        }
        
        logging.info(f"Calculator server initialized on {host}:{port}")
    
    def start(self):
        """
        Start the server and begin accepting client connections
        
        This method:
        1. Creates a TCP socket
        2. Binds to the specified address
        3. Listens for incoming connections
        4. Handles clients one at a time
        """
        try:
            # Create TCP socket
            # AF_INET = IPv4, SOCK_STREAM = TCP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Allow reuse of address (helpful during development)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind socket to address
            self.socket.bind((self.host, self.port))
            
            # Listen for incoming connections (backlog of 5)
            self.socket.listen(5)
            
            self.running = True
            logging.info(f"Server listening on {self.host}:{self.port}")
            print(f"Calculator Server v1.0 started on {self.host}:{self.port}")
            print("Press Ctrl+C to stop the server")
            
            # Main server loop
            while self.running:
                try:
                    # Accept incoming connection (blocking call)
                    client_socket, client_address = self.socket.accept()
                    logging.info(f"Client connected from {client_address}")
                    print(f"Client connected: {client_address}")
                    
                    # Handle the client
                    self._handle_client(client_socket, client_address)
                    
                except KeyboardInterrupt:
                    print("\nShutting down server...")
                    break
                except Exception as e:
                    logging.error(f"Error accepting connection: {e}")
                    
        except Exception as e:
            logging.error(f"Failed to start server: {e}")
            print(f"Error: {e}")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        """
        Handle communication with a single client
        
        Args:
            client_socket: Socket connected to the client
            client_address: Client's address (IP, port)
        """
        try:
            # Send welcome message
            welcome_msg = "Welcome to Calculator Server v1.0 (CalcProtocol/1.0)\n"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # Process client requests until disconnection
            while True:
                # Receive data from client (max 1024 bytes)
                data = client_socket.recv(1024)
                
                if not data:
                    # Client disconnected
                    logging.info(f"Client {client_address} disconnected")
                    print(f"Client disconnected: {client_address}")
                    break
                
                # Decode the received data
                request = data.decode('utf-8').strip()
                logging.info(f"Received from {client_address}: {request}")
                
                # Process the request and generate response
                response = self._process_request(request)
                logging.info(f"Sending to {client_address}: {response}")
                
                # Send response back to client
                client_socket.send((response + '\n').encode('utf-8'))
                
        except Exception as e:
            logging.error(f"Error handling client {client_address}: {e}")
        finally:
            # Always close the client socket
            client_socket.close()
    
    def _process_request(self, request: str) -> str:
        """
        Process a client request according to CalcProtocol/1.0
        
        Args:
            request (str): Raw request string from client
            
        Returns:
            str: Formatted response according to protocol
        """
        try:
            # Parse the request
            operation, operands = self._parse_request(request)
            
            if operation is None:
                return operands  # operands contains error message in this case
            
            # Validate operation
            if operation not in self.operations:
                return f"INVALID Unknown operation: {operation}"
            
            # Check operand count
            expected_operands = self.operations[operation]['operands']
            if len(operands) != expected_operands:
                return f"INVALID {operation} requires {expected_operands} operand(s), got {len(operands)}"
            
            # Perform the calculation
            result = self.operations[operation]['function'](*operands)
            
            if result is None:
                return "ERROR Calculation failed"
            
            return f"OK {result}"
            
        except Exception as e:
            logging.error(f"Error processing request '{request}': {e}")
            return f"ERROR Internal server error"
    
    def _parse_request(self, request: str) -> Tuple[Optional[str], any]:
        """
        Parse a request string according to CalcProtocol/1.0 format
        
        Args:
            request (str): Raw request string
            
        Returns:
            Tuple[Optional[str], any]: (operation, operands) or (None, error_message)
        """
        if not request.strip():
            return None, "INVALID Empty request"
        
        # Split request into components
        parts = request.strip().split()
        
        if len(parts) < 1:
            return None, "INVALID Malformed request"
        
        operation = parts[0].upper()
        
        if len(parts) < 2:
            return None, "INVALID Missing operands"
        
        # Parse operands
        operands = []
        for i, operand_str in enumerate(parts[1:], 1):
            try:
                # Try to convert to float first, then to int if it's a whole number
                operand = float(operand_str)
                if operand.is_integer():
                    operand = int(operand)
                operands.append(operand)
            except ValueError:
                return None, f"INVALID Invalid operand: '{operand_str}' is not a number"
        
        return operation, operands
    
    # Mathematical operation implementations
    
    def _add(self, a: float, b: float) -> Optional[float]:
        """
        Perform addition operation
        
        Args:
            a, b (float): Operands
            
        Returns:
            Optional[float]: Result or None if error
        """
        try:
            result = a + b
            # Check for overflow
            if abs(result) > 1e308:  # Approximate float overflow threshold
                logging.error(f"Addition overflow: {a} + {b}")
                return None
            return result
        except Exception as e:
            logging.error(f"Addition error: {e}")
            return None
    
    def _subtract(self, a: float, b: float) -> Optional[float]:
        """
        Perform subtraction operation
        
        Args:
            a, b (float): Operands
            
        Returns:
            Optional[float]: Result or None if error
        """
        try:
            result = a - b
            if abs(result) > 1e308:
                logging.error(f"Subtraction overflow: {a} - {b}")
                return None
            return result
        except Exception as e:
            logging.error(f"Subtraction error: {e}")
            return None
    
    def _multiply(self, a: float, b: float) -> Optional[float]:
        """
        Perform multiplication operation
        
        Args:
            a, b (float): Operands
            
        Returns:
            Optional[float]: Result or None if error
        """
        try:
            result = a * b
            if abs(result) > 1e308:
                logging.error(f"Multiplication overflow: {a} * {b}")
                return None
            return result
        except Exception as e:
            logging.error(f"Multiplication error: {e}")
            return None
    
    def _divide(self, a: float, b: float) -> Optional[str]:
        """
        Perform division operation
        
        Args:
            a, b (float): Operands
            
        Returns:
            Optional[str]: Result or error message
        """
        try:
            if b == 0:
                return "ERROR Division by zero"
            
            result = a / b
            if abs(result) > 1e308:
                return "ERROR Result overflow: number too large"
            
            return result
        except Exception as e:
            logging.error(f"Division error: {e}")
            return "ERROR Division failed"
    
    def _power(self, a: float, b: float) -> Optional[str]:
        """
        Perform exponentiation operation
        
        Args:
            a, b (float): Base and exponent
            
        Returns:
            Optional[str]: Result or error message
        """
        try:
            # Check for potential overflow conditions
            if abs(a) > 1000 and abs(b) > 10:
                return "ERROR Result overflow: number too large"
            
            result = a ** b
            
            if abs(result) > 1e308:
                return "ERROR Result overflow: number too large"
            
            if math.isnan(result) or math.isinf(result):
                return "ERROR Invalid result: not a finite number"
            
            return result
        except Exception as e:
            logging.error(f"Power operation error: {e}")
            return "ERROR Power calculation failed"
    
    def _square_root(self, a: float) -> Optional[str]:
        """
        Perform square root operation
        
        Args:
            a (float): Operand
            
        Returns:
            Optional[str]: Result or error message
        """
        try:
            if a < 0:
                return "ERROR Cannot calculate square root of negative number"
            
            result = math.sqrt(a)
            return result
        except Exception as e:
            logging.error(f"Square root error: {e}")
            return "ERROR Square root calculation failed"
    
    def stop(self):
        """
        Stop the server gracefully
        """
        self.running = False
        if self.socket:
            self.socket.close()
        logging.info("Server stopped")


def main():
    """
    Main function to run the calculator server
    """
    # Default configuration
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 8080
    
    # Parse command line arguments (simple implementation)
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            print(f"Usage: {sys.argv[0]} [port]")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    # Create and start the server
    server = CalculatorServer(host, port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
    except Exception as e:
        print(f"Server error: {e}")
        logging.error(f"Server error: {e}")
    finally:
        print("Server shutdown complete")


if __name__ == "__main__":
    main()