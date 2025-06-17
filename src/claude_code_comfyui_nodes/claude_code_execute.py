import os
import json
import uuid
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

try:
    from server import PromptServer
except ImportError:
    PromptServer = None


class ClaudeCodeExecute:
    """
    Execute Claude Code commands with modular configuration and progress reporting.
    """
    
    CATEGORY = "claude_code"
    
    @classmethod
    def get_command_files(cls):
        """Get list of command files from the commands folder."""
        commands_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "commands")
        command_files = ["[Custom Command]"]  # Option for custom text input
        
        if os.path.exists(commands_dir):
            for file in sorted(os.listdir(commands_dir)):
                if file.endswith('.md') or file.endswith('.txt'):
                    command_files.append(file)
        
        return command_files
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "command_source": (["file", "text"], {
                    "default": "file",
                    "tooltip": "Use command from file or custom text"
                }),
                "command_file": (cls.get_command_files(), {
                    "default": "[Custom Command]",
                    "tooltip": "Select a command file from the commands folder"
                }),
                "command": ("STRING", {
                    "multiline": True,
                    "default": "# Claude Code Command\n\nYour command instructions here...",
                    "tooltip": "Custom command (used when command_source is 'text' or file is '[Custom Command]')"
                }),
                "model": (["default", "sonnet", "opus"], {
                    "default": "default",
                    "tooltip": "Claude model to use"
                }),
                "max_turns": ("INT", {
                    "default": 8,
                    "min": 1,
                    "max": 512,
                    "tooltip": "Maximum number of turns Claude can take to complete the task"
                }),
            },
            "optional": {
                "memory": ("CLAUDE_MEMORY", {
                    "tooltip": "Memory/context from Claude Memory Builder"
                }),
                "arguments": ("CLAUDE_ARGUMENTS", {
                    "tooltip": "Arguments from Claude Arguments Builder"
                }),
                "tools": ("CLAUDE_TOOLS", {
                    "tooltip": "Tool configuration from Claude Tools Config"
                }),
                "previous_output": ("CLAUDE_OUTPUT", {
                    "tooltip": "Output from previous Claude Code execution"
                }),
                "mcp_config": ("MCP_CONFIG", {
                    "tooltip": "MCP configuration from Claude MCP Manager"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("CLAUDE_OUTPUT", "STRING", "JSON")
    RETURN_NAMES = ("output", "response", "metadata")
    DESCRIPTION = "Execute Claude Code with modular configuration and progress reporting"
    FUNCTION = "execute"
    
    OUTPUT_NODE = False
    
    def __init__(self):
        self.output_base_dir = os.path.join(os.getcwd(), "claude_code_outputs")
        os.makedirs(self.output_base_dir, exist_ok=True)
    
    def send_progress(self, message: str, unique_id: str):
        """Send progress update to UI."""
        if PromptServer and unique_id:
            PromptServer.instance.send_progress_text(message, unique_id)
    
    def replace_arguments(self, text: str, arguments: str) -> str:
        """Replace argument placeholders in text."""
        try:
            args_dict = json.loads(arguments) if arguments else {}
            for key, value in args_dict.items():
                placeholder = f"${{{key}}}"
                text = text.replace(placeholder, str(value))
        except json.JSONDecodeError:
            pass
        return text
    
    def generate_output_folder(self) -> Tuple[str, str]:
        """Generate unique output folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        folder_name = f"output_{timestamp}_{unique_id}"
        folder_path = os.path.join(self.output_base_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_name, folder_path
    
    def build_prompt(
        self,
        command: str,
        memory: str,
        output_folder: str,
        previous_output: str
    ) -> str:
        """Build the final prompt."""
        parts = []
        
        if memory:
            parts.append("# Context/Memory\n")
            parts.append(memory)
            parts.append("\n\n")
        
        if previous_output:
            prev_path = os.path.join(self.output_base_dir, previous_output)
            if os.path.exists(prev_path):
                parts.append("# Previous Output\n")
                parts.append(f"Previous execution created files in: {prev_path}")
                parts.append("Read and understand these files as context.\n\n")
        
        parts.append("# Command\n")
        parts.append(command)
        parts.append("\n\n")
        
        parts.append("# Output Instructions\n")
        parts.append(f"Create all output files in: {output_folder}")
        parts.append("\nDo not create files elsewhere.")
        
        return "".join(parts)
    
    def setup_mcps_from_config(self, mcp_config: str, unique_id: str) -> List[str]:
        """Setup MCP servers from MCP Manager node output."""
        errors = []
        
        if not mcp_config or not mcp_config.strip():
            return errors
        
        self.send_progress("Setting up MCPs...", unique_id)
        
        # Parse the MCP status
        if mcp_config.startswith("enabled:"):
            mcp_name = mcp_config.split(":", 1)[1]
            self.send_progress(f"MCP '{mcp_name}' is configured and ready", unique_id)
        elif mcp_config.startswith("disabled:"):
            mcp_name = mcp_config.split(":", 1)[1]
            errors.append(f"MCP '{mcp_name}' was disabled")
        elif "error" in mcp_config.lower():
            errors.append(f"MCP configuration error: {mcp_config}")
        
        return errors
    
    def load_command_from_file(self, command_file: str) -> str:
        """Load command from file in commands folder."""
        if command_file == "[Custom Command]":
            return None
            
        commands_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "commands")
        file_path = os.path.join(commands_dir, command_file)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading command file: {str(e)}"
        
        return None
    
    def execute(
        self,
        command_source: str,
        command_file: str,
        command: str,
        model: str,
        max_turns: int,
        memory: str = "",
        arguments: str = "{}",
        tools: str = "Read,Write,Edit,MultiEdit,Bash,Grep,Glob",
        previous_output: str = "",
        mcp_config: str = "",
        unique_id: str = "",
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Execute Claude Code command with progress reporting."""
        
        self.send_progress("Initializing Claude Code execution...", unique_id)
        
        # Load command from file if specified
        if command_source == "file" and command_file != "[Custom Command]":
            loaded_command = self.load_command_from_file(command_file)
            if loaded_command:
                command = loaded_command
                self.send_progress(f"Loaded command from: {command_file}", unique_id)
            else:
                self.send_progress(f"Failed to load command file, using custom command", unique_id)
        
        # Replace arguments in command and memory
        command = self.replace_arguments(command, arguments)
        memory = self.replace_arguments(memory, arguments) if memory else ""
        
        # Generate output folder
        folder_name, folder_path = self.generate_output_folder()
        self.send_progress(f"Created output folder: {folder_name}", unique_id)
        
        # Configure MCPs if specified
        mcp_setup_errors = []
        if mcp_config:
            mcp_setup_errors = self.setup_mcps_from_config(mcp_config, unique_id)
        
        # Build prompt
        self.send_progress("Building prompt...", unique_id)
        prompt = self.build_prompt(command, memory, folder_path, previous_output)
        
        # Build CLI command
        cmd_parts = ["claude", "-p", "--max-turns", str(max_turns)]
        
        if model != "default":
            cmd_parts.extend(["--model", model])
        
        # Parse tools and skip_permissions from tools config
        skip_permissions = False
        tool_list = []
        
        if tools:
            # Check if tools contains skip_permissions flag
            if "|skip_permissions:" in tools:
                tools_part, permissions_part = tools.split("|skip_permissions:")
                skip_permissions = permissions_part.lower() == "true"
                tools = tools_part
            
            tool_list = [tool.strip() for tool in tools.split(",") if tool.strip()]
            self.send_progress(f"Configuring tools: {', '.join(tool_list)}", unique_id)
            for tool in tool_list:
                cmd_parts.extend(["--allowedTools", tool])
        
        # Add skip permissions flag if enabled
        if skip_permissions:
            cmd_parts.append("--dangerously-skip-permissions")
            self.send_progress("⚠️  Skipping permission prompts", unique_id)
        
        # Execute
        self.send_progress("Executing Claude Code...", unique_id)
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                cmd_parts,
                input=prompt,
                cwd=folder_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Extract response
            if result.returncode == 0:
                response = result.stdout
                self.send_progress(f"✅ Execution completed successfully in {duration:.1f}s", unique_id)
            else:
                response = f"Error: {result.stderr}"
                self.send_progress(f"❌ Execution failed: {result.stderr}", unique_id)
            
            # Create metadata
            metadata = {
                "execution_time": duration,
                "model": model,
                "max_turns": max_turns,
                "output_folder": folder_name,
                "output_path": folder_path,
                "timestamp": start_time.isoformat(),
                "tools_used": tools.split(",") if tools else [],
                "exit_code": result.returncode,
                "has_memory": bool(memory),
                "has_arguments": arguments != "{}",
                "has_previous": bool(previous_output),
                "mcp_config_received": bool(mcp_config),
                "mcp_setup_errors": mcp_setup_errors,
            }
            
            # Save metadata and raw output
            self.send_progress("Saving execution metadata...", unique_id)
            
            with open(os.path.join(folder_path, "_claude_code_metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)
            
            if result.stdout:
                with open(os.path.join(folder_path, "_claude_raw_output.txt"), "w") as f:
                    f.write(result.stdout)
            
            if result.stderr:
                with open(os.path.join(folder_path, "_claude_raw_error.txt"), "w") as f:
                    f.write(result.stderr)
            
            # Check what files were created
            created_files = list(Path(folder_path).glob("*"))
            created_files = [f for f in created_files if not f.name.startswith("_claude_")]
            
            if created_files:
                file_list = ", ".join([f.name for f in created_files[:5]])
                if len(created_files) > 5:
                    file_list += f" and {len(created_files) - 5} more"
                self.send_progress(f"📁 Created files: {file_list}", unique_id)
            
            return (folder_name, response, metadata)
            
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            self.send_progress(f"❌ {error_msg}", unique_id)
            
            metadata = {
                "error": str(e),
                "execution_time": 0,
                "output_folder": folder_name,
                "timestamp": start_time.isoformat(),
            }
            return (folder_name, error_msg, metadata)