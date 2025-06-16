import os
import json
from typing import Any, Dict, List, Tuple
from pathlib import Path


class ClaudeCodeContext:
    """
    Build context/memory from Claude Code output folders.
    This node helps chain multiple Claude Code commands by converting
    previous outputs into memory for the next command.
    """
    
    CATEGORY = "claude_code"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_folder": ("STRING", {
                    "default": "",
                    "tooltip": "The output folder from a previous ClaudeCodeCommand"
                }),
                "context_mode": (["full_content", "file_list", "summary", "custom"], {
                    "default": "summary",
                    "tooltip": "How to build the context from the folder"
                }),
            },
            "optional": {
                "base_memory": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Base memory to append the folder context to"
                }),
                "file_filter": ("STRING", {
                    "default": "*.py,*.js,*.ts,*.md,*.txt,*.json",
                    "tooltip": "Comma-separated file extensions to include"
                }),
                "custom_template": ("STRING", {
                    "multiline": True,
                    "default": "# Previous Output\n\nThe following files were generated:\n{file_list}\n\nKey files:\n{file_contents}",
                    "tooltip": "Custom template for context (available vars: {file_list}, {file_contents}, {metadata})"
                }),
                "max_file_size_kb": ("INT", {
                    "default": 100,
                    "min": 1,
                    "max": 1000,
                    "tooltip": "Maximum file size in KB to include in full content"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("memory",)
    DESCRIPTION = "Convert Claude Code output folders into context/memory for subsequent commands"
    FUNCTION = "build_context"
    
    OUTPUT_NODE = False
    
    def __init__(self):
        self.output_base_dir = os.path.join(os.getcwd(), "claude_code_outputs")
    
    def build_context(
        self,
        output_folder: str,
        context_mode: str,
        base_memory: str = "",
        file_filter: str = "*.py,*.js,*.ts,*.md,*.txt,*.json",
        custom_template: str = "",
        max_file_size_kb: int = 100,
    ) -> Tuple[str]:
        """Build context from output folder."""
        
        # Handle empty output folder
        if not output_folder or not output_folder.strip():
            # Just return the base memory if no folder is provided
            return (base_memory if base_memory else "",)
        
        folder_path = os.path.join(self.output_base_dir, output_folder)
        
        if not os.path.exists(folder_path):
            return (f"Error: Output folder '{output_folder}' not found",)
        
        # Parse file filters
        extensions = [ext.strip() for ext in file_filter.split(",")]
        
        # Get all files matching filters
        all_files = []
        for ext in extensions:
            pattern = f"**/{ext}" if ext.startswith("*") else f"**/*.{ext}"
            files = list(Path(folder_path).glob(pattern))
            all_files.extend(files)
        
        # Remove duplicates and sort
        all_files = sorted(set(all_files))
        
        # Read metadata
        metadata_content = ""
        metadata_path = os.path.join(folder_path, "_claude_code_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                metadata_content = json.dumps(metadata, indent=2)
        
        # Build file list
        file_list_str = ""
        file_contents = {}
        
        for file_path in all_files:
            if file_path.name == "_claude_code_metadata.json":
                continue
                
            rel_path = file_path.relative_to(folder_path)
            file_size = file_path.stat().st_size
            
            file_list_str += f"- {rel_path} ({file_size} bytes)\n"
            
            # Read file content if it's not too large
            if file_size <= max_file_size_kb * 1024:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    file_contents[str(rel_path)] = content
                except Exception as e:
                    file_contents[str(rel_path)] = f"[Error reading file: {e}]"
            else:
                file_contents[str(rel_path)] = f"[File too large: {file_size} bytes]"
        
        # Build context based on mode
        context_parts = []
        
        if base_memory:
            context_parts.append(base_memory)
            context_parts.append("\n\n")
        
        if context_mode == "full_content":
            context_parts.append(f"# Files from {output_folder}\n\n")
            for rel_path, content in file_contents.items():
                context_parts.append(f"## {rel_path}\n\n```\n{content}\n```\n\n")
        
        elif context_mode == "file_list":
            context_parts.append(f"# Files created in {output_folder}\n\n")
            context_parts.append(file_list_str)
            context_parts.append("\n")
            if metadata_content:
                context_parts.append("## Execution Metadata\n\n```json\n")
                context_parts.append(metadata_content)
                context_parts.append("\n```\n")
        
        elif context_mode == "summary":
            context_parts.append(f"# Previous execution: {output_folder}\n\n")
            context_parts.append("## Files created:\n")
            context_parts.append(file_list_str)
            context_parts.append("\n")
            
            # Include key files (first few or specific important ones)
            key_files = list(file_contents.items())[:5]  # First 5 files
            if key_files:
                context_parts.append("## Key file contents:\n\n")
                for rel_path, content in key_files:
                    # Truncate large contents
                    if len(content) > 1000:
                        content = content[:1000] + "\n... [truncated]"
                    context_parts.append(f"### {rel_path}\n\n```\n{content}\n```\n\n")
        
        elif context_mode == "custom" and custom_template:
            # Build file contents string
            file_contents_str = ""
            for rel_path, content in list(file_contents.items())[:5]:
                file_contents_str += f"### {rel_path}\n\n```\n{content}\n```\n\n"
            
            # Replace template variables
            formatted = custom_template.replace("{file_list}", file_list_str)
            formatted = formatted.replace("{file_contents}", file_contents_str)
            formatted = formatted.replace("{metadata}", metadata_content)
            formatted = formatted.replace("{output_folder}", output_folder)
            
            context_parts.append(formatted)
        
        memory = "".join(context_parts)
        return (memory,)