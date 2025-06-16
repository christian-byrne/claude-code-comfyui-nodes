import os
from typing import Tuple


class ClaudeCodeMemory:
    """
    Create and manage memory/context for Claude Code commands.
    This node helps build CLAUDE.md-style memory from various sources.
    """
    
    CATEGORY = "claude_code/helpers"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "memory_type": (["text", "file", "claude_md", "combined"], {
                    "default": "text",
                    "tooltip": "Type of memory input"
                }),
            },
            "optional": {
                "text_memory": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Direct text input for memory/context"
                }),
                "file_path": ("STRING", {
                    "default": "",
                    "tooltip": "Path to a file containing memory (e.g., CLAUDE.md)"
                }),
                "claude_md_content": ("STRING", {
                    "multiline": True,
                    "default": "# Project Context\n\n",
                    "tooltip": "CLAUDE.md formatted content"
                }),
                "append_to": ("CLAUDE_MEMORY", {
                    "tooltip": "Previous memory to append to"
                }),
            }
        }
    
    RETURN_TYPES = ("CLAUDE_MEMORY", "STRING")
    RETURN_NAMES = ("memory", "memory_text")
    DESCRIPTION = "Build memory/context for Claude Code commands from various sources"
    FUNCTION = "build_memory"
    
    OUTPUT_NODE = False
    
    def build_memory(
        self,
        memory_type: str,
        text_memory: str = "",
        file_path: str = "",
        claude_md_content: str = "",
        append_to: str = "",
    ) -> Tuple[str, str]:
        """Build memory from various sources."""
        
        memory_parts = []
        
        # Start with previous memory if provided
        if append_to:
            memory_parts.append(append_to)
            memory_parts.append("\n\n")
        
        # Add memory based on type
        if memory_type == "text":
            if text_memory:
                memory_parts.append(text_memory)
        
        elif memory_type == "file":
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    memory_parts.append(content)
                except Exception as e:
                    memory_parts.append(f"Error reading file {file_path}: {str(e)}")
            elif file_path:
                memory_parts.append(f"Error: File not found: {file_path}")
        
        elif memory_type == "claude_md":
            if claude_md_content:
                memory_parts.append(claude_md_content)
        
        elif memory_type == "combined":
            # Combine all available sources
            if claude_md_content:
                memory_parts.append(claude_md_content)
                memory_parts.append("\n\n")
            
            if text_memory:
                memory_parts.append("## Additional Context\n\n")
                memory_parts.append(text_memory)
                memory_parts.append("\n\n")
            
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    memory_parts.append("## File Content\n\n")
                    memory_parts.append(content)
                except Exception as e:
                    memory_parts.append(f"Error reading file: {str(e)}")
        
        memory = "".join(memory_parts).strip()
        
        # Return both as custom type and string for compatibility
        return (memory, memory)