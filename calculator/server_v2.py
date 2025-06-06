#!/usr/bin/env python3
"""
Multi-Threaded Calculator Server (Version 2)
===========================================

This is an advanced, multi-threaded implementation of the CalcProtocol/1.0 server.
It can handle multiple clients simultaneously using threading.

Key Improvements over Version 1:
- Concurrent client handling using threads
- Thread-safe operation logging
- Better resource management
- Connection pooling and management
- Enhanced error handling and recovery

Learning Objectives:
- Understand multi-threaded server programming
- Learn thread synchronization and safety
- Practice concurrent programming concepts
- Implement thread pooling and management

Version: 2.0
Protocol: CalcProtocol/1.0
"""

import socket
import sys
import math
import logging
import threading
import time
from typing import Tuple, Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, RLock
import queue
import signal

# Configure thread-safe logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calculator_server_v2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ClientConnection:
    """
    Represents a client connection with metadata
    """
    def __init__(self, socket: socket.socket, address: Tuple[str, int]):
        self.socket = socket
        self.address = address
        self.connected_at = time.time()
        self.last_activity = time.time()
        self.request_count = 0
        self.thread_id = None
    
    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = time.time()
    
    def increment_requests(self):
        """Increment the request counter"""
        self.request_count += 1


class ThreadSafeCounter:
    """
    Thread-safe counter for tracking statistics
    """
    def __init__(self):
        self._value = 0
        self._lock = Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
    
    def decrement(self):
        with self._lock:
            self._value -= 1
            return self._value
    
    @property
    def value(self):
        with self._lock:
            return self._value


class MultiThreadedCalculatorServer:
    """
    Multi-threaded calculator server implementing CalcProtocol/1.0
    
    Features:
    - Handles multiple clients simultaneously
    - Thread pool for efficient resource management
    - Thread-safe logging and statistics
    - Connection timeout management
    - Graceful shutdown handling
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8080, max_workers: int = 10):
        """
        Initialize the multi-threaded calculator server
        
        Args:
            host (str): Server hostname or IP address
            port (int): Server port number
            max_workers (int): Maximum number of worker threads
        """
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.socket = None
        self.running = False
        
        # Thread management
        self.thread_pool = None
        self.active_connections: Dict[str, ClientConnection] = {}
        self.connections_lock = RLock()
        
        # Statistics (thread-safe counters)
        self.total_connections = ThreadSafeCounter()
        self.active_connection_count = ThreadSafeCounter()
        self.total_requests = ThreadSafeCounter()
        
        # Configuration
        self.connection_timeout = 300  # 5 minutes
        self.max_requests_per_client = 1000
        
        # Define supported operations and their requirements
        self.operations = {
            'ADD': {'operands': 2, 'function': self._add},
            'SUB': {'operands': 2, 'function': self._subtract},
            'MUL': {'operands': 2, 'function': self._multiply},
            'DIV': {'operands': 2, 'function': self._divide},
            'POW': {'operands': 2, 'function': self._power},
            'SQRT': {'operands': 1, 'function': self._square_root}
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logging.info(f"Multi-threaded calculator server initialized on {host}:{port}")
        logging.info(f"Maximum worker threads: {max_workers}")
    
    def start(self):
        """
        Start the multi-threaded server
        
        This method:
        1. Creates a TCP socket
        2. Initializes the thread pool
        3. Starts the connection timeout monitor
        4. Begins accepting client connections
        """
        try:
            # Create TCP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind and listen
            self.socket.bind((self.host, self.port))
            self.socket.listen(20)  # Higher backlog for multi-threaded server
            
            # Initialize thread pool
            self.thread_pool = ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix="CalcWorker"
            )
            
            self.running = True
            
            # Start connection timeout monitor in a separate thread
            timeout_thread = threading.Thread(
                target=self._monitor_connections,
                name="ConnectionMonitor",
                daemon=True
            )
            timeout_thread.start()
            
            # Start statistics reporter
            stats_thread = threading.Thread(
                target=self._report_statistics,
                name="StatsReporter",
                daemon=True
            )
            stats_thread.start()
            
            logging.info(f"Multi-threaded server listening on {self.host}:{self.port}")
            print(f"Calculator Server v2.0 (Multi-threaded) started on {self.host}:{self.port}")
            print(f"Max concurrent connections: {self.max_workers}")
            print("Press Ctrl+C to stop the server")
            
            # Main server loop - accept connections
            while self.running:
                try:
                    # Accept incoming connection
                    client_socket, client_address = self.socket.accept()
                    
                    # Create client connection object
                    connection_id = f"{client_address[0]}:{client_address[1]}:{int(time.time())}"
                    client_conn = ClientConnection(client_socket, client_address)
                    
                    # Store connection
                    with self.connections_lock:
                        self.active_connections[connection_id] = client_conn
                    
                    # Update statistics
                    self.total_connections.increment()
                    self.active_connection_count.increment()
                    
                    logging.info(f"New client connected: {client_address} (ID: {connection_id})")
                    print(f"Client connected: {client_address} (Total active: {self.active_connection_count.value})")
                    
                    # Submit client handling to thread pool
                    future = self.thread_pool.submit(
                        self._handle_client_threaded,
                        connection_id,
                        client_conn
                    )
                    
                    # Store thread reference
                    client_conn.thread_id = future
                    
                except Exception as e:
                    if self.running:  # Only log if server is still supposed to be running
                        logging.error(f"Error accepting connection: {e}")
                    
        except Exception as e:
            logging.error(f"Failed to start server: {e}")
            print(f"Error: {e}")
        finally:
            self.stop()
    
    def _handle_client_threaded(self, connection_id: str, client_conn: ClientConnection):
        """
        Handle communication with a single client in a separate thread
        
        Args:
            connection_id (str): Unique connection identifier
            client_conn (ClientConnection): Client connection object
        """
        client_socket = client_conn.socket
        client_address = client_conn.address
        
        try:
            # Send welcome message
            welcome_msg = f"Welcome to Calculator Server v2.0 (CalcProtocol/1.0)\n"
            welcome_msg += f"Multi-threaded server - Thread: {threading.current_thread().name}\n"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # Set socket timeout for this client
            client_socket.settimeout(30.0)  # 30 second timeout per operation
            
            # Process client requests
            while self.running:
                try:
                    # Receive data from client
                    data = client_socket.recv(1024)
                    
                    if not data:
                        # Client disconnected
                        logging.info(f"Client {client_address} disconnected normally")
                        break
                    
                    # Update activity and request count
                    client_conn.update_activity()
                    client_conn.increment_requests()
                    self.total_requests.increment()
                    
                    # Check request limit
                    if client_conn.request_count > self.max_requests_per_client:
                        error_msg = "ERROR Too many requests - connection limit reached\n"
                        client_socket.send(error_msg.encode('utf-8'))
                        logging.warning(f"Client {client_address} exceeded request limit")
                        break
                    
                    # Decode and process request
                    request = data.decode('utf-8').strip()
                    logging.info(f"[{threading.current_thread().name}] Received from {client_address}: {request}")
                    
                    # Process the request
                    response = self._process_request(request)
                    logging.info(f"[{threading.current_thread().name}] Sending to {client_address}: {response}")
                    
                    # Send response
                    client_socket.send((response + '\n').encode('utf-8'))
                    
                except socket.timeout:
                    # Client took too long to send data
                    timeout_msg = "ERROR Connection timeout - closing connection\n"
                    try:
                        client_socket.send(timeout_msg.encode('utf-8'))
                    except:
                        pass  # Client might have already disconnected
                    logging.warning(f"Client {client_address} timed out")
                    break
                    
                except Exception as e:
                    logging.error(f"Error handling client {client_address} in thread {threading.current_thread().name}: {e}")
                    break
                    
        except Exception as e:
            logging.error(f"Error in client handler thread for {client_address}: {e}")
        finally:
            # Cleanup: remove from active connections and close socket
            self._cleanup_client_connection(connection_id, client_conn)
    
    def _cleanup_client_connection(self, connection_id: str, client_conn: ClientConnection):
        """
        Clean up a client connection
        
        Args:
            connection_id (str): Connection identifier
            client_conn (ClientConnection): Client connection object
        """
        try:
            # Remove from active connections
            with self.connections_lock:
                if connection_id in self.active_connections:
                    del self.active_connections[connection_id]
            
            # Close socket
            if client_conn.socket:
                client_conn.socket.close()
            
            # Update statistics
            self.active_connection_count.decrement()
            
            # Calculate session duration
            session_duration = time.time() - client_conn.connected_at
            
            logging.info(f"Client {client_conn.address} disconnected. "
                        f"Session duration: {session_duration:.2f}s, "
                        f"Requests processed: {client_conn.request_count}")
            
            print(f"Client disconnected: {client_conn.address} "
                  f"(Active: {self.active_connection_count.value})")
            
        except Exception as e:
            logging.error(f"Error cleaning up client connection: {e}")
    
    def _monitor_connections(self):
        """
        Monitor connections for timeouts and cleanup stale connections
        This runs in a separate daemon thread
        """
        while self.running:
            try:
                current_time = time.time()
                connections_to_close = []
                
                # Check for timed out connections
                with self.connections_lock:
                    for conn_id, client_conn in self.active_connections.items():
                        if current_time - client_conn.last_activity > self.connection_timeout:
                            connections_to_close.append((conn_id, client_conn))
                
                # Close timed out connections
                for conn_id, client_conn in connections_to_close:
                    logging.warning(f"Closing timed out connection: {client_conn.address}")
                    try:
                        timeout_msg = "ERROR Connection timeout - server closing connection\n"
                        client_conn.socket.send(timeout_msg.encode('utf-8'))
                    except:
                        pass  # Socket might already be closed
                    
                    self._cleanup_client_connection(conn_id, client_conn)
                
                # Sleep before next check
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logging.error(f"Error in connection monitor: {e}")
                time.sleep(30)
    
    def _report_statistics(self):
        """
        Periodically report server statistics
        This runs in a separate daemon thread
        """
        while self.running:
            try:
                time.sleep(60)  # Report every minute
                
                if not self.running:
                    break
                
                with self.connections_lock:
                    active_count = len(self.active_connections)
                
                logging.info(f"SERVER STATS - Active connections: {active_count}, "
                           f"Total connections: {self.total_connections.value}, "
                           f"Total requests: {self.total_requests.value}")
                
            except Exception as e:
                logging.error(f"Error in statistics reporter: {e}")
    
    def _process_request(self, request: str) -> str:
        """
        Process a client request according to CalcProtocol/1.0
        This method is thread-safe
        
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
            
            # Handle error results (strings starting with "ERROR")
            if isinstance(result, str) and result.startswith("ERROR"):
                return result
            
            return f"OK {result}"
            
        except Exception as e:
            thread_name = threading.current_thread().name
            logging.error(f"[{thread_name}] Error processing request '{request}': {e}")
            return f"ERROR Internal server error"
    
    def _parse_request(self, request: str) -> Tuple[Optional[str], any]:
        """
        Parse a request string according to CalcProtocol/1.0 format
        Thread-safe method
        
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
    
    # Mathematical operation implementations (thread-safe)
    
    def _add(self, a: float, b: float) -> Optional[float]:
        """Thread-safe addition operation"""
        try:
            result = a + b
            if abs(result) > 1e308:
                logging.error(f"[{threading.current_thread().name}] Addition overflow: {a} + {b}")
                return "ERROR Result overflow: number too large"
            return result
        except Exception as e:
            logging.error(f"[{threading.current_thread().name}] Addition error: {e}")
            return None
    
    def _subtract(self, a: float, b: float) -> Optional[float]:
        """Thread-safe subtraction operation"""
        try:
            result = a - b
            if abs(result) > 1e308:
                logging.error(f"[{threading.current_thread().name}] Subtraction overflow: {a} - {b}")
                return "ERROR Result overflow: number too large"
            return result
        except Exception as e:
            logging.error(f"[{threading.current_thread().name}] Subtraction error: {e}")
            return None
    
    def _multiply(self, a: float, b: float) -> Optional[float]:
        """Thread-safe multiplication operation"""
        try:
            result = a * b
            if abs(result) > 1e308:
                logging.error(f"[{threading.current_thread().name}] Multiplication overflow: {a} * {b}")
                return "ERROR Result overflow: number too large"
            return result
        except Exception as e:
            logging.error(f"[{threading.current_thread().name}] Multiplication error: {e}")
            return None
    
    def _divide(self, a: float, b: float) -> str:
        """Thread-safe division operation"""
        try:
            if b == 0:
                return "ERROR Division by zero"
            
            result = a / b
            if abs(result) > 1e308:
                return "ERROR Result overflow: number too large"
            
            return result
        except Exception as e:
            logging.error(f"[{threading.current_thread().name}] Division error: {e}")
            return "ERROR Division failed"
    
    def _power(self, a: float, b: float) -> str:
        """Thread-safe exponentiation operation"""
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
            logging.error(f"[{threading.current_thread().name}] Power operation error: {e}")
            return "ERROR Power calculation failed"
    
    def _square_root(self, a: float) -> str:
        """Thread-safe square root operation"""
        try:
            if a < 0:
                return "ERROR Cannot calculate square root of negative number"
            
            result = math.sqrt(a)
            return result
        except Exception as e:
            logging.error(f"[{threading.current_thread().name}] Square root error: {e}")
            return "ERROR Square root calculation failed"
    
    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals gracefully
        """
        print(f"\nReceived signal {signum}, shutting down server...")
        logging.info(f"Received signal {signum}, initiating graceful shutdown")
        self.stop()
    
    def stop(self):
        """
        Stop the server gracefully
        """
        logging.info("Initiating server shutdown...")
        self.running = False
        
        # Close all active client connections
        connections_to_close = []
        with self.connections_lock:
            connections_to_close = list(self.active_connections.items())
        
        for conn_id, client_conn in connections_to_close:
            try:
                shutdown_msg = "SERVER Server shutting down - closing connection\n"
                client_conn.socket.send(shutdown_msg.encode('utf-8'))
                client_conn.socket.close()
            except:
                pass  # Ignore errors during shutdown
        
        # Shutdown thread pool
        if self.thread_pool:
            logging.info("Shutting down thread pool...")
            self.thread_pool.shutdown(wait=True, timeout=10)
        
        # Close server socket
        if self.socket:
            self.socket.close()
        
        # Final statistics
        logging.info(f"Server shutdown complete. Final stats:")
        logging.info(f"Total connections served: {self.total_connections.value}")
        logging.info(f"Total requests processed: {self.total_requests.value}")
        
        print("Multi-threaded server shutdown complete")


def main():
    """
    Main function to run the multi-threaded calculator server
    """
    # Default configuration
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 8080
    DEFAULT_MAX_WORKERS = 10
    
    # Parse command line arguments
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    max_workers = DEFAULT_MAX_WORKERS
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            print(f"Usage: {sys.argv[0]} [port] [host] [max_workers]")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    if len(sys.argv) > 3:
        try:
            max_workers = int(sys.argv[3])
        except ValueError:
            print(f"Invalid max_workers: {sys.argv[3]}")
            sys.exit(1)
    
    # Create and start the server
    server = MultiThreadedCalculatorServer(host, port, max_workers)
    
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