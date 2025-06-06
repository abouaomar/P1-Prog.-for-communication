/**
 * Java Calculator Client
 * ======================
 * 
 * This is a comprehensive Java implementation of a calculator client
 * that connects to the CalcProtocol/1.0 server using TCP sockets.
 * 
 * Features:
 * - Command-line interface with rich input handling
 * - Robust connection management with automatic retry
 * - Comprehensive input validation and error handling
 * - Multi-mode operation (interactive and batch)
 * - Detailed logging and error reporting
 * - Exception handling and resource management
 * 
 * Learning Objectives:
 * - Understand Java Socket programming for TCP connections
 * - Learn exception handling and resource management (try-with-resources)
 * - Practice object-oriented design patterns
 * - Implement command-line argument parsing
 * - Experience multi-threaded programming concepts
 * - Learn Java I/O streams and buffered communication
 * 
 * Requirements:
 * - Java 8 or higher
 * - No external dependencies (uses only standard Java libraries)
 * 
 * Compilation:
 *   javac CalculatorClient.java
 * 
 * Usage:
 *   java CalculatorClient [options]
 *   java CalculatorClient --host localhost --port 8080
 *   java CalculatorClient --batch \"ADD 5 3\" \"MUL 7 6\"
 * 
 * Version: 1.0
 * Protocol: CalcProtocol/1.0
 */

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;

/**
 * Operation class to represent calculator operations
 * This encapsulates operation metadata for validation and help
 */
class Operation {
    private final String name;
    private final String description;
    private final String example;
    private final int operandCount;
    
    public Operation(String name, String description, String example, int operandCount) {
        this.name = name;
        this.description = description;
        this.example = example;
        this.operandCount = operandCount;
    }
    
    // Getters
    public String getName() { return name; }
    public String getDescription() { return description; }
    public String getExample() { return example; }
    public int getOperandCount() { return operandCount; }
}

/**
 * Response class to represent server responses
 * This provides structured access to response components
 */
class ServerResponse {
    public enum Status { OK, ERROR, INVALID, UNKNOWN }
    
    private final Status status;
    private final String message;
    private final String rawResponse;
    
    public ServerResponse(String rawResponse) {
        this.rawResponse = rawResponse.trim();
        
        if (rawResponse.startsWith(\"OK \")) {
            this.status = Status.OK;
            this.message = rawResponse.substring(3);
        } else if (rawResponse.startsWith(\"ERROR \")) {
            this.status = Status.ERROR;
            this.message = rawResponse.substring(6);
        } else if (rawResponse.startsWith(\"INVALID \")) {
            this.status = Status.INVALID;
            this.message = rawResponse.substring(8);
        } else {
            this.status = Status.UNKNOWN;
            this.message = rawResponse;
        }
    }
    
    // Getters
    public Status getStatus() { return status; }
    public String getMessage() { return message; }
    public String getRawResponse() { return rawResponse; }
    
    public boolean isSuccess() { return status == Status.OK; }
    public boolean isError() { return status == Status.ERROR || status == Status.INVALID; }
}

/**
 * Main Calculator Client Class
 * 
 * This class implements a full-featured calculator client with:
 * - Connection management
 * - User interface
 * - Input validation
 * - Error handling
 * - Batch processing
 */
public class CalculatorClient {
    
    // ANSI Color codes for enhanced console output
    public static final String RESET = \"\\u001B[0m\";
    public static final String BLACK = \"\\u001B[30m\";
    public static final String RED = \"\\u001B[31m\";
    public static final String GREEN = \"\\u001B[32m\";
    public static final String YELLOW = \"\\u001B[33m\";
    public static final String BLUE = \"\\u001B[34m\";
    public static final String PURPLE = \"\\u001B[35m\";
    public static final String CYAN = \"\\u001B[36m\";
    public static final String WHITE = \"\\u001B[37m\";
    public static final String BOLD = \"\\u001B[1m\";
    
    // Configuration
    private final String host;
    private final int port;
    private final int connectionTimeout;
    private final int readTimeout;
    private final int maxRetryAttempts;
    
    // Connection state
    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;
    private boolean connected;
    private int retryAttempts;
    
    // Supported operations
    private final Map<String, Operation> operations;
    
    // Scanner for user input
    private final Scanner scanner;
    
    /**
     * Constructor with default configuration
     */
    public CalculatorClient() {
        this(\"localhost\", 8080);
    }
    
    /**
     * Constructor with custom host and port
     * 
     * @param host Server hostname or IP address
     * @param port Server port number
     */
    public CalculatorClient(String host, int port) {
        this.host = host;
        this.port = port;
        this.connectionTimeout = 10000; // 10 seconds
        this.readTimeout = 30000; // 30 seconds
        this.maxRetryAttempts = 3;
        
        this.connected = false;
        this.retryAttempts = 0;
        
        this.scanner = new Scanner(System.in);
        
        // Initialize supported operations
        this.operations = new HashMap<>();
        initializeOperations();
        
        // Setup shutdown hook for cleanup
        Runtime.getRuntime().addShutdownHook(new Thread(this::cleanup));
        
        displayWelcome();
    }
    
    /**
     * Initialize the supported operations map
     */
    private void initializeOperations() {
        operations.put(\"ADD\", new Operation(\"ADD\", \"Addition: ADD num1 num2\", \"ADD 5 3\", 2));
        operations.put(\"SUB\", new Operation(\"SUB\", \"Subtraction: SUB num1 num2\", \"SUB 10 4\", 2));
        operations.put(\"MUL\", new Operation(\"MUL\", \"Multiplication: MUL num1 num2\", \"MUL 7 6\", 2));
        operations.put(\"DIV\", new Operation(\"DIV\", \"Division: DIV num1 num2\", \"DIV 15 3\", 2));
        operations.put(\"POW\", new Operation(\"POW\", \"Exponentiation: POW base exponent\", \"POW 2 8\", 2));
        operations.put(\"SQRT\", new Operation(\"SQRT\", \"Square root: SQRT number\", \"SQRT 16\", 1));
    }
    
    /**
     * Display welcome message with formatting
     */
    private void displayWelcome() {
        System.out.println(BOLD + CYAN);
        System.out.println(\"╔═══════════════════════════════════════════╗\");
        System.out.println(\"║        Java Calculator Client v1.0       ║\");
        System.out.println(\"║      (Standard Library Implementation)    ║\");
        System.out.println(\"╚═══════════════════════════════════════════╝\");
        System.out.println(RESET);
    }
    
    /**
     * Connect to the calculator server
     * 
     * @return true if connection successful, false otherwise
     */
    public boolean connect() {
        try {
            System.out.printf(\"%sConnecting to %s:%d...%s%n\", YELLOW, host, port, RESET);
            
            // Create socket with timeout
            socket = new Socket();
            socket.connect(new InetSocketAddress(host, port), connectionTimeout);
            socket.setSoTimeout(readTimeout);
            
            // Setup I/O streams
            out = new PrintWriter(socket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            
            connected = true;
            retryAttempts = 0;
            
            System.out.printf(\"%s✓ Connected to %s:%d%s%n\", GREEN, host, port, RESET);
            
            // Read welcome message
            String welcome = readResponse();
            if (welcome != null && !welcome.isEmpty()) {
                System.out.printf(\"%sServer: %s%s%n\", CYAN, welcome, RESET);
            }
            
            return true;
            
        } catch (ConnectException e) {
            System.out.printf(\"%s✗ Connection refused - server not available%s%n\", RED, RESET);
            return false;
        } catch (SocketTimeoutException e) {
            System.out.printf(\"%s✗ Connection timeout - server not responding%s%n\", RED, RESET);
            return false;
        } catch (IOException e) {
            System.out.printf(\"%s✗ Connection failed: %s%s%n\", RED, e.getMessage(), RESET);
            return false;
        }
    }
    
    /**
     * Disconnect from the server
     */
    public void disconnect() {
        connected = false;
        
        // Close resources in reverse order
        try {
            if (out != null) {
                out.close();
            }
        } catch (Exception e) {
            // Ignore cleanup errors
        }
        
        try {
            if (in != null) {
                in.close();
            }
        } catch (Exception e) {
            // Ignore cleanup errors
        }
        
        try {
            if (socket != null && !socket.isClosed()) {
                socket.close();
            }
        } catch (Exception e) {
            // Ignore cleanup errors
        }
        
        System.out.printf(\"%sDisconnected from server%s%n\", YELLOW, RESET);
    }
    
    /**
     * Send a request to the server
     * 
     * @param request Request string to send
     * @return true if sent successfully, false otherwise
     */
    private boolean sendRequest(String request) {
        if (!connected || out == null) {
            System.out.printf(\"%s✗ Not connected to server%s%n\", RED, RESET);
            return false;
        }
        
        try {
            out.println(request);
            
            // Check if the stream encountered an error
            if (out.checkError()) {
                System.out.printf(\"%s✗ Error sending request%s%n\", RED, RESET);
                connected = false;
                return false;
            }
            
            return true;
            
        } catch (Exception e) {
            System.out.printf(\"%s✗ Error sending request: %s%s%n\", RED, e.getMessage(), RESET);
            connected = false;
            return false;
        }
    }
    
    /**
     * Read a response from the server
     * 
     * @return Response string or null if error
     */
    private String readResponse() {
        if (!connected || in == null) {
            return null;
        }
        
        try {
            String response = in.readLine();
            
            if (response == null) {
                System.out.printf(\"%s✗ Server closed connection%s%n\", RED, RESET);
                connected = false;
                return null;
            }
            
            return response;
            
        } catch (SocketTimeoutException e) {
            System.out.printf(\"%s✗ Response timeout - server not responding%s%n\", RED, RESET);
            return null;
        } catch (IOException e) {
            System.out.printf(\"%s✗ Error reading response: %s%s%n\", RED, e.getMessage(), RESET);
            connected = false;
            return null;
        }
    }
    
    /**
     * Validate user input according to CalcProtocol/1.0
     * 
     * @param input User input string
     * @return Validation result object with success status and error message
     */
    private ValidationResult validateInput(String input) {
        if (input == null || input.trim().isEmpty()) {
            return new ValidationResult(false, \"Empty input\");
        }
        
        String[] parts = input.trim().split(\"\\\\s+\");
        
        if (parts.length < 1) {
            return new ValidationResult(false, \"Invalid input format\");
        }
        
        String operation = parts[0].toUpperCase();
        
        // Check if operation is supported
        if (!operations.containsKey(operation)) {
            return new ValidationResult(false, 
                String.format(\"Unknown operation: %s. Type 'help' for available operations.\", operation));
        }
        
        // Check operand count
        Operation op = operations.get(operation);
        int expectedOperands = op.getOperandCount();
        int providedOperands = parts.length - 1;
        
        if (providedOperands != expectedOperands) {
            return new ValidationResult(false,
                String.format(\"%s requires %d operand(s), got %d\", operation, expectedOperands, providedOperands));
        }
        
        // Validate operands are numbers
        Pattern numberPattern = Pattern.compile(\"-?\\\\d+(\\\\.\\\\d+)?\");
        for (int i = 1; i < parts.length; i++) {
            if (!numberPattern.matcher(parts[i]).matches()) {
                return new ValidationResult(false,
                    String.format(\"Invalid operand #%d: '%s' is not a number\", i, parts[i]));
            }
        }
        
        return new ValidationResult(true, \"\");
    }
    
    /**
     * Format and display server response
     * 
     * @param response Server response object
     */
    private void displayResponse(ServerResponse response) {
        switch (response.getStatus()) {
            case OK:
                System.out.printf(\"%s✓ Result: %s%s%s%n\", GREEN, BOLD, response.getMessage(), RESET);
                break;
            case ERROR:
                System.out.printf(\"%s✗ Error: %s%s%n\", RED, response.getMessage(), RESET);
                break;
            case INVALID:
                System.out.printf(\"%s✗ Invalid: %s%s%n\", RED, response.getMessage(), RESET);
                break;
            default:
                System.out.printf(\"%sServer: %s%s%n\", CYAN, response.getRawResponse(), RESET);
        }
    }
    
    /**
     * Display help information
     */
    private void showHelp() {
        System.out.printf(\"%n%s%sCalculator Client Help%s%n\", BOLD, CYAN, RESET);
        System.out.printf(\"%s%s%s%n%n\", CYAN, \"=\".repeat(50), RESET);
        
        System.out.printf(\"%sAvailable Operations:%s%n\", BOLD, RESET);
        System.out.printf(\"%s%s%s%n\", CYAN, \"-\".repeat(50), RESET);
        
        for (Operation op : operations.values()) {
            System.out.printf(\"%s%s%s%n\", GREEN, op.getDescription(), RESET);
            System.out.printf(\"  %sExample: %s%s%n%n\", BOLD, op.getExample(), RESET);
        }
        
        System.out.printf(\"%sSpecial Commands:%s%n\", BOLD, RESET);
        System.out.printf(\"%s%s%s%n\", CYAN, \"-\".repeat(50), RESET);
        System.out.printf(\"%shelp%s       - Show this help message%n\", YELLOW, RESET);
        System.out.printf(\"%squit, exit%s - Disconnect and exit%n\", YELLOW, RESET);
        System.out.printf(\"%sreconnect%s  - Reconnect to server%n\", YELLOW, RESET);
        System.out.printf(\"%sstatus%s     - Show connection status%n%n\", YELLOW, RESET);
        
        System.out.printf(\"%sNotes:%s%n\", BOLD, RESET);
        System.out.printf(\"%s%s%s%n\", CYAN, \"-\".repeat(50), RESET);
        System.out.println(\"- Operations are case-insensitive\");
        System.out.println(\"- Numbers can be integers or decimals\");
        System.out.println(\"- Use Ctrl+C to exit at any time\");
        System.out.println();
    }
    
    /**
     * Display connection status
     */
    private void showStatus() {
        System.out.printf(\"%n%sConnection Status:%s%n\", BOLD, RESET);
        System.out.printf(\"%s%s%s%n\", CYAN, \"─\".repeat(30), RESET);
        System.out.printf(\"Host: %s%s%s%n\", YELLOW, host, RESET);
        System.out.printf(\"Port: %s%d%s%n\", YELLOW, port, RESET);
        
        if (connected) {
            System.out.printf(\"Status: %sConnected ✓%s%n\", GREEN, RESET);
            System.out.printf(\"%sReady to send calculations%s%n\", GREEN, RESET);
        } else {
            System.out.printf(\"Status: %sDisconnected ✗%s%n\", RED, RESET);
            System.out.printf(\"%sUse 'reconnect' to connect%s%n\", RED, RESET);
        }
        System.out.println();
    }
    
    /**
     * Attempt to reconnect with exponential backoff
     * 
     * @return true if reconnection successful, false otherwise
     */
    private boolean attemptReconnect() {
        if (retryAttempts >= maxRetryAttempts) {
            System.out.printf(\"%s✗ Maximum reconnection attempts reached%s%n\", RED, RESET);
            return false;
        }
        
        retryAttempts++;
        long delay = (long) Math.pow(2, retryAttempts) * 1000; // Exponential backoff
        
        System.out.printf(\"%sAttempting to reconnect (%d/%d)...%s%n\", 
            YELLOW, retryAttempts, maxRetryAttempts, RESET);
        
        if (delay > 1000) {
            System.out.printf(\"%sWaiting %d seconds before retry...%s%n\", YELLOW, delay/1000, RESET);
            try {
                TimeUnit.MILLISECONDS.sleep(delay);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }
        
        return connect();
    }
    
    /**
     * Process user input and handle special commands
     * 
     * @param input User input string
     * @return true to continue, false to exit
     */
    private boolean processInput(String input) {
        String trimmedInput = input.trim();
        
        if (trimmedInput.isEmpty()) {
            return true;
        }
        
        String lowerInput = trimmedInput.toLowerCase();
        
        // Handle special commands
        switch (lowerInput) {
            case \"quit\":
            case \"exit\":
                return false;
                
            case \"help\":
                showHelp();
                return true;
                
            case \"status\":
                showStatus();
                return true;
                
            case \"reconnect\":
                disconnect();
                if (connect()) {
                    System.out.printf(\"%sReconnected successfully%s%n\", GREEN, RESET);
                } else {
                    System.out.printf(\"%sReconnection failed%s%n\", RED, RESET);
                }
                return true;
        }
        
        // Check connection status
        if (!connected) {
            System.out.printf(\"%s✗ Not connected to server. Use 'reconnect' to connect.%s%n\", RED, RESET);
            return true;
        }
        
        // Validate calculation input
        ValidationResult validation = validateInput(trimmedInput);
        if (!validation.isValid()) {
            System.out.printf(\"%s✗ %s%s%n\", RED, validation.getErrorMessage(), RESET);
            return true;
        }
        
        // Send request to server
        if (!sendRequest(trimmedInput)) {
            // Connection error - try to reconnect
            System.out.printf(\"%sAttempting to reconnect...%s%n\", YELLOW, RESET);
            if (attemptReconnect()) {
                System.out.printf(\"%sReconnected! Retrying request...%s%n\", GREEN, RESET);
                if (sendRequest(trimmedInput)) {
                    String responseStr = readResponse();
                    if (responseStr != null) {
                        displayResponse(new ServerResponse(responseStr));
                    }
                }
            }
            return true;
        }
        
        // Read and display response
        String responseStr = readResponse();
        if (responseStr != null) {
            displayResponse(new ServerResponse(responseStr));
        } else {
            System.out.printf(\"%s✗ No response received from server%s%n\", RED, RESET);
        }
        
        return true;
    }
    
    /**
     * Run the calculator in interactive mode
     */
    public void runInteractive() {
        try {
            // Initial connection
            if (!connect()) {
                System.out.print(\"Connection failed. Retry? (y/n): \");
                String retry = scanner.nextLine().trim().toLowerCase();
                if (!retry.equals(\"y\")) {
                    return;
                }
                if (!connect()) {
                    System.out.printf(\"%sUnable to connect. Exiting.%s%n\", RED, RESET);
                    return;
                }
            }
            
            System.out.printf(\"%n%sType 'help' for available operations, 'quit' to exit%s%n\", BOLD, RESET);
            System.out.printf(\"%sCalculator ready! Enter calculations:%s%n%n\", CYAN, RESET);
            
            // Main interaction loop
            while (true) {
                System.out.printf(\"%scalc> %s\", CYAN, RESET);
                String input = scanner.nextLine();
                
                if (!processInput(input)) {
                    break; // Exit requested
                }
            }
            
        } catch (Exception e) {
            System.out.printf(\"%s✗ Unexpected error: %s%s%n\", RED, e.getMessage(), RESET);
        } finally {
            disconnect();
            System.out.printf(\"%n%sGoodbye! 👋%s%n\", GREEN, RESET);
        }
    }
    
    /**
     * Run the calculator in batch mode
     * 
     * @param commands List of commands to execute
     */
    public void runBatch(String[] commands) {
        System.out.println(\"Running in batch mode...\");
        
        if (!connect()) {
            System.out.printf(\"%sFailed to connect for batch processing%s%n\", RED, RESET);
            return;
        }
        
        for (int i = 0; i < commands.length; i++) {
            String command = commands[i];
            System.out.printf(\"%n[%d] %s%n\", i + 1, command);
            
            // Validate command
            ValidationResult validation = validateInput(command);
            if (!validation.isValid()) {
                System.out.printf(\"%s✗ %s%s%n\", RED, validation.getErrorMessage(), RESET);
                continue;
            }
            
            // Send and receive
            if (sendRequest(command)) {
                String responseStr = readResponse();
                if (responseStr != null) {
                    System.out.print(\"    \");
                    displayResponse(new ServerResponse(responseStr));
                } else {
                    System.out.printf(\"    %s✗ No response received%s%n\", RED, RESET);
                }
            } else {
                System.out.printf(\"    %s✗ Failed to send request%s%n\", RED, RESET);
            }
        }
        
        disconnect();
        System.out.printf(\"%n%sBatch processing complete%s%n\", GREEN, RESET);
    }
    
    /**
     * Cleanup resources
     */
    private void cleanup() {
        if (connected) {
            disconnect();
        }
        if (scanner != null) {
            scanner.close();
        }
    }
    
    /**
     * Display usage information
     */
    private static void showUsage() {
        System.out.println(\"Java Calculator Client\");
        System.out.println(\"Usage:\");
        System.out.println(\"  java CalculatorClient [options]\");
        System.out.println();
        System.out.println(\"Options:\");
        System.out.println(\"  -h, --help              Show this help\");
        System.out.println(\"  --host HOST            Server hostname (default: localhost)\");
        System.out.println(\"  --port PORT            Server port (default: 8080)\");
        System.out.println(\"  --batch CMD1 CMD2 ...  Run in batch mode with commands\");
        System.out.println();
        System.out.println(\"Examples:\");
        System.out.println(\"  java CalculatorClient                           # Interactive mode\");
        System.out.println(\"  java CalculatorClient --host 192.168.1.100     # Connect to specific host\");
        System.out.println(\"  java CalculatorClient --port 9000              # Connect to specific port\");
        System.out.println(\"  java CalculatorClient --batch \\\"ADD 5 3\\\" \\\"MUL 7 6\\\"  # Batch mode\");
    }
    
    /**
     * Main method - entry point of the application
     * 
     * @param args Command line arguments
     */
    public static void main(String[] args) {
        // Default configuration
        String host = \"localhost\";
        int port = 8080;
        boolean batchMode = false;
        List<String> batchCommands = new ArrayList<>();
        
        // Parse command line arguments
        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case \"-h\":
                case \"--help\":
                    showUsage();
                    System.exit(0);
                    break;
                    
                case \"--host\":
                    if (i + 1 < args.length) {
                        host = args[++i];
                    } else {
                        System.err.println(\"Error: --host requires a value\");
                        System.exit(1);
                    }
                    break;
                    
                case \"--port\":
                    if (i + 1 < args.length) {
                        try {
                            port = Integer.parseInt(args[++i]);
                            if (port < 1 || port > 65535) {
                                throw new NumberFormatException(\"Port out of range\");
                            }
                        } catch (NumberFormatException e) {
                            System.err.printf(\"Error: Invalid port number: %s%n\", args[i]);
                            System.exit(1);
                        }
                    } else {
                        System.err.println(\"Error: --port requires a value\");
                        System.exit(1);
                    }
                    break;
                    
                case \"--batch\":
                    batchMode = true;
                    // Collect all remaining arguments as batch commands
                    for (int j = i + 1; j < args.length; j++) {
                        batchCommands.add(args[j]);
                    }
                    i = args.length; // Exit the parsing loop
                    break;
                    
                default:
                    System.err.printf(\"Error: Unknown argument: %s%n\", args[i]);
                    System.err.println(\"Use java CalculatorClient --help for usage information\");
                    System.exit(1);
            }
        }
        
        // Create and run client
        CalculatorClient client = new CalculatorClient(host, port);
        
        try {
            if (batchMode) {
                if (batchCommands.isEmpty()) {
                    System.err.println(\"Error: No commands provided for batch mode\");
                    System.exit(1);
                }
                client.runBatch(batchCommands.toArray(new String[0]));
            } else {
                client.runInteractive();
            }
        } catch (Exception e) {
            System.err.printf(\"Client error: %s%n\", e.getMessage());
            System.exit(1);
        }
    }
}

/**
 * Validation result helper class
 */
class ValidationResult {
    private final boolean valid;
    private final String errorMessage;
    
    public ValidationResult(boolean valid, String errorMessage) {
        this.valid = valid;
        this.errorMessage = errorMessage;
    }
    
    public boolean isValid() { return valid; }
    public String getErrorMessage() { return errorMessage; }
}