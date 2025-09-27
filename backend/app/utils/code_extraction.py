"""
Code extraction utilities for processing AI responses.

This module provides comprehensive code block extraction from AI response text,
matching the exact implementation patterns used in web1 for consistency.
It supports both Markdown fenced code blocks and HTML code elements as fallback.

Key Features:
- Regex-based Markdown fenced code block extraction (```lang\\n...\\n```)
- HTML <pre><code> element parsing as fallback
- Automatic programming language detection
- Code preview generation (first 3 lines)
- Filename generation with appropriate extensions
- HTML entity decoding for clean code content
- Empty block filtering to avoid noise

Pattern Matching:
- Primary: Markdown fenced blocks using /```(\\w+)?\\n([\\s\\S]*?)\\n```/g
- Fallback: HTML <pre><code class="language-xxx"> elements
- Language detection for unlabeled blocks using keyword analysis

This module ensures consistency with web1's code parsing behavior while
providing enhanced functionality for the v2 backend.
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from .language_detection import detect_language, generate_filename


def extract_code_blocks_from_content(content: str, message_id: str) -> List[Dict[str, Any]]:
    """
    Extract code blocks from text content using regex patterns.
    
    This function matches the web1 implementation exactly, supporting both
    Markdown fenced code blocks and HTML code elements as fallback.
    
    Args:
        content: The text content to extract code from
        message_id: Unique identifier for the message (used in block IDs)
        
    Returns:
        List[Dict]: List of extracted code blocks with metadata
    """
    code_blocks = []
    
    # Primary pattern: Markdown fenced code blocks (matching web1's approach)
    # Pattern: ```(\w+)?\n([\s\S]*?)\n``` 
    fenced_pattern = r'```(\w+)?\n([\s\S]*?)\n```'
    matches = re.findall(fenced_pattern, content)
    
    for i, (language, code) in enumerate(matches):
        if code.strip():  # Only include non-empty code blocks
            # Clean up the code content (trim whitespace)
            clean_code = code.strip()
            
            # Detect language if not specified
            if not language:
                language = detect_language(clean_code)
            
            # Generate filename based on language
            filename = generate_filename(language or "text", i + 1)
            
            # Create preview (first 3 lines, matching web1)
            lines = clean_code.split('\n')
            preview_lines = lines[:3]
            preview = '\n'.join(preview_lines)
            if len(lines) > 3:
                preview += '\n...'
            
            code_block = {
                "id": f"code-{message_id}-{i + 1}",
                "language": language or "text",
                "code": clean_code,
                "filename": filename,
                "preview": preview,
                "extractedAt": datetime.now().isoformat(),
                "lineCount": len(lines),
                "source": "markdown"
            }
            code_blocks.append(code_block)
    
    # If no markdown blocks found, try HTML fallback (matching web1's fallback approach)
    if len(code_blocks) == 0:
        html_pattern = r'<pre><code(?:\s+class="language-(\w+)")?>([\s\S]*?)</code></pre>'
        html_matches = re.findall(html_pattern, content, re.IGNORECASE)
        
        for i, (language, code) in enumerate(html_matches):
            if code.strip():
                # Clean up HTML entities
                clean_code = clean_html_entities(code.strip())
                
                if not language:
                    language = detect_language(clean_code)
                
                filename = generate_filename(language or "text", i + 1)
                
                # Create preview
                lines = clean_code.split('\n')
                preview_lines = lines[:3]
                preview = '\n'.join(preview_lines)
                if len(lines) > 3:
                    preview += '\n...'
                
                code_block = {
                    "id": f"html-code-{message_id}-{i + 1}",
                    "language": language or "text",
                    "code": clean_code,
                    "filename": filename,
                    "preview": preview,
                    "extractedAt": datetime.now().isoformat(),
                    "lineCount": len(lines),
                    "source": "html"
                }
                code_blocks.append(code_block)
    
    return code_blocks


def clean_html_entities(text: str) -> str:
    """
    Clean up common HTML entities in text content.
    
    Args:
        text: Text content with potential HTML entities
        
    Returns:
        str: Text with HTML entities decoded
    """
    return (text
            .replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&amp;', '&')
            .replace('&quot;', '"')
            .replace('&#39;', "'")
            .replace('&nbsp;', ' '))


def find_message_content(message_id: str, conversation_manager) -> Optional[str]:
    """
    Find message content by ID in conversation history.
    
    Args:
        message_id: The message ID to search for
        conversation_manager: The conversation manager instance
        
    Returns:
        Optional[str]: The message content if found, None otherwise
    """
    for session_id, session in conversation_manager._sessions.items():
        summary = session.get_summary()
        for entry in summary.conversation_history:
            if f"msg-{session_id}" in message_id and entry.role == "assistant":
                return entry.content
    return None


def create_code_preview(code: str, max_lines: int = 3) -> str:
    """
    Create a preview of code content showing first few lines.
    
    Args:
        code: The code content
        max_lines: Maximum number of lines to include in preview
        
    Returns:
        str: Code preview with ellipsis if truncated
    """
    lines = code.split('\n')
    preview_lines = lines[:max_lines]
    preview = '\n'.join(preview_lines)
    
    if len(lines) > max_lines:
        preview += '\n...'
    
    return preview