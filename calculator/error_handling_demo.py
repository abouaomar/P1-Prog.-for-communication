#!/usr/bin/env python3
"""
Error Handling Demonstration for Calculator System
=================================================

This script demonstrates comprehensive error handling scenarios
for the CalcProtocol/1.0 calculator system. It covers all types
of errors students should understand and handle in their implementations.

Error Categories Covered:
1. Protocol Errors (INVALID status)
2. Mathematical Errors (ERROR status)
3. Network Errors (Connection issues)
4. Input Validation Errors
5. Server-side Error Scenarios

Learning Objectives:
- Understand different types of errors in network applications
- Learn proper error classification and handling strategies
- Practice defensive programming techniques
- Experience error recovery and graceful degradation
- Implement comprehensive error logging and reporting

Version: 1.0
Protocol: CalcProtocol/1.0
"""

import socket
import sys
import time
import threading
import logging
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime

# Configure logging for error tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error_handling_demo.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ErrorTestCase:
    """
    Represents a single error test case with expected behavior
    """
    def __init__(self, name: str, description: str, test_input: str, 
                 expected_status: str, category: str, severity: str = "medium"):
        self.name = name
        self.description = description
        self.test_input = test_input
        self.expected_status = expected_status
        self.category = category
        self.severity = severity
        self.result = None
        self.actual_response = None
        self.execution_time = 0
        self.error_details = None

class ErrorHandlingTester:
    """
    Comprehensive error handling tester for the calculator system
    
    This class provides:
    - Systematic error scenario testing
    - Error classification and analysis
    - Performance impact measurement
    - Detailed reporting and logging
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
        # Test results tracking
        self.test_results = []
        self.error_statistics = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'connection_errors': 0,
            'protocol_errors': 0,
            'mathematical_errors': 0,
            'validation_errors': 0
        }
        
        # Initialize test cases
        self.test_cases = self._initialize_test_cases()
        
        print("Error Handling Demonstration System")
        print("==================================")
        print(f"Target server: {host}:{port}")
        print(f"Total test cases: {len(self.test_cases)}")
        print()
    
    def _initialize_test_cases(self) -> List[ErrorTestCase]:
        """
        Initialize comprehensive error test cases
        
        Returns:
            List[ErrorTestCase]: Complete set of error test scenarios
        """
        test_cases = []
        
        # 1. Protocol Errors (INVALID status)
        protocol_errors = [
            ErrorTestCase(
                "Unknown Operation",
                "Test server response to unknown mathematical operation",
                "MULTIPLY 5 3",
                "INVALID",
                "protocol",
                "high"
            ),
            ErrorTestCase(
                "Missing Operands",
                "Test insufficient operands for binary operation",
                "ADD 5",
                "INVALID",
                "protocol",
                "high"
            ),
            ErrorTestCase(
                "Too Many Operands",
                "Test excess operands for unary operation",
                "SQRT 16 4",
                "INVALID",
                "protocol",
                "medium"
            ),
            ErrorTestCase(
                "Invalid Operand Format",
                "Test non-numeric operand handling",
                "ADD five 3",
                "INVALID",
                "protocol",
                "high"
            ),
            ErrorTestCase(
                "Empty Request",
                "Test empty request handling",
                "",
                "INVALID",
                "protocol",
                "medium"
            ),
            ErrorTestCase(
                "Malformed Request",
                "Test request with only operation name",
                "ADD",
                "INVALID",
                "protocol",
                "medium"
            ),
            ErrorTestCase(
                "Special Characters",
                "Test operands with special characters",
                "ADD 5@ 3#",
                "INVALID",
                "protocol",
                "medium"
            ),
            ErrorTestCase(
                "Multiple Decimal Points",
                "Test invalid decimal number format",
                "ADD 5.3.2 3",
                "INVALID",
                "protocol",
                "medium"
            )
        ]
        
        # 2. Mathematical Errors (ERROR status)
        mathematical_errors = [
            ErrorTestCase(
                "Division by Zero",
                "Test division by zero error handling",
                "DIV 10 0",
                "ERROR",
                "mathematical",
                "high"
            ),
            ErrorTestCase(
                "Square Root of Negative",
                "Test square root of negative number",
                "SQRT -25",
                "ERROR",
                "mathematical",
                "high"
            ),
            ErrorTestCase(
                "Large Number Overflow",
                "Test arithmetic overflow conditions",
                "POW 999 999",
                "ERROR",
                "mathematical",
                "medium"
            ),
            ErrorTestCase(
                "Very Small Division",
                "Test division resulting in very small numbers",
                "DIV 1 999999999",
                "OK",  # Should succeed but test precision
                "mathematical",
                "low"
            ),
            ErrorTestCase(
                "Negative Base Power",
                "Test negative base with fractional exponent",
                "POW -4 0.5",
                "ERROR",
                "mathematical",
                "medium"
            )
        ]
        
        # 3. Edge Cases and Boundary Conditions
        edge_cases = [
            ErrorTestCase(
                "Maximum Integer",
                "Test with very large integers",
                "ADD 999999999999999 1",
                "OK",
                "edge_case",
                "low"
            ),
            ErrorTestCase(
                "Minimum Integer",
                "Test with very small negative integers",
                "SUB -999999999999999 1",
                "OK",
                "edge_case",
                "low"
            ),
            ErrorTestCase(
                "Zero Operations",
                "Test operations with zero",
                "MUL 0 999999",
                "OK",
                "edge_case",
                "low"
            ),
            ErrorTestCase(
                "Scientific Notation",
                "Test scientific notation input",
                "ADD 1e10 2e5",
                "INVALID",  # Depends on server implementation
                "edge_case",
                "medium"
            ),
            ErrorTestCase(
                "Leading Zeros",
                "Test numbers with leading zeros",
                "ADD 007 003",
                "OK",
                "edge_case",
                "low"
            ),
            ErrorTestCase(
                "Decimal Precision",
                "Test high precision decimal operations",
                "DIV 1 3",
                "OK",
                "edge_case",
                "low"
            )
        ]
        
        # 4. Input Validation Edge Cases
        validation_cases = [
            ErrorTestCase(
                "Whitespace Handling",
                "Test excessive whitespace in request",
                "   ADD    5    3   ",
                "OK",
                "validation",
                "low"
            ),
            ErrorTestCase(
                "Case Sensitivity",
                "Test operation case sensitivity",
                "add 5 3",
                "OK",  # Should be case-insensitive
                "validation",
                "medium"
            ),
            ErrorTestCase(
                "Mixed Case",
                "Test mixed case operations",
                "AdD 5 3",
                "OK",
                "validation",
                "low"
            ),
            ErrorTestCase(
                "Tab Characters",
                "Test tab-separated operands",
                "ADD\\t5\\t3",
                "OK",
                "validation",
                "low"
            )
        ]
        
        # Combine all test cases
        test_cases.extend(protocol_errors)
        test_cases.extend(mathematical_errors)
        test_cases.extend(edge_cases)
        test_cases.extend(validation_cases)
        
        return test_cases
    
    def connect(self) -> bool:
        """
        Connect to the calculator server
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # Read welcome message
            welcome = self.socket.recv(1024).decode('utf-8').strip()
            logging.info(f"Connected to server: {welcome}")
            
            return True
            
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            self.connected = False
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
    
    def send_test_request(self, test_case: ErrorTestCase) -> bool:
        """
        Send a test request and measure response
        
        Args:
            test_case: Test case to execute
            
        Returns:
            bool: True if request sent successfully
        """
        if not self.connected:
            test_case.error_details = "Not connected to server"
            return False
        
        try:
            start_time = time.time()
            
            # Send request
            request = test_case.test_input + '\\n'
            self.socket.send(request.encode('utf-8'))
            
            # Receive response
            response = self.socket.recv(1024).decode('utf-8').strip()
            
            end_time = time.time()
            test_case.execution_time = (end_time - start_time) * 1000  # milliseconds
            test_case.actual_response = response
            
            return True
            
        except socket.timeout:
            test_case.error_details = "Response timeout"
            return False
        except Exception as e:
            test_case.error_details = f"Network error: {e}"
            return False
    
    def evaluate_test_result(self, test_case: ErrorTestCase) -> bool:
        """
        Evaluate if test case passed based on expected vs actual response
        
        Args:
            test_case: Test case to evaluate
            
        Returns:
            bool: True if test passed
        """
        if test_case.actual_response is None:
            test_case.result = "FAILED"
            return False
        
        # Check if response starts with expected status
        if test_case.actual_response.startswith(test_case.expected_status):
            test_case.result = "PASSED"
            return True
        else:
            test_case.result = "FAILED"
            return False
    
    def run_single_test(self, test_case: ErrorTestCase) -> bool:
        """
        Run a single test case
        
        Args:
            test_case: Test case to run
            
        Returns:
            bool: True if test passed
        """
        print(f"Running: {test_case.name}")
        print(f"  Description: {test_case.description}")
        print(f"  Input: '{test_case.test_input}'")
        print(f"  Expected: {test_case.expected_status}")
        
        # Send request and get response
        success = self.send_test_request(test_case)
        
        if not success:
            print(f"  Result: FAILED - {test_case.error_details}")
            test_case.result = "FAILED"
            return False
        
        # Evaluate result
        passed = self.evaluate_test_result(test_case)
        
        print(f"  Actual: {test_case.actual_response}")
        print(f"  Result: {test_case.result}")
        print(f"  Time: {test_case.execution_time:.2f}ms")
        
        if not passed:
            print(f"  ERROR: Expected '{test_case.expected_status}' but got '{test_case.actual_response}'")
        
        print("-" * 60)
        
        # Log result
        logging.info(f"Test '{test_case.name}': {test_case.result} - "
                    f"Input: '{test_case.test_input}' - "
                    f"Response: '{test_case.actual_response}' - "
                    f"Time: {test_case.execution_time:.2f}ms")
        
        return passed
    
    def run_all_tests(self) -> Dict:
        """
        Run all error handling test cases
        
        Returns:
            Dict: Test execution summary
        """
        print("Starting comprehensive error handling tests...")
        print("=" * 60)
        
        if not self.connect():
            print("ERROR: Cannot connect to server. Tests aborted.")
            return {"error": "Connection failed"}
        
        total_tests = len(self.test_cases)
        passed_tests = 0
        failed_tests = 0
        
        # Group tests by category for organized execution
        categories = {}
        for test_case in self.test_cases:
            if test_case.category not in categories:
                categories[test_case.category] = []
            categories[test_case.category].append(test_case)
        
        # Run tests by category
        for category, test_cases in categories.items():
            print(f"\\n{category.upper()} ERROR TESTS")
            print("=" * 40)
            
            for test_case in test_cases:
                try:
                    if self.run_single_test(test_case):
                        passed_tests += 1
                    else:
                        failed_tests += 1
                    
                    self.test_results.append(test_case)
                    
                    # Update statistics
                    self._update_statistics(test_case)
                    
                    # Small delay between tests
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"  EXCEPTION: {e}")
                    test_case.result = "EXCEPTION"
                    test_case.error_details = str(e)
                    failed_tests += 1
                    logging.error(f"Exception in test '{test_case.name}': {e}")
        
        self.disconnect()
        
        # Update final statistics
        self.error_statistics['total_tests'] = total_tests
        self.error_statistics['passed_tests'] = passed_tests
        self.error_statistics['failed_tests'] = failed_tests
        
        return self.error_statistics
    
    def _update_statistics(self, test_case: ErrorTestCase):
        """Update error statistics based on test case"""
        if test_case.category == "protocol":
            self.error_statistics['protocol_errors'] += 1
        elif test_case.category == "mathematical":
            self.error_statistics['mathematical_errors'] += 1
        elif test_case.category == "validation":
            self.error_statistics['validation_errors'] += 1
        
        if test_case.error_details and "Network" in test_case.error_details:
            self.error_statistics['connection_errors'] += 1
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive error handling report
        
        Returns:
            str: Formatted report
        """
        report = []
        report.append("\\n" + "=" * 80)
        report.append("ERROR HANDLING TEST REPORT")
        report.append("=" * 80)
        
        # Summary statistics
        stats = self.error_statistics
        report.append(f"\\nSUMMARY:")
        report.append(f"Total Tests: {stats['total_tests']}")
        report.append(f"Passed: {stats['passed_tests']} ({stats['passed_tests']/stats['total_tests']*100:.1f}%)")
        report.append(f"Failed: {stats['failed_tests']} ({stats['failed_tests']/stats['total_tests']*100:.1f}%)")
        
        report.append(f"\\nERROR CATEGORY BREAKDOWN:")
        report.append(f"Protocol Errors: {stats['protocol_errors']}")
        report.append(f"Mathematical Errors: {stats['mathematical_errors']}")
        report.append(f"Validation Errors: {stats['validation_errors']}")
        report.append(f"Connection Errors: {stats['connection_errors']}")
        
        # Performance analysis
        execution_times = [tc.execution_time for tc in self.test_results if tc.execution_time > 0]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)
            
            report.append(f"\\nPERFORMANCE ANALYSIS:")
            report.append(f"Average Response Time: {avg_time:.2f}ms")
            report.append(f"Maximum Response Time: {max_time:.2f}ms")
            report.append(f"Minimum Response Time: {min_time:.2f}ms")
        
        # Failed tests details
        failed_tests = [tc for tc in self.test_results if tc.result == "FAILED" or tc.result == "EXCEPTION"]
        if failed_tests:
            report.append(f"\\nFAILED TESTS DETAILS:")
            report.append("-" * 40)
            for test_case in failed_tests:
                report.append(f"Test: {test_case.name}")
                report.append(f"  Input: '{test_case.test_input}'")
                report.append(f"  Expected: {test_case.expected_status}")
                report.append(f"  Actual: {test_case.actual_response}")
                if test_case.error_details:
                    report.append(f"  Error: {test_case.error_details}")
                report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        report.append("-" * 40)
        
        if stats['failed_tests'] > 0:
            report.append("• Review failed test cases to improve error handling")
            report.append("• Ensure consistent error message formatting")
            report.append("• Implement proper input validation")
        
        if stats['connection_errors'] > 0:
            report.append("• Improve network error handling and recovery")
            report.append("• Implement connection retry mechanisms")
        
        if execution_times and max(execution_times) > 1000:
            report.append("• Optimize server response time for error conditions")
        
        if stats['passed_tests'] == stats['total_tests']:
            report.append("• Excellent error handling implementation!")
            report.append("• Consider adding more edge cases for comprehensive testing")
        
        report.append("\\n" + "=" * 80)
        
        return "\\n".join(report)
    
    def save_detailed_results(self, filename: str = None):
        """
        Save detailed test results to JSON file
        
        Args:
            filename: Output filename (optional)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_test_results_{timestamp}.json"
        
        results_data = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "server": f"{self.host}:{self.port}",
                "total_tests": len(self.test_results)
            },
            "statistics": self.error_statistics,
            "test_results": [
                {
                    "name": tc.name,
                    "description": tc.description,
                    "category": tc.category,
                    "severity": tc.severity,
                    "input": tc.test_input,
                    "expected_status": tc.expected_status,
                    "actual_response": tc.actual_response,
                    "result": tc.result,
                    "execution_time_ms": tc.execution_time,
                    "error_details": tc.error_details
                }
                for tc in self.test_results
            ]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            print(f"\\nDetailed results saved to: {filename}")
        except Exception as e:
            print(f"\\nError saving results: {e}")

def demonstrate_client_side_error_handling():
    """
    Demonstrate client-side error handling techniques
    """
    print("\\n" + "=" * 60)
    print("CLIENT-SIDE ERROR HANDLING DEMONSTRATION")
    print("=" * 60)
    
    print("\\n1. Connection Error Handling:")
    print("   - Server unavailable")
    print("   - Connection timeout")
    print("   - Connection lost during operation")
    
    print("\\n2. Input Validation:")
    print("   - Empty input detection")
    print("   - Format validation")
    print("   - Range checking")
    
    print("\\n3. Response Processing:")
    print("   - Status code parsing")
    print("   - Error message extraction")
    print("   - Timeout handling")
    
    print("\\n4. Recovery Strategies:")
    print("   - Automatic reconnection")
    print("   - Retry with exponential backoff")
    print("   - Graceful degradation")
    
    # Example client-side validation function
    def validate_client_input(user_input: str) -> Tuple[bool, str]:
        \"\"\"Example client-side input validation\"\"\"
        if not user_input.strip():
            return False, "Input cannot be empty"
        
        parts = user_input.strip().split()
        if len(parts) < 2:
            return False, "Invalid format: operation and operands required"
        
        operation = parts[0].upper()
        valid_ops = ['ADD', 'SUB', 'MUL', 'DIV', 'POW', 'SQRT']
        if operation not in valid_ops:
            return False, f"Unknown operation: {operation}"
        
        # Validate operands are numbers
        for operand in parts[1:]:
            try:
                float(operand)
            except ValueError:
                return False, f"Invalid number: {operand}"
        
        return True, ""
    
    # Test the validation function
    test_inputs = [
        "ADD 5 3",
        "INVALID 5 3",
        "ADD abc 3",
        "",
        "ADD"
    ]
    
    print("\\nClient-side validation examples:")
    for test_input in test_inputs:
        valid, error = validate_client_input(test_input)
        status = "✓" if valid else "✗"
        print(f"  {status} '{test_input}' -> {error if not valid else 'Valid'}")

def main():
    """
    Main function to run error handling demonstrations
    """
    # Parse command line arguments
    host = 'localhost'
    port = 8080
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    print(f"Error Handling Demo for Calculator Server")
    print(f"Target: {host}:{port}")
    print(f"Log file: error_handling_demo.log")
    print()
    
    # Create tester instance
    tester = ErrorHandlingTester(host, port)
    
    try:
        # Run all error handling tests
        results = tester.run_all_tests()
        
        if "error" in results:
            print(f"Testing failed: {results['error']}")
            return
        
        # Generate and display report
        report = tester.generate_report()
        print(report)
        
        # Save detailed results
        tester.save_detailed_results()
        
        # Demonstrate client-side error handling
        demonstrate_client_side_error_handling()
        
        print("\\nError handling demonstration complete!")
        print("Review the log file and JSON results for detailed analysis.")
        
    except KeyboardInterrupt:
        print("\\nDemo interrupted by user")
    except Exception as e:
        print(f"\\nDemo failed with error: {e}")
        logging.error(f"Demo exception: {e}")

if __name__ == "__main__":
    main()