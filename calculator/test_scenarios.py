#!/usr/bin/env python3
"""
Comprehensive Testing Script for Calculator System
=================================================

This script provides automated testing for the CalcProtocol/1.0 calculator system
with various scenarios including functional testing, performance testing,
stress testing, and integration testing.

Test Categories:
1. Functional Tests - Core mathematical operations
2. Protocol Compliance Tests - CalcProtocol/1.0 adherence
3. Performance Tests - Response time and throughput
4. Stress Tests - High load and concurrent connections
5. Integration Tests - Multi-client scenarios
6. Regression Tests - Ensure fixes don't break existing functionality

Learning Objectives:
- Understand comprehensive software testing strategies
- Learn automated testing frameworks and patterns
- Practice performance and stress testing techniques
- Implement test reporting and analysis
- Experience CI/CD testing concepts

Version: 1.0
Protocol: CalcProtocol/1.0
"""

import socket
import sys
import time
import threading
import concurrent.futures
import statistics
import json
import random
import logging
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_scenarios.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

@dataclass
class TestResult:
    """Data class to represent a test result"""
    test_name: str
    category: str
    success: bool
    response_time: float
    request: str
    response: str
    error_message: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class PerformanceMetrics:
    """Data class for performance metrics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    percentile_95: float
    percentile_99: float
    requests_per_second: float

class CalculatorTester:
    """
    Comprehensive testing framework for the calculator system
    
    This class provides:
    - Automated test execution
    - Performance measurement
    - Stress testing capabilities
    - Detailed reporting
    - Multi-threaded test scenarios
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.test_results: List[TestResult] = []
        self.performance_data: List[float] = []
        
        # Test configuration
        self.timeout = 30.0
        self.max_workers = 10
        
        print(f"Calculator Testing Framework v1.0")
        print(f"Target: {host}:{port}")
        print("=" * 50)
    
    def create_connection(self) -> Optional[socket.socket]:
        """
        Create a connection to the calculator server
        
        Returns:
            Optional[socket.socket]: Connected socket or None if failed
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            
            # Read welcome message
            welcome = sock.recv(1024).decode('utf-8').strip()
            logging.debug(f"Welcome message: {welcome}")
            
            return sock
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            return None
    
    def send_request(self, sock: socket.socket, request: str) -> Tuple[bool, str, float]:
        """
        Send a request and measure response time
        
        Args:
            sock: Connected socket
            request: Request string to send
            
        Returns:
            Tuple[bool, str, float]: (success, response, response_time_ms)
        """
        try:
            start_time = time.time()
            
            # Send request
            sock.send((request + '\\n').encode('utf-8'))
            
            # Receive response
            response = sock.recv(1024).decode('utf-8').strip()
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return True, response, response_time
            
        except Exception as e:
            return False, f"Error: {e}", 0.0
    
    def run_functional_tests(self) -> List[TestResult]:
        """
        Run functional tests for all mathematical operations
        
        Returns:
            List[TestResult]: Test results
        """
        print("\\nRunning Functional Tests")
        print("-" * 30)
        
        test_cases = [
            # Basic Addition Tests
            ("Basic Addition", "ADD 5 3", "OK 8"),
            ("Addition with Decimals", "ADD 2.5 3.7", "OK 6.2"),
            ("Addition with Negatives", "ADD -5 3", "OK -2"),
            ("Addition with Zero", "ADD 0 0", "OK 0"),
            
            # Basic Subtraction Tests
            ("Basic Subtraction", "SUB 10 4", "OK 6"),
            ("Subtraction with Decimals", "SUB 7.5 2.3", "OK 5.2"),
            ("Subtraction Negative Result", "SUB 3 7", "OK -4"),
            
            # Basic Multiplication Tests
            ("Basic Multiplication", "MUL 6 7", "OK 42"),
            ("Multiplication with Decimals", "MUL 2.5 4", "OK 10"),
            ("Multiplication by Zero", "MUL 5 0", "OK 0"),
            ("Multiplication by Negative", "MUL -3 4", "OK -12"),
            
            # Basic Division Tests
            ("Basic Division", "DIV 15 3", "OK 5"),
            ("Division with Decimals", "DIV 7.5 2.5", "OK 3"),
            ("Division by Zero", "DIV 10 0", "ERROR"),
            
            # Power Tests
            ("Basic Power", "POW 2 3", "OK 8"),
            ("Power with Decimals", "POW 2.5 2", "OK 6.25"),
            ("Power of Zero", "POW 5 0", "OK 1"),
            ("Zero to Power", "POW 0 5", "OK 0"),
            
            # Square Root Tests
            ("Basic Square Root", "SQRT 16", "OK 4"),
            ("Square Root Decimal", "SQRT 2.25", "OK 1.5"),
            ("Square Root of Zero", "SQRT 0", "OK 0"),
            ("Square Root of Negative", "SQRT -4", "ERROR"),
        ]
        
        results = []
        sock = self.create_connection()
        
        if not sock:
            print("Failed to connect to server for functional tests")
            return results
        
        try:
            for test_name, request, expected_prefix in test_cases:
                success, response, response_time = self.send_request(sock, request)
                
                # Check if response matches expected prefix
                test_success = success and response.startswith(expected_prefix)
                
                result = TestResult(
                    test_name=test_name,
                    category="functional",
                    success=test_success,
                    response_time=response_time,
                    request=request,
                    response=response,
                    error_message=None if test_success else f"Expected prefix '{expected_prefix}', got '{response}'"
                )
                
                results.append(result)
                self.test_results.append(result)
                self.performance_data.append(response_time)
                
                # Display result
                status = "✓" if test_success else "✗"
                print(f"{status} {test_name}: {request} -> {response} ({response_time:.2f}ms)")
                
        finally:
            sock.close()
        
        return results
    
    def run_protocol_compliance_tests(self) -> List[TestResult]:
        """
        Run tests to verify CalcProtocol/1.0 compliance
        
        Returns:
            List[TestResult]: Test results
        """
        print("\\nRunning Protocol Compliance Tests")
        print("-" * 35)
        
        test_cases = [
            # Invalid Operation Tests
            ("Unknown Operation", "MULTIPLY 5 3", "INVALID"),
            ("Typo in Operation", "ADDD 5 3", "INVALID"),
            ("Empty Operation", "", "INVALID"),
            
            # Invalid Operand Count Tests
            ("Too Few Operands ADD", "ADD 5", "INVALID"),
            ("Too Many Operands SQRT", "SQRT 16 4", "INVALID"),
            ("No Operands", "ADD", "INVALID"),
            
            # Invalid Operand Format Tests
            ("Non-numeric Operand", "ADD five 3", "INVALID"),
            ("Special Characters", "ADD 5@ 3", "INVALID"),
            ("Multiple Decimals", "ADD 5.3.2 3", "INVALID"),
            
            # Case Sensitivity Tests
            ("Lowercase Operation", "add 5 3", "OK"),
            ("Mixed Case Operation", "Add 5 3", "OK"),
            
            # Whitespace Tests
            ("Extra Whitespace", "  ADD   5   3  ", "OK"),
            ("Tab Characters", "ADD\\t5\\t3", "OK"),
        ]
        
        results = []
        sock = self.create_connection()
        
        if not sock:
            print("Failed to connect to server for protocol tests")
            return results
        
        try:
            for test_name, request, expected_prefix in test_cases:
                success, response, response_time = self.send_request(sock, request)
                
                # Check protocol compliance
                test_success = success and response.startswith(expected_prefix)
                
                result = TestResult(
                    test_name=test_name,
                    category="protocol",
                    success=test_success,
                    response_time=response_time,
                    request=request,
                    response=response,
                    error_message=None if test_success else f"Expected prefix '{expected_prefix}', got '{response}'"
                )
                
                results.append(result)
                self.test_results.append(result)
                
                # Display result
                status = "✓" if test_success else "✗"
                print(f"{status} {test_name}: '{request}' -> {response}")
                
        finally:
            sock.close()
        
        return results
    
    def run_performance_tests(self, num_requests: int = 100) -> PerformanceMetrics:
        """
        Run performance tests to measure response times
        
        Args:
            num_requests: Number of requests to send
            
        Returns:
            PerformanceMetrics: Performance analysis results
        """
        print(f"\\nRunning Performance Tests ({num_requests} requests)")
        print("-" * 40)
        
        test_requests = [
            "ADD 5 3",
            "SUB 10 4",
            "MUL 6 7",
            "DIV 15 3",
            "POW 2 8",
            "SQRT 16"
        ]
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        start_time = time.time()
        
        for i in range(num_requests):
            request = random.choice(test_requests)
            
            sock = self.create_connection()
            if not sock:
                failed_requests += 1
                continue
            
            try:
                success, response, response_time = self.send_request(sock, request)
                
                if success and response.startswith("OK"):
                    successful_requests += 1
                    response_times.append(response_time)
                else:
                    failed_requests += 1
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"Progress: {i + 1}/{num_requests} requests completed")
                
            finally:
                sock.close()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate performance metrics
        if response_times:
            metrics = PerformanceMetrics(
                total_requests=num_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                average_response_time=statistics.mean(response_times),
                min_response_time=min(response_times),
                max_response_time=max(response_times),
                percentile_95=self._percentile(response_times, 95),
                percentile_99=self._percentile(response_times, 99),
                requests_per_second=successful_requests / total_time if total_time > 0 else 0
            )
        else:
            metrics = PerformanceMetrics(
                total_requests=num_requests,
                successful_requests=0,
                failed_requests=failed_requests,
                average_response_time=0,
                min_response_time=0,
                max_response_time=0,
                percentile_95=0,
                percentile_99=0,
                requests_per_second=0
            )
        
        self._print_performance_metrics(metrics)
        return metrics
    
    def run_stress_tests(self, num_concurrent_clients: int = 5, requests_per_client: int = 20) -> List[TestResult]:
        """
        Run stress tests with multiple concurrent clients
        
        Args:
            num_concurrent_clients: Number of simultaneous clients
            requests_per_client: Number of requests each client sends
            
        Returns:
            List[TestResult]: Stress test results
        """
        print(f"\\nRunning Stress Tests ({num_concurrent_clients} clients, {requests_per_client} requests each)")
        print("-" * 60)
        
        def client_worker(client_id: int) -> List[TestResult]:
            \"\"\"Worker function for a single client\"\"\"
            results = []
            test_requests = ["ADD 5 3", "SUB 10 4", "MUL 6 7", "DIV 15 3"]
            
            for i in range(requests_per_client):
                request = random.choice(test_requests)
                
                sock = self.create_connection()
                if not sock:
                    result = TestResult(
                        test_name=f"Client-{client_id}-Request-{i+1}",
                        category="stress",
                        success=False,
                        response_time=0,
                        request=request,
                        response="Connection failed",
                        error_message="Failed to connect"
                    )
                    results.append(result)
                    continue
                
                try:
                    success, response, response_time = self.send_request(sock, request)
                    
                    result = TestResult(
                        test_name=f"Client-{client_id}-Request-{i+1}",
                        category="stress",
                        success=success and response.startswith("OK"),
                        response_time=response_time,
                        request=request,
                        response=response,
                        error_message=None if success else "Request failed"
                    )
                    results.append(result)
                    
                finally:
                    sock.close()
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.01)
            
            return results
        
        # Run concurrent clients
        all_results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_clients) as executor:
            # Submit all client tasks
            futures = [executor.submit(client_worker, i) for i in range(num_concurrent_clients)]
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    client_results = future.result()
                    all_results.extend(client_results)
                except Exception as e:
                    logging.error(f"Client worker failed: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Add results to main collection
        self.test_results.extend(all_results)
        
        # Analyze stress test results
        successful_tests = sum(1 for r in all_results if r.success)
        failed_tests = len(all_results) - successful_tests
        total_requests = len(all_results)
        
        print(f"\\nStress Test Results:")
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {successful_tests} ({successful_tests/total_requests*100:.1f}%)")
        print(f"Failed: {failed_tests} ({failed_tests/total_requests*100:.1f}%)")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Average Throughput: {total_requests/total_time:.2f} requests/second")
        
        return all_results
    
    def run_edge_case_tests(self) -> List[TestResult]:
        """
        Run edge case and boundary condition tests
        
        Returns:
            List[TestResult]: Edge case test results
        """
        print("\\nRunning Edge Case Tests")
        print("-" * 25)
        
        test_cases = [
            # Boundary Value Tests
            ("Large Numbers", "ADD 999999999 1", "OK"),
            ("Very Small Numbers", "DIV 1 999999999", "OK"),
            ("Zero Edge Cases", "POW 0 0", "OK"),  # 0^0 is typically 1
            ("Negative Powers", "POW -2 3", "OK"),
            
            # Precision Tests
            ("High Precision Division", "DIV 1 3", "OK"),
            ("Decimal Addition", "ADD 0.1 0.2", "OK"),
            ("Scientific Edge Cases", "POW 10 10", "OK"),
            
            # Input Format Edge Cases
            ("Leading Zeros", "ADD 007 003", "OK"),
            ("Trailing Zeros", "ADD 5.000 3.000", "OK"),
            ("Negative Zero", "ADD -0 0", "OK"),
        ]
        
        results = []
        sock = self.create_connection()
        
        if not sock:
            print("Failed to connect to server for edge case tests")
            return results
        
        try:
            for test_name, request, expected_prefix in test_cases:
                success, response, response_time = self.send_request(sock, request)
                
                # For edge cases, we mainly check that the server responds appropriately
                test_success = success and (response.startswith("OK") or response.startswith("ERROR"))
                
                result = TestResult(
                    test_name=test_name,
                    category="edge_case",
                    success=test_success,
                    response_time=response_time,
                    request=request,
                    response=response,
                    error_message=None if test_success else "Server did not respond appropriately"
                )
                
                results.append(result)
                self.test_results.append(result)
                
                # Display result
                status = "✓" if test_success else "✗"
                print(f"{status} {test_name}: {request} -> {response}")
                
        finally:
            sock.close()
        
        return results
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of a dataset"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_data) - 1)
        weight = index - lower_index
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
    
    def _print_performance_metrics(self, metrics: PerformanceMetrics):
        """Print formatted performance metrics"""
        print(f"\\nPerformance Metrics:")
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Successful: {metrics.successful_requests}")
        print(f"Failed: {metrics.failed_requests}")
        print(f"Success Rate: {metrics.successful_requests/metrics.total_requests*100:.1f}%")
        print(f"Average Response Time: {metrics.average_response_time:.2f}ms")
        print(f"Min Response Time: {metrics.min_response_time:.2f}ms")
        print(f"Max Response Time: {metrics.max_response_time:.2f}ms")
        print(f"95th Percentile: {metrics.percentile_95:.2f}ms")
        print(f"99th Percentile: {metrics.percentile_99:.2f}ms")
        print(f"Requests per Second: {metrics.requests_per_second:.2f}")
    
    def generate_comprehensive_report(self) -> str:
        """
        Generate a comprehensive test report
        
        Returns:
            str: Formatted test report
        """
        report = []
        report.append("\\n" + "=" * 80)
        report.append("COMPREHENSIVE CALCULATOR TESTING REPORT")
        report.append("=" * 80)
        
        # Summary by category
        categories = {}
        for result in self.test_results:
            if result.category not in categories:
                categories[result.category] = {'total': 0, 'passed': 0, 'failed': 0}
            categories[result.category]['total'] += 1
            if result.success:
                categories[result.category]['passed'] += 1
            else:
                categories[result.category]['failed'] += 1
        
        report.append(f"\\nTEST SUMMARY BY CATEGORY:")
        report.append("-" * 40)
        for category, stats in categories.items():
            pass_rate = stats['passed'] / stats['total'] * 100 if stats['total'] > 0 else 0
            report.append(f"{category.upper()}: {stats['passed']}/{stats['total']} passed ({pass_rate:.1f}%)")
        
        # Overall statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        overall_pass_rate = passed_tests / total_tests * 100 if total_tests > 0 else 0
        
        report.append(f"\\nOVERALL STATISTICS:")
        report.append(f"Total Tests: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {total_tests - passed_tests}")
        report.append(f"Pass Rate: {overall_pass_rate:.1f}%")
        
        # Performance analysis
        if self.performance_data:
            avg_time = statistics.mean(self.performance_data)
            report.append(f"\\nPERFORMANCE ANALYSIS:")
            report.append(f"Average Response Time: {avg_time:.2f}ms")
            report.append(f"Total Requests Measured: {len(self.performance_data)}")
        
        # Failed tests
        failed_tests = [r for r in self.test_results if not r.success]
        if failed_tests:
            report.append(f"\\nFAILED TESTS:")
            report.append("-" * 20)
            for result in failed_tests[:10]:  # Show first 10 failures
                report.append(f"• {result.test_name}: {result.request}")
                report.append(f"  Expected: Success, Got: {result.response}")
                if result.error_message:
                    report.append(f"  Error: {result.error_message}")
                report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        report.append("-" * 20)
        if overall_pass_rate >= 95:
            report.append("• Excellent performance! System is working correctly.")
        elif overall_pass_rate >= 80:
            report.append("• Good performance with room for improvement.")
            report.append("• Review failed test cases for optimization opportunities.")
        else:
            report.append("• Significant issues detected. Review and fix failed tests.")
            report.append("• Focus on protocol compliance and error handling.")
        
        if self.performance_data and statistics.mean(self.performance_data) > 100:
            report.append("• Consider performance optimization for response times.")
        
        report.append("\\n" + "=" * 80)
        return "\\n".join(report)
    
    def save_results(self, filename: str = None):
        """
        Save test results to JSON file
        
        Args:
            filename: Output filename (optional)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        results_data = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "server": f"{self.host}:{self.port}",
                "total_tests": len(self.test_results)
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "category": r.category,
                    "success": r.success,
                    "response_time_ms": r.response_time,
                    "request": r.request,
                    "response": r.response,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp
                }
                for r in self.test_results
            ]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            print(f"\\nTest results saved to: {filename}")
        except Exception as e:
            print(f"\\nError saving results: {e}")

def main():
    """Main function to run comprehensive testing"""
    parser = argparse.ArgumentParser(description="Calculator System Testing Framework")
    parser.add_argument("--host", default="localhost", help="Server hostname")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--functional", action="store_true", help="Run functional tests only")
    parser.add_argument("--protocol", action="store_true", help="Run protocol tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--stress", action="store_true", help="Run stress tests only")
    parser.add_argument("--edge", action="store_true", help="Run edge case tests only")
    parser.add_argument("--perf-requests", type=int, default=100, help="Number of performance test requests")
    parser.add_argument("--stress-clients", type=int, default=5, help="Number of concurrent stress test clients")
    parser.add_argument("--stress-requests", type=int, default=20, help="Requests per stress test client")
    
    args = parser.parse_args()
    
    print(f"Calculator System Testing Framework")
    print(f"Target: {args.host}:{args.port}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = CalculatorTester(args.host, args.port)
    
    try:
        # Determine which tests to run
        run_all = not any([args.functional, args.protocol, args.performance, args.stress, args.edge])
        
        if run_all or args.functional:
            tester.run_functional_tests()
        
        if run_all or args.protocol:
            tester.run_protocol_compliance_tests()
        
        if run_all or args.performance:
            tester.run_performance_tests(args.perf_requests)
        
        if run_all or args.stress:
            tester.run_stress_tests(args.stress_clients, args.stress_requests)
        
        if run_all or args.edge:
            tester.run_edge_case_tests()
        
        # Generate and display report
        report = tester.generate_comprehensive_report()
        print(report)
        
        # Save results
        tester.save_results()
        
        print("\\nTesting complete! Check the log file and JSON results for detailed analysis.")
        
    except KeyboardInterrupt:
        print("\\nTesting interrupted by user")
    except Exception as e:
        print(f"\\nTesting failed with error: {e}")
        logging.error(f"Testing exception: {e}")

if __name__ == "__main__":
    main()