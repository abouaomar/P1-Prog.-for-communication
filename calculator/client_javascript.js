#!/usr/bin/env node
/**
 * JavaScript Calculator Client (Node.js)
 * =====================================
 * 
 * This is a JavaScript/Node.js implementation of a calculator client
 * that connects to the CalcProtocol/1.0 server using TCP sockets.
 * - Interactive command-line interface using readline
 * - Real-time connection status monitoring
 * - Comprehensive input validation
 * - Error handling and auto-reconnection
 * - Command history and auto-completion
 * - Colorized output for better user experience
 * 
 * Learning Objectives:
 * - Understand Node.js net module for TCP sockets
 * - Learn asynchronous programming with callbacks and promises
 * - Practice event-driven programming patterns
 * - Implement interactive CLI applications in JavaScript
 * - Experience client-server communication in JavaScript
 * 
 * Requirements:
 * - Node.js (v12.0.0 or higher)
 * - No external dependencies (uses only built-in modules)
 * 
 * Version: 1.0
 * Protocol: CalcProtocol/1.0
 */

const net = require('net');
const readline = require('readline');
const process = require('process');

/**
 * ANSI color codes for colorized output
 * These make the interface more user-friendly
 */
const Colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    white: '\x1b[37m'
};

/**
 * JavaScript Calculator Client Class
 * 
 * This class encapsulates all the functionality needed for a calculator client:
 * - Connection management
 * - User interface
 * - Input validation
 * - Error handling
 */
class JavaScriptCalculatorClient {
    /**
     * Initialize the calculator client
     * 
     * @param {string} host - Server hostname or IP address
     * @param {number} port - Server port number
     */
    constructor(host = 'localhost', port = 8080) {
        this.host = host;
        this.port = port;
        this.socket = null;
        this.connected = false;
        this.running = true;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        
        // Setup readline interface for user interaction
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            prompt: `${Colors.cyan}calc> ${Colors.reset}`,
            completer: this.completer.bind(this)
        });
        
        // Define supported operations for validation and help
        this.operations = {
            'ADD': {
                description: 'Addition: ADD num1 num2',
                example: 'ADD 5 3',
                operands: 2,
                color: Colors.green
            },
            'SUB': {
                description: 'Subtraction: SUB num1 num2', 
                example: 'SUB 10 4',
                operands: 2,
                color: Colors.green
            },
            'MUL': {
                description: 'Multiplication: MUL num1 num2',
                example: 'MUL 7 6', 
                operands: 2,
                color: Colors.yellow
            },
            'DIV': {
                description: 'Division: DIV num1 num2',
                example: 'DIV 15 3',
                operands: 2,
                color: Colors.yellow
            },
            'POW': {
                description: 'Exponentiation: POW base exponent',
                example: 'POW 2 8',
                operands: 2,
                color: Colors.magenta
            },
            'SQRT': {
                description: 'Square root: SQRT number',
                example: 'SQRT 16',
                operands: 1,
                color: Colors.blue
            }
        };
        
        // Setup signal handlers for graceful shutdown
        process.on('SIGINT', () => this.handleShutdown());
        process.on('SIGTERM', () => this.handleShutdown());
        
        this.displayWelcome();
    }
    
    /**
     * Display welcome message with styling
     */
    displayWelcome() {
        console.log(`${Colors.bright}${Colors.cyan}`);
        console.log('╔════════════════════════════════════════╗');
        console.log('║    JavaScript Calculator Client v1.0  ║');
        console.log('║         (Node.js Implementation)      ║');
        console.log('╚════════════════════════════════════════╝');
        console.log(`${Colors.reset}`);
    }
    
    /**
     * Auto-completion function for readline
     * Provides tab completion for operations and commands
     * 
     * @param {string} line - Current input line
     * @returns {Array} Array of [completions, originalLine]
     */
    completer(line) {
        const operations = Object.keys(this.operations);
        const commands = ['help', 'quit', 'exit', 'reconnect', 'status'];
        const allCompletions = [...operations, ...commands];
        
        const hits = allCompletions.filter(cmd => 
            cmd.toLowerCase().startsWith(line.toLowerCase())
        );
        
        return [hits.length ? hits : allCompletions, line];
    }
    
    /**
     * Connect to the calculator server
     * 
     * @returns {Promise<boolean>} Promise that resolves to true if connected
     */
    connect() {
        return new Promise((resolve) => {
            console.log(`${Colors.yellow}Connecting to ${this.host}:${this.port}...${Colors.reset}`);
            
            // Create TCP socket
            this.socket = new net.Socket();
            
            // Set connection timeout
            this.socket.setTimeout(10000); // 10 seconds
            
            // Connection event handlers
            this.socket.on('connect', () => {
                this.connected = true;
                this.reconnectAttempts = 0;
                console.log(`${Colors.green}✓ Connected to ${this.host}:${this.port}${Colors.reset}`);
                
                // Remove timeout after successful connection
                this.socket.setTimeout(0);
                resolve(true);
            });
            
            this.socket.on('data', (data) => {
                const response = data.toString().trim();
                
                // Check if this is a welcome message (contains \"Welcome\")
                if (response.includes('Welcome')) {
                    console.log(`${Colors.cyan}Server: ${response}${Colors.reset}`);
                } else {
                    // This is a response to a calculation
                    this.displayResponse(response);
                    this.rl.prompt();
                }
            });
            
            this.socket.on('error', (error) => {
                if (error.code === 'ECONNREFUSED') {
                    console.log(`${Colors.red}✗ Connection refused - server not available${Colors.reset}`);
                } else if (error.code === 'ETIMEDOUT') {
                    console.log(`${Colors.red}✗ Connection timeout - server not responding${Colors.reset}`);
                } else {
                    console.log(`${Colors.red}✗ Connection error: ${error.message}${Colors.reset}`);
                }
                this.connected = false;
                resolve(false);
            });
            
            this.socket.on('close', () => {
                if (this.connected) {
                    console.log(`${Colors.yellow}Connection closed by server${Colors.reset}`);
                }
                this.connected = false;
            });
            
            this.socket.on('timeout', () => {
                console.log(`${Colors.red}✗ Connection timeout${Colors.reset}`);
                this.socket.destroy();
                this.connected = false;
                resolve(false);
            });
            
            // Attempt connection
            this.socket.connect(this.port, this.host);
        });
    }
    
    /**
     * Disconnect from the server
     */
    disconnect() {
        if (this.socket) {
            this.socket.destroy();
            this.socket = null;
        }
        this.connected = false;
        console.log(`${Colors.yellow}Disconnected from server${Colors.reset}`);
    }
    
    /**
     * Send a request to the server
     * 
     * @param {string} request - Request string to send
     * @returns {boolean} True if sent successfully
     */
    sendRequest(request) {
        if (!this.connected || !this.socket) {
            console.log(`${Colors.red}✗ Not connected to server${Colors.reset}`);
            return false;
        }
        
        try {
            this.socket.write(request + '\\n');
            return true;
        } catch (error) {
            console.log(`${Colors.red}✗ Error sending request: ${error.message}${Colors.reset}`);
            this.connected = false;
            return false;
        }
    }
    
    /**
     * Validate user input according to CalcProtocol/1.0
     * 
     * @param {string} input - User input string
     * @returns {Object} Validation result {valid: boolean, error: string}
     */
    validateInput(input) {
        if (!input.trim()) {
            return { valid: false, error: 'Empty input' };
        }
        
        const parts = input.trim().split(/\\s+/);
        
        if (parts.length < 1) {
            return { valid: false, error: 'Invalid input format' };
        }
        
        const operation = parts[0].toUpperCase();
        
        // Check if operation is supported
        if (!this.operations[operation]) {
            return { 
                valid: false, 
                error: `Unknown operation: ${operation}. Type 'help' for available operations.`
            };
        }
        
        // Check operand count
        const expectedOperands = this.operations[operation].operands;
        const providedOperands = parts.length - 1;
        
        if (providedOperands !== expectedOperands) {
            return {
                valid: false,
                error: `${operation} requires ${expectedOperands} operand(s), got ${providedOperands}`
            };
        }
        
        // Validate operands are numbers
        for (let i = 1; i < parts.length; i++) {
            const operand = parts[i];
            if (isNaN(operand) || operand === '') {
                return {
                    valid: false,
                    error: `Invalid operand #${i}: '${operand}' is not a number`
                };
            }
        }
        
        return { valid: true, error: '' };
    }
    
    /**
     * Display server response with appropriate formatting and colors
     * 
     * @param {string} response - Server response string
     */
    displayResponse(response) {
        if (response.startsWith('OK ')) {
            const result = response.substring(3);
            console.log(`${Colors.green}✓ Result: ${Colors.bright}${result}${Colors.reset}`);
        } else if (response.startsWith('ERROR ')) {
            const error = response.substring(6);
            console.log(`${Colors.red}✗ Error: ${error}${Colors.reset}`);
        } else if (response.startsWith('INVALID ')) {
            const error = response.substring(8);
            console.log(`${Colors.red}✗ Invalid: ${error}${Colors.reset}`);
        } else {
            console.log(`${Colors.cyan}Server: ${response}${Colors.reset}`);
        }
    }
    
    /**
     * Display help information with colors and formatting
     */
    showHelp() {
        console.log(`\\n${Colors.bright}${Colors.cyan}Calculator Client Help${Colors.reset}`);
        console.log(`${Colors.cyan}${'='.repeat(50)}${Colors.reset}\\n`);
        
        console.log(`${Colors.bright}Available Operations:${Colors.reset}`);
        console.log(`${Colors.cyan}${'-'.repeat(50)}${Colors.reset}`);
        
        Object.entries(this.operations).forEach(([op, info]) => {
            console.log(`${info.color}${info.description}${Colors.reset}`);
            console.log(`  ${Colors.bright}Example: ${info.example}${Colors.reset}\\n`);
        });
        
        console.log(`${Colors.bright}Special Commands:${Colors.reset}`);
        console.log(`${Colors.cyan}${'-'.repeat(50)}${Colors.reset}`);
        console.log(`${Colors.yellow}help${Colors.reset}       - Show this help message`);
        console.log(`${Colors.yellow}quit, exit${Colors.reset} - Disconnect and exit`);
        console.log(`${Colors.yellow}reconnect${Colors.reset}  - Reconnect to server`);
        console.log(`${Colors.yellow}status${Colors.reset}     - Show connection status\\n`);
        
        console.log(`${Colors.bright}Notes:${Colors.reset}`);
        console.log(`${Colors.cyan}${'-'.repeat(50)}${Colors.reset}`);
        console.log('- Operations are case-insensitive');
        console.log('- Numbers can be integers or decimals');
        console.log('- Use Tab for auto-completion');
        console.log('- Use Ctrl+C to exit at any time\\n');
    }
    
    /**
     * Display connection status with visual indicators
     */
    showStatus() {
        console.log(`\\n${Colors.bright}Connection Status:${Colors.reset}`);
        console.log(`${Colors.cyan}${'─'.repeat(30)}${Colors.reset}`);
        console.log(`Host: ${Colors.yellow}${this.host}${Colors.reset}`);
        console.log(`Port: ${Colors.yellow}${this.port}${Colors.reset}`);
        
        if (this.connected) {
            console.log(`Status: ${Colors.green}Connected ✓${Colors.reset}`);
            console.log(`${Colors.green}Ready to send calculations${Colors.reset}`);
        } else {
            console.log(`Status: ${Colors.red}Disconnected ✗${Colors.reset}`);
            console.log(`${Colors.red}Use 'reconnect' to connect${Colors.reset}`);
        }
        console.log();
    }
    
    /**
     * Attempt to reconnect with exponential backoff
     * 
     * @returns {Promise<boolean>} Promise that resolves to connection status
     */
    async attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log(`${Colors.red}✗ Maximum reconnection attempts reached${Colors.reset}`);
            return false;
        }
        
        this.reconnectAttempts++;
        const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff
        
        console.log(`${Colors.yellow}Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...${Colors.reset}`);
        
        if (delay > 1000) {
            console.log(`${Colors.yellow}Waiting ${delay/1000} seconds before retry...${Colors.reset}`);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
        
        return await this.connect();
    }
    
    /**
     * Process user input and handle special commands
     * 
     * @param {string} input - User input string
     */
    async processInput(input) {
        const trimmedInput = input.trim();
        
        if (!trimmedInput) {
            this.rl.prompt();
            return;
        }
        
        const lowerInput = trimmedInput.toLowerCase();
        
        // Handle special commands
        switch (lowerInput) {
            case 'quit':
            case 'exit':
                this.handleShutdown();
                return;
                
            case 'help':
                this.showHelp();
                this.rl.prompt();
                return;
                
            case 'status':
                this.showStatus();
                this.rl.prompt();
                return;
                
            case 'reconnect':
                this.disconnect();
                const connected = await this.connect();
                if (connected) {
                    console.log(`${Colors.green}Reconnected successfully${Colors.reset}`);
                } else {
                    console.log(`${Colors.red}Reconnection failed${Colors.reset}`);
                }
                this.rl.prompt();
                return;
        }
        
        // Check connection status
        if (!this.connected) {
            console.log(`${Colors.red}✗ Not connected to server. Use 'reconnect' to connect.${Colors.reset}`);
            this.rl.prompt();
            return;
        }
        
        // Validate calculation input
        const validation = this.validateInput(trimmedInput);
        if (!validation.valid) {
            console.log(`${Colors.red}✗ ${validation.error}${Colors.reset}`);
            this.rl.prompt();
            return;
        }
        
        // Send request to server
        if (!this.sendRequest(trimmedInput)) {
            // Connection error - try to reconnect
            console.log(`${Colors.yellow}Attempting to reconnect...${Colors.reset}`);
            const reconnected = await this.attemptReconnect();
            
            if (reconnected) {
                console.log(`${Colors.green}Reconnected! Retrying request...${Colors.reset}`);
                if (this.sendRequest(trimmedInput)) {
                    // Response will be handled by the data event
                    return;
                }
            }
            this.rl.prompt();
        }
        
        // Note: Response will be displayed by the socket data event handler
        // The prompt will be shown after the response is received
    }
    
    /**
     * Handle graceful shutdown
     */
    handleShutdown() {
        console.log(`\\n${Colors.yellow}Shutting down calculator client...${Colors.reset}`);
        this.running = false;
        this.disconnect();
        this.rl.close();
        
        console.log(`${Colors.green}Goodbye! 👋${Colors.reset}`);
        process.exit(0);
    }
    
    /**
     * Start the interactive calculator client
     */
    async start() {
        try {
            // Initial connection attempt
            const connected = await this.connect();
            
            if (!connected) {
                const retry = await this.askYesNo('Connection failed. Retry? (y/n): ');
                if (!retry) {
                    console.log(`${Colors.red}Exiting...${Colors.reset}`);
                    process.exit(1);
                }
                
                const reconnected = await this.connect();
                if (!reconnected) {
                    console.log(`${Colors.red}Unable to connect. Exiting.${Colors.reset}`);
                    process.exit(1);
                }
            }
            
            // Display usage instructions
            console.log(`\\n${Colors.bright}Type 'help' for available operations, 'quit' to exit${Colors.reset}`);
            console.log(`${Colors.cyan}Calculator ready! Enter calculations:${Colors.reset}\\n`);
            
            // Setup readline event handlers
            this.rl.on('line', (input) => {
                this.processInput(input);
            });
            
            this.rl.on('close', () => {
                this.handleShutdown();
            });
            
            // Start the interactive prompt
            this.rl.prompt();
            
        } catch (error) {
            console.error(`${Colors.red}Fatal error: ${error.message}${Colors.reset}`);
            process.exit(1);
        }
    }
    
    /**
     * Helper method to ask yes/no questions
     * 
     * @param {string} question - Question to ask
     * @returns {Promise<boolean>} Promise that resolves to user's answer
     */
    askYesNo(question) {
        return new Promise((resolve) => {
            this.rl.question(question, (answer) => {
                resolve(answer.toLowerCase().trim() === 'y');
            });
        });
    }
}

/**
 * Main function to parse arguments and start the client
 */
function main() {
    // Default configuration
    const DEFAULT_HOST = 'localhost';
    const DEFAULT_PORT = 8080;
    
    // Parse command line arguments
    let host = DEFAULT_HOST;
    let port = DEFAULT_PORT;
    
    const args = process.argv.slice(2);
    
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        
        switch (arg) {
            case '-h':
            case '--help':
                console.log('JavaScript Calculator Client (Node.js)');
                console.log('Usage:');
                console.log(`  node ${process.argv[1]} [options]`);
                console.log('\\nOptions:');
                console.log('  -h, --help              Show this help');
                console.log('  --host HOST            Server hostname (default: localhost)');
                console.log('  --port PORT            Server port (default: 8080)');
                console.log('\\nExamples:');
                console.log(`  node ${process.argv[1]}                           # Interactive mode`);
                console.log(`  node ${process.argv[1]} --host 192.168.1.100     # Connect to specific host`);
                console.log(`  node ${process.argv[1]} --port 9000              # Connect to specific port`);
                process.exit(0);
                break;
                
            case '--host':
                if (i + 1 < args.length) {
                    host = args[i + 1];
                    i++;
                } else {
                    console.error('Error: --host requires a value');
                    process.exit(1);
                }
                break;
                
            case '--port':
                if (i + 1 < args.length) {
                    const portValue = parseInt(args[i + 1]);
                    if (isNaN(portValue) || portValue < 1 || portValue > 65535) {
                        console.error(`Error: Invalid port number: ${args[i + 1]}`);
                        process.exit(1);
                    }
                    port = portValue;
                    i++;
                } else {
                    console.error('Error: --port requires a value');
                    process.exit(1);
                }
                break;
                
            default:
                console.error(`Error: Unknown argument: ${arg}`);
                console.error(`Use node ${process.argv[1]} --help for usage information`);
                process.exit(1);
        }
    }
    
    // Create and start the client
    const client = new JavaScriptCalculatorClient(host, port);
    client.start().catch((error) => {
        console.error(`${Colors.red}Client error: ${error.message}${Colors.reset}`);
        process.exit(1);
    });
}

// Export the client class for potential reuse
module.exports = JavaScriptCalculatorClient;

// Run the main function if this file is executed directly
if (require.main === module) {
    main();
}