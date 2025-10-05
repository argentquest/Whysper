"""
Shell Service for Whysper Web2 Backend.

This service manages shell sessions and command execution with proper security controls.
It provides real-time command execution with output streaming via WebSocket connections.

Features:
- Secure command execution with validation
- Real-time stdout/stderr streaming
- Session management and cleanup
- Working directory restrictions
- Command filtering and timeouts
"""
import asyncio
import subprocess
import os
import uuid
import time
from typing import Dict, Optional, Set, Callable, Any
from dataclasses import dataclass
from enum import Enum
from common.logger import get_logger
from common.env_manager import env_manager

logger = get_logger(__name__)

class CommandStatus(Enum):
    """Command execution status states."""
    RUNNING = "running"
    COMPLETED = "completed" 
    FAILED = "failed"
    TIMEOUT = "timeout"
    KILLED = "killed"

@dataclass
class ShellSession:
    """Represents an active shell session."""
    id: str
    process: Optional[subprocess.Popen]
    working_directory: str
    shell_type: str
    created_at: float
    last_activity: float
    is_active: bool = True
    command_count: int = 0

class ShellSecurityManager:
    """Manages security controls for shell command execution."""
    
    # Commands that are explicitly blocked for security
    BLOCKED_COMMANDS = {
        'rm', 'rmdir', 'del', 'format', 'fdisk', 'mkfs', 'dd',
        'shutdown', 'reboot', 'halt', 'poweroff', 'init',
        'passwd', 'su', 'sudo', 'chmod', 'chown', 'chgrp',
        'mount', 'umount', 'fsck', 'e2fsck',
        'killall', 'pkill', 'kill'
    }
    
    # Commands that are allowed without restrictions
    ALLOWED_COMMANDS = {
        'ls', 'dir', 'pwd', 'cd', 'cat', 'type', 'echo', 'find',
        'grep', 'head', 'tail', 'wc', 'sort', 'uniq', 'cut',
        'git', 'npm', 'pip', 'python', 'py', 'node', 'java',
        'mvn', 'gradle', 'make', 'cargo', 'go', 'dotnet',
        'curl', 'wget', 'ping', 'telnet', 'ssh', 'scp',
        'tar', 'zip', 'unzip', 'gzip', 'gunzip',
        'ps', 'top', 'htop', 'df', 'du', 'free', 'uname',
        'which', 'where', 'whoami', 'date', 'uptime'
    }
    
    # Dangerous argument patterns
    DANGEROUS_PATTERNS = {
        '-rf', '--force', '--no-preserve-root', '>', '>>', 
        '|', '&&', '||', ';', '`', '$(',
        'eval', 'exec', 'source', '.'
    }

    @classmethod
    def is_command_safe(cls, command: str) -> tuple[bool, str]:
        """
        Check if a command is safe to execute.
        
        Returns:
            tuple[bool, str]: (is_safe, reason)
        """
        if not command or not command.strip():
            return False, "Empty command"
            
        # Parse the base command
        parts = command.strip().split()
        if not parts:
            return False, "No command found"
            
        base_command = parts[0].lower()
        
        # Remove path prefixes (e.g., ./command, /usr/bin/command)
        if '/' in base_command or '\\' in base_command:
            base_command = os.path.basename(base_command)
        
        # Check for explicitly blocked commands
        if base_command in cls.BLOCKED_COMMANDS:
            return False, f"Command '{base_command}' is blocked for security"
        
        # Check for dangerous patterns in the full command
        command_lower = command.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern in command_lower:
                return False, f"Command contains dangerous pattern: '{pattern}'"
        
        # For now, allow all other commands (can be made more restrictive)
        return True, "Command approved"

class ShellService:
    """
    Service for managing shell sessions and command execution.
    
    Provides secure, real-time shell access with proper session management,
    security controls, and output streaming capabilities.
    """
    
    def __init__(self):
        self.sessions: Dict[str, ShellSession] = {}
        self.security_manager = ShellSecurityManager()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_started = False
        
        # Get base directory from environment
        env_vars = env_manager.load_env_file()
        self.base_directory = os.path.abspath(env_vars.get("CODE_PATH", "."))
        
        logger.info(f"ShellService initialized with base directory: {self.base_directory}")
    
    def _start_cleanup_task(self):
        """Start the background cleanup task."""
        if not self._cleanup_started and (self._cleanup_task is None or self._cleanup_task.done()):
            try:
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
                self._cleanup_started = True
            except RuntimeError:
                # No event loop running yet, will start when needed
                pass
    
    async def _cleanup_loop(self):
        """Background task to clean up inactive sessions."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                current_time = time.time()
                
                # Find sessions to clean up (inactive for more than 30 minutes)
                sessions_to_remove = []
                for session_id, session in self.sessions.items():
                    if (current_time - session.last_activity) > 1800:  # 30 minutes
                        sessions_to_remove.append(session_id)
                
                # Clean up old sessions
                for session_id in sessions_to_remove:
                    await self.close_session(session_id)
                    logger.info(f"Cleaned up inactive session: {session_id}")
                    
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def create_session(self, working_directory: Optional[str] = None, shell_type: str = "auto") -> str:
        """
        Create a new shell session.
        
        Args:
            working_directory: Optional custom working directory
            shell_type: Shell type ("auto", "cmd", "powershell", "bash")
            
        Returns:
            str: Session ID
        """
        # Start cleanup task if not already started
        if not self._cleanup_started:
            self._start_cleanup_task()
            
        session_id = str(uuid.uuid4())
        
        # Validate and set working directory
        if working_directory:
            # Normalize path and ensure it's within base directory
            abs_path = os.path.abspath(working_directory)
            if not abs_path.startswith(self.base_directory):
                working_directory = self.base_directory
                logger.warning(f"Working directory outside base, using: {working_directory}")
            else:
                working_directory = abs_path
        else:
            working_directory = self.base_directory
        
        # Ensure directory exists
        if not os.path.exists(working_directory):
            working_directory = self.base_directory
            logger.warning(f"Working directory doesn't exist, using: {working_directory}")
        
        # Determine shell type
        if shell_type == "auto":
            if os.name == 'nt':  # Windows
                shell_type = "cmd"  # Default to cmd on Windows
            else:
                shell_type = "bash"  # Default to bash on Unix
        
        session = ShellSession(
            id=session_id,
            process=None,
            working_directory=working_directory,
            shell_type=shell_type,
            created_at=time.time(),
            last_activity=time.time()
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created shell session {session_id} in {working_directory}")
        
        return session_id
    
    async def execute_command(
        self, 
        session_id: str, 
        command: str,
        output_callback: Callable[[str, str], None]  # (data, stream_type)
    ) -> CommandStatus:
        """
        Execute a command in the specified session.
        
        Args:
            session_id: Session identifier
            command: Command to execute
            output_callback: Function to call with output data
            
        Returns:
            CommandStatus: Final status of command execution
        """
        if session_id not in self.sessions:
            await output_callback("Error: Session not found\n", "stderr")
            return CommandStatus.FAILED
        
        session = self.sessions[session_id]
        session.last_activity = time.time()
        session.command_count += 1
        
        # Security check
        is_safe, reason = self.security_manager.is_command_safe(command)
        if not is_safe:
            error_msg = f"Command blocked: {reason}\n"
            await output_callback(error_msg, "stderr")
            logger.warning(f"Blocked unsafe command in session {session_id}: {command}")
            return CommandStatus.FAILED
        
        try:
            # Determine shell command based on session shell type
            if session.shell_type == "cmd":
                shell_cmd = ['cmd', '/c', command]
            elif session.shell_type == "powershell":
                shell_cmd = ['powershell', '-Command', command]
            elif session.shell_type == "bash":
                shell_cmd = ['bash', '-c', command]
            else:
                # Fallback based on platform
                if os.name == 'nt':  # Windows
                    shell_cmd = ['cmd', '/c', command]
                else:  # Unix/Linux/macOS
                    shell_cmd = ['bash', '-c', command]
            
            # Start the process
            process = await asyncio.create_subprocess_exec(
                *shell_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session.working_directory,
                env=os.environ.copy()
            )
            
            session.process = process
            logger.info(f"Executing command in session {session_id}: {command}")
            
            # Create tasks to read stdout and stderr concurrently
            async def read_stream(stream, stream_type):
                try:
                    while True:
                        data = await stream.read(1024)
                        if not data:
                            break
                        text = data.decode('utf-8', errors='replace')
                        await output_callback(text, stream_type)
                except Exception as e:
                    logger.error(f"Error reading {stream_type}: {e}")
            
            # Wait for process completion with timeout
            stdout_task = asyncio.create_task(read_stream(process.stdout, "stdout"))
            stderr_task = asyncio.create_task(read_stream(process.stderr, "stderr"))
            
            try:
                # Wait for process with 5 minute timeout
                await asyncio.wait_for(process.wait(), timeout=300)
                
                # Ensure all output is read
                await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)
                
                if process.returncode == 0:
                    return CommandStatus.COMPLETED
                else:
                    return CommandStatus.FAILED
                    
            except asyncio.TimeoutError:
                logger.warning(f"Command timeout in session {session_id}: {command}")
                process.kill()
                await output_callback("\nCommand timed out and was terminated.\n", "stderr")
                return CommandStatus.TIMEOUT
                
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}\n"
            await output_callback(error_msg, "stderr")
            logger.error(f"Command execution error in session {session_id}: {e}")
            return CommandStatus.FAILED
        
        finally:
            session.process = None
    
    async def close_session(self, session_id: str) -> bool:
        """
        Close and clean up a shell session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session was closed successfully
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Kill any running process
        if session.process and session.process.returncode is None:
            try:
                session.process.kill()
                await session.process.wait()
            except Exception as e:
                logger.error(f"Error killing process in session {session_id}: {e}")
        
        # Remove session
        del self.sessions[session_id]
        logger.info(f"Closed shell session {session_id}")
        
        return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            "id": session.id,
            "working_directory": session.working_directory,
            "shell_type": session.shell_type,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "is_active": session.is_active,
            "command_count": session.command_count,
            "has_running_process": session.process is not None
        }
    
    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """List all active sessions."""
        return {sid: self.get_session_info(sid) for sid in self.sessions.keys()}

# Global shell service instance
shell_service = ShellService()