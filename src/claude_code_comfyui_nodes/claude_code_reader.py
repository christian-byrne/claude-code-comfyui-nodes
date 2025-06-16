import os
import json
from typing import Any, Dict, List, Tuple


class ClaudeCodeReader:
    """
    Read and display contents from Claude Code output folders.
    Useful for inspecting what Claude generated.
    """
    
    CATEGORY = "claude_code"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_folder": ("STRING", {
                    "default": "",
                    "tooltip": "The output folder name from a ClaudeCodeCommand node"
                }),
                "file_pattern": ("STRING", {
                    "default": "*",
                    "tooltip": "File pattern to read (e.g., '*.py', 'README.md', '*')"
                }),
                "read_mode": (["list_files", "read_all", "read_specific"], {
                    "default": "list_files",
                    "tooltip": "Mode for reading files"
                }),
            },
            "optional": {
                "specific_file": ("STRING", {
                    "default": "",
                    "tooltip": "Specific file to read (when using read_specific mode)"
                }),
                "max_files": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 100,
                    "tooltip": "Maximum number of files to read"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "JSON", "STRING")
    RETURN_NAMES = ("file_contents", "file_list", "metadata")
    DESCRIPTION = "Read and inspect contents from Claude Code output folders"
    FUNCTION = "read_output"
    
    OUTPUT_NODE = True
    
    def __init__(self):
        self.output_base_dir = os.path.join(os.getcwd(), "claude_code_outputs")
    
    def read_output(
        self,
        output_folder: str,
        file_pattern: str,
        read_mode: str,
        specific_file: str = "",
        max_files: int = 10,
    ) -> Tuple[str, List[Dict[str, str]], str]:
        """Read files from the output folder."""
        
        folder_path = os.path.join(self.output_base_dir, output_folder)
        
        if not os.path.exists(folder_path):
            return (f"Error: Output folder '{output_folder}' not found", [], "")
        
        # Read metadata if it exists
        metadata = ""
        metadata_path = os.path.join(folder_path, "_claude_code_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = f.read()
        
        # Get list of files
        import glob
        pattern_path = os.path.join(folder_path, "**", file_pattern)
        files = glob.glob(pattern_path, recursive=True)
        
        # Filter out the metadata file
        files = [f for f in files if not f.endswith("_claude_code_metadata.json")]
        
        # Create file list
        file_list = []
        for file_path in files[:max_files]:
            rel_path = os.path.relpath(file_path, folder_path)
            file_info = {
                "path": rel_path,
                "size": os.path.getsize(file_path),
                "type": os.path.splitext(file_path)[1],
            }
            file_list.append(file_info)
        
        # Read file contents based on mode
        file_contents = ""
        
        if read_mode == "list_files":
            file_contents = f"Files in {output_folder}:\n"
            for info in file_list:
                file_contents += f"- {info['path']} ({info['size']} bytes)\n"
        
        elif read_mode == "read_all":
            contents_parts = []
            for file_path in files[:max_files]:
                rel_path = os.path.relpath(file_path, folder_path)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    contents_parts.append(f"=== {rel_path} ===\n{content}\n")
                except Exception as e:
                    contents_parts.append(f"=== {rel_path} ===\nError reading file: {e}\n")
            file_contents = "\n".join(contents_parts)
        
        elif read_mode == "read_specific" and specific_file:
            specific_path = os.path.join(folder_path, specific_file)
            if os.path.exists(specific_path):
                try:
                    with open(specific_path, "r", encoding="utf-8") as f:
                        file_contents = f.read()
                except Exception as e:
                    file_contents = f"Error reading file: {e}"
            else:
                file_contents = f"File '{specific_file}' not found in output folder"
        
        return (file_contents, file_list, metadata)