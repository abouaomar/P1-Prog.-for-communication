#!/usr/bin/env python3
"""
Python Interactive Calculator Client
===================================

This is an interactive calculator client that connects to the CalcProtocol/1.0 server.
It provides a user-friendly interface for performing mathematical operations remotely.
- Interactive command-line interface
- Connection management and retry logic
- Input validation and error handling
- Command history and help system
- Graceful error recovery

Learning Objectives:
- Understand TCP client socket programming
- Learn interactive application design
- Practice user input validation
- Implement error handling and recovery
- Experience client-server communication patterns

Version: 1.0
Protocol: CalcProtocol/1.0
"""

import socket
import sys
import re
import readline  # For command history and editing
import time
from typing import Optional, Tuple, List
import signal

class CalculatorClient:
    """
    Interactive calculator client for CalcProtocol/1.0
    
    This client provides:
    - Interactive command-line interface
    - Automatic connection management
    - Input validation and help
    - Error handling and recovery
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        """
        Initialize the calculator client
        
        Args:
            host (str): Server hostname or IP address
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = True
        
        # Command history for readline
        self.history_file = '.calc_client_history'
        self._setup_history()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Define supported operations for help and validation
        self.operations = {
            'ADD': {
                'description': 'Addition: ADD num1 num2',
                'example': 'ADD 5 3',
                'operands': 2
            },
            'SUB': {
                'description': 'Subtraction: SUB num1 num2',
                'example': 'SUB 10 4',
                'operands': 2
            },
            'MUL': {
                'description': 'Multiplication: MUL num1 num2',
                'example': 'MUL 7 6',
                'operands': 2
            },
            'DIV': {
                'description': 'Division: DIV num1 num2',
                'example': 'DIV 15 3',
                'operands': 2
            },
            'POW': {
                'description': 'Exponentiation: POW base exponent',
                'example': 'POW 2 8',
                'operands': 2
            },
            'SQRT': {
                'description': 'Square root: SQRT number',
                'example': 'SQRT 16',
                'operands': 1
            }
        }
        
        print("Python Calculator Client v1.0")
        print("=============================")
    
    def _setup_history(self):
        """Setup command history for readline"""
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass  # History file doesn't exist yet
        
        # Set history length
        readline.set_history_length(100)
    
    def _save_history(self):
        """Save command history"""
        try:
            readline.write_history_file(self.history_file)
        except:
            pass  # Ignore errors when saving history
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\nDisconnecting from server...")
        self.running = False
        self.disconnect()
        self._save_history()
        sys.exit(0)
    
    def connect(self) -> bool:
        """
        Connect to the calculator server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print(f"Connecting to {self.host}:{self.port}...")
            
            # Create TCP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set connection timeout
            self.socket.settimeout(10.0)
            
            # Connect to server
            self.socket.connect((self.host, self.port))
            
            # Set socket timeout for operations
            self.socket.settimeout(30.0)
            
            self.connected = True
            print(f"✓ Connected to {self.host}:{self.port}")
            
            # Receive welcome message
            welcome = self._receive_response()
            if welcome:
                print(f"Server: {welcome.strip()}")
            
            return True
            
        except socket.timeout:
            print(f"✗ Connection timeout - server at {self.host}:{self.port} not responding")
            return False
        except ConnectionRefusedError:
            print(f"✗ Connection refused - server at {self.host}:{self.port} not available")
            return False
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False
        print("Disconnected from server")
    
    def _send_request(self, request: str) -> bool:
        """
        Send a request to the server
        
        Args:
            request (str): Request to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            if not self.connected or not self.socket:
                print("✗ Not connected to server")
                return False
            
            # Send request
            self.socket.send((request + '\n').encode('utf-8'))
            return True
            
        except socket.timeout:
            print("✗ Request timeout - server not responding")
            return False
        except ConnectionResetError:
            print("✗ Connection lost - server disconnected")
            self.connected = False
            return False
        except Exception as e:
            print(f"✗ Error sending request: {e}")
            return False
    
    def _receive_response(self) -> Optional[str]:
        """
        Receive a response from the server
        
        Returns:
            Optional[str]: Response string or None if error
        """
        try:
            if not self.connected or not self.socket:
                return None
            
            # Receive response
            data = self.socket.recv(1024)
            
            if not data:
                print("✗ Server closed connection")
                self.connected = False
                return None
            
            response = data.decode('utf-8').strip()
            return response
            
        except socket.timeout:
            print("✗ Response timeout - server not responding")
            return None
        except ConnectionResetError:
            print("✗ Connection lost - server disconnected")
            self.connected = False
            return None
        except Exception as e:
            print(f"✗ Error receiving response: {e}")
            return None
    
    def _validate_input(self, user_input: str) -> Tuple[bool, str]:
        """
        Validate user input before sending to server
        
        Args:
            user_input (str): User input string
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not user_input.strip():
            return False, "Empty input"
        
        parts = user_input.strip().split()
        
        if len(parts) < 1:
            return False, "Invalid input format"
        
        operation = parts[0].upper()
        
        # Check if operation is supported
        if operation not in self.operations:
            return False, f"Unknown operation: {operation}. Type 'help' for available operations."
        
        # Check operand count
        expected_operands = self.operations[operation]['operands']
        provided_operands = len(parts) - 1
        
        if provided_operands != expected_operands:
            return False, f"{operation} requires {expected_operands} operand(s), got {provided_operands}"
        
        # Validate operands are numbers
        for i, operand_str in enumerate(parts[1:], 1):
            try:
                float(operand_str)
            except ValueError:
                return False, f"Invalid operand #{i}: '{operand_str}' is not a number"
        
        return True, ""
    
    def _format_response(self, response: str) -> str:
        """
        Format server response for display
        
        Args:
            response (str): Raw server response
            
        Returns:
            str: Formatted response
        """
        if response.startswith('OK '):
            result = response[3:]
            return f"✓ Result: {result}"
        elif response.startswith('ERROR '):
            error = response[6:]
            return f"✗ Error: {error}"
        elif response.startswith('INVALID '):
            error = response[8:]
            return f"✗ Invalid: {error}"
        else:
            return f"Server: {response}"
    
    def show_help(self):
        """Display help information"""
        print("\nCalculator Client Help")
        print("=====================")
        print("\nAvailable Operations:")
        print("-" * 50)
        
        for op, info in self.operations.items():
            print(f"{info['description']}")
            print(f"  Example: {info['example']}")
            print()
        
        print("Special Commands:")
        print("-" * 50)
        print("help       - Show this help message")
        print("quit, exit - Disconnect and exit")
        print("reconnect  - Reconnect to server")
        print("status     - Show connection status")
        print("\nNotes:")
        print("- Operations are case-insensitive")
        print("- Numbers can be integers or decimals")
        print("- Use Ctrl+C to exit at any time")
        print()
    
    def show_status(self):
        """Show connection status"""
        print(f"\nConnection Status:")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Connected: {'Yes' if self.connected else 'No'}")
        if self.connected:
            print("✓ Ready to send calculations")
        else:
            print("✗ Not connected - use 'reconnect' to connect")
        print()
    
    def run_interactive(self):
        """
        Run the interactive calculator client
        
        Main loop that:
        1. Connects to server
        2. Accepts user input
        3. Validates and sends requests
        4. Displays responses
        5. Handles special commands
        """
        try:
            # Initial connection
            if not self.connect():
                retry = input("Connection failed. Retry? (y/n): ").lower().strip()
                if retry != 'y':
                    return
                if not self.connect():
                    print("Unable to connect. Exiting.")
                    return
            
            print("\nType 'help' for available operations, 'quit' to exit")
            print("Calculator ready! Enter calculations:")
            
            # Main interaction loop
            while self.running:
                try:
                    # Get user input with prompt
                    user_input = input("\ncalc> ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() in ['quit', 'exit']:
                        break
                    elif user_input.lower() == 'help':
                        self.show_help()
                        continue
                    elif user_input.lower() == 'status':
                        self.show_status()
                        continue
                    elif user_input.lower() == 'reconnect':
                        self.disconnect()
                        if self.connect():
                            print("Reconnected successfully")
                        else:
                            print("Reconnection failed")
                        continue
                    
                    # Check if connected
                    if not self.connected:
                        print("✗ Not connected to server. Use 'reconnect' to connect.")
                        continue
                    
                    # Validate input
                    is_valid, error_msg = self._validate_input(user_input)
                    if not is_valid:
                        print(f"✗ {error_msg}")
                        continue
                    
                    # Send request to server
                    if not self._send_request(user_input):
                        # Connection error - try to reconnect
                        print("Attempting to reconnect...")
                        if self.connect():
                            print("Reconnected! Retrying request...")
                            if self._send_request(user_input):
                                response = self._receive_response()
                                if response:
                                    print(self._format_response(response))
                        continue
                    
                    # Receive and display response
                    response = self._receive_response()
                    if response:
                        print(self._format_response(response))
                    else:
                        print("✗ No response received from server")
                
                except KeyboardInterrupt:
                    # Ctrl+C pressed
                    break
                except EOFError:
                    # Ctrl+D pressed
                    break
                except Exception as e:
                    print(f"✗ Unexpected error: {e}")
                    continue
            
        finally:
            # Cleanup
            self.disconnect()
            self._save_history()
            print("\nGoodbye!")
    
    def run_batch(self, commands: List[str]):
        """
        Run calculator in batch mode with a list of commands
        
        Args:
            commands (List[str]): List of commands to execute
        """
        print("Running in batch mode...")
        
        if not self.connect():
            print("Failed to connect for batch processing")
            return
        
        for i, command in enumerate(commands, 1):
            print(f"\n[{i}] {command}")
            
            # Validate command
            is_valid, error_msg = self._validate_input(command)
            if not is_valid:
                print(f"✗ {error_msg}")
                continue
            
            # Send and receive
            if self._send_request(command):
                response = self._receive_response()
                if response:
                    print(f"    {self._format_response(response)}")
                else:
                    print("    ✗ No response received")
            else:
                print("    ✗ Failed to send request")
        
        self.disconnect()
        print("\nBatch processing complete")


def main():
    """
    Main function to run the calculator client
    """
    # Default configuration
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 8080
    
    # Parse command line arguments
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    batch_mode = False
    batch_commands = []
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ['-h', '--help']:
            print("Python Calculator Client")
            print("Usage:")
            print(f"  {sys.argv[0]} [options]")
            print("\nOptions:")
            print("  -h, --help              Show this help")
            print("  --host HOST            Server hostname (default: localhost)")
            print("  --port PORT            Server port (default: 8080)")
            print("  --batch 'CMD1' 'CMD2'  Run in batch mode with commands")
            print("\nExamples:")
            print(f"  {sys.argv[0]}                           # Interactive mode")
            print(f"  {sys.argv[0]} --host 192.168.1.100     # Connect to specific host")
            print(f"  {sys.argv[0]} --port 9000              # Connect to specific port")
            print(f"  {sys.argv[0]} --batch 'ADD 5 3' 'MUL 7 6'  # Batch mode")
            sys.exit(0)
        elif arg == '--host':
            if i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
                i += 1
            else:
                print("Error: --host requires a value")
                sys.exit(1)
        elif arg == '--port':
            if i + 1 < len(sys.argv):
                try:
                    port = int(sys.argv[i + 1])
                except ValueError:
                    print(f"Error: Invalid port number: {sys.argv[i + 1]}")
                    sys.exit(1)
                i += 1
            else:
                print("Error: --port requires a value")
                sys.exit(1)
        elif arg == '--batch':
            batch_mode = True
            # Collect all remaining arguments as batch commands
            batch_commands = sys.argv[i + 1:]
            break
        else:
            print(f"Error: Unknown argument: {arg}")
            print(f"Use {sys.argv[0]} --help for usage information")
            sys.exit(1)
        
        i += 1
    
    # Create and run client
    client = CalculatorClient(host, port)
    
    try:
        if batch_mode:
            if not batch_commands:
                print("Error: No commands provided for batch mode")
                sys.exit(1)
            client.run_batch(batch_commands)
        else:
            client.run_interactive()
    except Exception as e:
        print(f"Client error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()