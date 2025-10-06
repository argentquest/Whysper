import React, { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import '@xterm/xterm/css/xterm.css';

interface TerminalComponentProps {
  sessionId: string;
  onCommand?: (command: string) => void;
  onConnectionChange?: (connected: boolean) => void;
  theme?: 'light' | 'dark';
  height?: string;
}

export const TerminalComponent: React.FC<TerminalComponentProps> = ({
  sessionId,
  onCommand,
  onConnectionChange,
  theme = 'dark',
  height = '400px'
}) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const terminal = useRef<Terminal | null>(null);
  const fitAddon = useRef<FitAddon | null>(null);
  const websocket = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [currentLine, setCurrentLine] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [sessionShellType, setSessionShellType] = useState<string>('auto');
  
  const getPromptForShell = (shellType?: string) => {
    const type = shellType || sessionShellType;
    switch (type) {
      case 'cmd':
        return '>';
      case 'powershell':
        return 'PS>';
      case 'bash':
        return '$';
      default:
        return '$';
    }
  };
  
  // Initialize terminal
  useEffect(() => {
    if (!terminalRef.current) return;

    // Create terminal instance
    terminal.current = new Terminal({
      theme: {
        background: theme === 'dark' ? '#1e1e1e' : '#ffffff',
        foreground: theme === 'dark' ? '#ffffff' : '#000000',
        cursor: theme === 'dark' ? '#ffffff' : '#000000',
      },
      fontSize: 14,
      fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
      cursorBlink: true,
      convertEol: true,
      scrollback: 1000,
      cols: 80,
      rows: 24,
    });

    // Add addons
    fitAddon.current = new FitAddon();
    terminal.current.loadAddon(fitAddon.current);
    terminal.current.loadAddon(new WebLinksAddon());

    // Open terminal
    terminal.current.open(terminalRef.current);
    
    // Handle data input
    terminal.current.onData(handleTerminalInput);

    // Handle resize
    const handleResize = () => {
      if (fitAddon.current && terminal.current) {
        try {
          fitAddon.current.fit();
        } catch (error) {
          console.warn('Error fitting terminal:', error);
        }
      }
    };

    window.addEventListener('resize', handleResize);
    
    // Wait for terminal to be properly initialized before fitting and connecting
    const initTimer = setTimeout(() => {
      if (fitAddon.current && terminal.current && terminalRef.current) {
        try {
          // Ensure parent has dimensions
          const parent = terminalRef.current.parentElement;
          if (parent && parent.offsetWidth > 0 && parent.offsetHeight > 0) {
            fitAddon.current.fit();
            terminal.current.focus();
            // Connect to WebSocket after terminal is ready
            connectWebSocket();
          } else {
            // Retry if parent doesn't have dimensions yet
            setTimeout(() => {
              if (fitAddon.current && terminal.current) {
                try {
                  fitAddon.current.fit();
                  terminal.current.focus();
                  connectWebSocket();
                } catch (error) {
                  console.warn('Error in delayed terminal setup:', error);
                  connectWebSocket(); // Connect anyway
                }
              }
            }, 200);
          }
        } catch (error) {
          console.warn('Error in terminal setup:', error);
          // Connect anyway in case of fit issues
          connectWebSocket();
        }
      }
    }, 150);

    return () => {
      clearTimeout(initTimer);
      window.removeEventListener('resize', handleResize);
      if (websocket.current) {
        websocket.current.close();
      }
      if (terminal.current) {
        terminal.current.dispose();
      }
    };
  }, [sessionId]);

  // Handle theme changes
  useEffect(() => {
    if (terminal.current) {
      terminal.current.options.theme = {
        background: theme === 'dark' ? '#1e1e1e' : '#ffffff',
        foreground: theme === 'dark' ? '#ffffff' : '#000000',
        cursor: theme === 'dark' ? '#ffffff' : '#000000',
      };
    }
  }, [theme]);

  const connectWebSocket = () => {
    if (websocket.current) {
      websocket.current.close();
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8001/api/v1/shell/ws/${sessionId}`;
    
    try {
      websocket.current = new WebSocket(wsUrl);

      websocket.current.onopen = () => {
        console.log('WebSocket connected to:', wsUrl);
        setIsConnected(true);
        onConnectionChange?.(true);
        if (terminal.current) {
          terminal.current.write('\r\n🔌 Connected to shell session\r\n');
          // Don't show a prompt immediately, let the backend handle it
        }
      };

      websocket.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      websocket.current.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        onConnectionChange?.(false);
        if (terminal.current) {
          terminal.current.write('\r\n🔌 Connection closed\r\n');
        }
        
        // Auto-reconnect after a delay if it wasn't a clean close
        if (event.code !== 1000 && event.code !== 1001) {
          setTimeout(() => {
            if (!isConnected) {
              console.log('Attempting to reconnect...');
              connectWebSocket();
            }
          }, 3000);
        }
      };

      websocket.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (terminal.current) {
          terminal.current.write('\r\n❌ Connection error - retrying...\r\n');
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      if (terminal.current) {
        terminal.current.write('\r\n❌ Failed to create connection\r\n');
      }
    }
  };

  const handleWebSocketMessage = (message: any) => {
    if (!terminal.current) return;

    switch (message.type) {
      case 'output':
        // Write command output to terminal
        terminal.current.write(message.data);
        break;
        
      case 'echo':
        // Command was echoed back - we already displayed it locally
        break;
        
      case 'status':
        if (message.data === 'completed' || message.data === 'failed') {
          // Command finished, show new prompt based on shell type
          const prompt = getPromptForShell();
          terminal.current.write(`\r\n${prompt} `);
        } else if (message.data === 'connected') {
          // Initial connection - show session info and prompt
          if (message.session_info) {
            const info = message.session_info;
            setSessionShellType(info.shell_type);
            terminal.current.write(`\r\n📁 ${info.working_directory} (${info.shell_type})\r\n`);
            const prompt = getPromptForShell(info.shell_type);
            terminal.current.write(`${prompt} `);
          } else {
            const prompt = getPromptForShell();
            terminal.current.write(`\r\n${prompt} `);
          }
        }
        break;
        
      case 'error':
        const errorPrompt = getPromptForShell();
        terminal.current.write(`\r\n❌ Error: ${message.data}\r\n${errorPrompt} `);
        break;
        
      case 'pong':
        // Keepalive response
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const handleTerminalInput = (data: string) => {
    // Allow input even when not connected for better UX - show local echo
    if (!terminal.current) return;

    // Handle special keys
    if (data === '\r' || data === '\n') { // Enter key
      if (currentLine.trim()) {
        // Add to history
        setCommandHistory(prev => [...prev, currentLine.trim()]);
        setHistoryIndex(-1);
        
        // Send command via WebSocket if connected
        if (isConnected) {
          sendCommand(currentLine.trim());
        } else {
          // Show command locally even if not connected
          terminal.current.write(`\r\nCommand queued (connecting...): ${currentLine.trim()}\r\n`);
        }
        onCommand?.(currentLine.trim());
      }
      
      terminal.current.write('\r\n');
      setCurrentLine('');
      return;
    }
    
    if (data === '\x7f' || data === '\b') { // Backspace
      if (currentLine.length > 0) {
        terminal.current.write('\b \b');
        setCurrentLine(prev => prev.slice(0, -1));
      }
      return;
    }
    
    // Handle arrow keys
    if (data === '\x1b[A') { // Up arrow
      navigateHistory(-1);
      return;
    }
    if (data === '\x1b[B') { // Down arrow
      navigateHistory(1);
      return;
    }
    
    // Handle printable characters (simplified approach)
    if (data.length === 1 && data.charCodeAt(0) >= 32) {
      terminal.current.write(data);
      setCurrentLine(prev => prev + data);
    }
  };

  const navigateHistory = (direction: number) => {
    if (!terminal.current) return;

    let newIndex = historyIndex + direction;
    
    if (newIndex < -1) {
      newIndex = -1;
    } else if (newIndex >= commandHistory.length) {
      newIndex = commandHistory.length - 1;
    }

    setHistoryIndex(newIndex);

    // Clear current line
    if (commandHistory.length === 0) return;
    for (let i = 0; i < currentLine.length; i++) {
      terminal.current.write('\b \b');
    }
    
    // Write historical command or empty line
    const command = newIndex === -1 ? '' : commandHistory[commandHistory.length - 1 - newIndex];
    terminal.current.write(command);
    setCurrentLine(command);
  };

  const sendCommand = (command: string) => {
    if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
      websocket.current.send(JSON.stringify({
        type: 'command',
        data: command
      }));
    }
  };

  const clearTerminal = () => {
    if (terminal.current) {
      terminal.current.clear();
      terminal.current.write('$ ');
    }
  };

  const reconnect = () => {
    connectWebSocket();
  };

  const handleTerminalClick = () => {
    if (terminal.current) {
      terminal.current.focus();
    }
  };

  return (
    <div className="terminal-container" style={{ height }}>
      <div 
        ref={terminalRef} 
        className="terminal-element"
        onClick={handleTerminalClick}
        style={{ 
          height: '100%',
          backgroundColor: theme === 'dark' ? '#1e1e1e' : '#ffffff'
        }}
      />
      
      {/* Terminal Status */}
      <div className={`terminal-status ${isConnected ? 'connected' : 'disconnected'}`}>
        <span className={`status-indicator ${isConnected ? 'green' : 'red'}`}>
          ●
        </span>
        <span className="status-text">
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
        {!isConnected && (
          <button 
            onClick={reconnect}
            className="reconnect-button"
          >
            Reconnect
          </button>
        )}
        <button 
          onClick={clearTerminal}
          className="clear-button"
        >
          Clear
        </button>
      </div>

      <style>{`
        .terminal-container {
          display: flex;
          flex-direction: column;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          overflow: hidden;
          min-height: 400px;
          width: 100%;
        }
        
        .terminal-element {
          flex: 1;
          padding: 8px;
          min-height: 350px;
          width: 100%;
        }
        
        .terminal-status {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          background: #f9fafb;
          border-top: 1px solid #e5e7eb;
          font-size: 12px;
        }
        
        .terminal-status.connected {
          background: #f0f9ff;
        }
        
        .terminal-status.disconnected {
          background: #fef2f2;
        }
        
        .status-indicator {
          font-size: 8px;
        }
        
        .status-indicator.green {
          color: #10b981;
        }
        
        .status-indicator.red {
          color: #ef4444;
        }
        
        .status-text {
          color: #6b7280;
          font-weight: 500;
        }
        
        .reconnect-button, .clear-button {
          margin-left: auto;
          padding: 4px 8px;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 11px;
          cursor: pointer;
        }
        
        .clear-button {
          background: #6b7280;
          margin-left: 8px;
        }
        
        .reconnect-button:hover, .clear-button:hover {
          opacity: 0.9;
        }
      `}</style>
    </div>
  );
};

export default TerminalComponent;