"""
Claude Code ComfyUI Nodes
"""

# Core execution nodes
from .claude_code_execute import ClaudeCodeExecute

# Helper/builder nodes
from .claude_code_memory import ClaudeCodeMemory
from .claude_code_arguments import ClaudeCodeArguments
from .claude_code_tools import ClaudeCodeTools
from .claude_code_mcp import ClaudeCodeMCP

# Utility nodes
from .claude_code_reader import ClaudeCodeReader
from .claude_code_context import ClaudeCodeContext

# Node class mappings
NODE_CLASS_MAPPINGS = {
    # Core nodes
    "ClaudeCodeExecute": ClaudeCodeExecute,
    
    # Helper nodes
    "ClaudeCodeMemory": ClaudeCodeMemory,
    "ClaudeCodeArguments": ClaudeCodeArguments,
    "ClaudeCodeTools": ClaudeCodeTools,
    "ClaudeCodeMCP": ClaudeCodeMCP,
    
    # Utility nodes
    "ClaudeCodeReader": ClaudeCodeReader,
    "ClaudeCodeContext": ClaudeCodeContext,
}

# Display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    # Core nodes
    "ClaudeCodeExecute": "Claude Code Execute",
    
    # Helper nodes
    "ClaudeCodeMemory": "Claude Memory Builder",
    "ClaudeCodeArguments": "Claude Arguments Builder",
    "ClaudeCodeTools": "Claude Tools Config",
    "ClaudeCodeMCP": "Claude MCP Manager",
    
    # Utility nodes
    "ClaudeCodeReader": "Claude Output Reader",
    "ClaudeCodeContext": "Claude Context Builder",
}