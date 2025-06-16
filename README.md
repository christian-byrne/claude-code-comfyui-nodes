# Claude Code ComfyUI Nodes

ComfyUI nodes for integrating Claude Code SDK - enables AI-powered code generation, analysis, and assistance within ComfyUI workflows.

## Overview

This node pack provides a stateless, command-based interface to Claude Code within ComfyUI. Unlike traditional chat interfaces, these nodes operate as single-shot commands, making them perfect for automation workflows similar to n8n, Zapier, or Make.

## Key Features

- **Stateless Command Execution**: Each node execution is independent, with explicit memory/context passing
- **Folder-Based Output Management**: All outputs are organized in timestamped folders
- **Context Chaining**: Convert previous outputs into memory for subsequent commands
- **Argument Substitution**: Use variables in commands and memory (e.g., `${PROJECT_NAME}`)
- **Tool Control**: Fine-grained control over which tools Claude can use

## Nodes

### 1. Claude Code Command

The main execution node that runs Claude Code commands.

**Inputs:**
- `command`: The instruction/command for Claude to execute
- `model`: Choose between "sonnet" or "opus" models
- `max_turns`: Maximum iterations Claude can take (1-10)
- `memory`: Optional context/memory (like CLAUDE.md content)
- `arguments`: JSON object for variable substitution
- `previous_output_folder`: Link to previous command's output
- `allowed_tools`: Comma-separated list of allowed tools

**Outputs:**
- `output_folder`: Name of the folder containing all generated files
- `claude_response`: Claude's final response text
- `session_id`: Session ID for potential continuations
- `execution_metadata`: JSON metadata about the execution

### 2. Claude Code Reader

Inspect and read files from Claude Code output folders.

**Inputs:**
- `output_folder`: Folder name from a ClaudeCodeCommand
- `file_pattern`: Glob pattern for files (e.g., "*.py")
- `read_mode`: "list_files", "read_all", or "read_specific"
- `specific_file`: File to read in "read_specific" mode
- `max_files`: Maximum files to read

**Outputs:**
- `file_contents`: The actual file contents
- `file_list`: JSON list of files with metadata
- `metadata`: Execution metadata from the folder

### 3. Claude Code Context Builder

Convert output folders into memory/context for chaining commands.

**Inputs:**
- `output_folder`: Folder to build context from
- `context_mode`: How to build context ("full_content", "file_list", "summary", "custom")
- `base_memory`: Existing memory to append to
- `file_filter`: File extensions to include
- `custom_template`: Custom context template
- `max_file_size_kb`: Max file size to include

**Outputs:**
- `memory`: Formatted memory/context string

## Installation

1. Ensure you have ComfyUI installed
2. Clone this repository into your `ComfyUI/custom_nodes` directory
3. Choose your setup:

### Option A: Claude Code Max Plan (Recommended)
If you have a Claude Code Max Plan subscription:
- Install Claude Code from https://claude.ai/code
- The "Claude Code Command (Max Plan)" node will use your existing subscription
- No API key needed, no per-token costs

### Option B: Developer API
If you want to use the Anthropic API directly:
- Install dependencies: `pip install claude-code-sdk aiofiles`
- Set your `ANTHROPIC_API_KEY` environment variable
- Use the "Claude Code Command (API)" node
- Pay per token based on API usage

4. Restart ComfyUI

## Usage Examples

### Basic Command Execution

1. Add a "Claude Code Command" node
2. Enter your command, e.g.:
   ```markdown
   Create a Python script that generates fibonacci numbers.
   Include error handling and type hints.
   ```
3. Set model to "sonnet" and max_turns to 3
4. Execute the workflow
5. Check the output folder for generated files

### Chaining Commands

1. First command generates code
2. Connect output_folder to a "Claude Code Context Builder"
3. Connect the memory output to a second "Claude Code Command"
4. The second command can reference and build upon the first

### Using Arguments

Set arguments as JSON:
```json
{
  "PROJECT_NAME": "MyAwesomeProject",
  "LANGUAGE": "Python"
}
```

Then use in your command:
```markdown
Create a ${LANGUAGE} project structure for ${PROJECT_NAME}.
Include README, tests, and proper package structure.
```

## Output Organization

All outputs are stored in `claude_code_outputs/` with the structure:
```
claude_code_outputs/
├── output_20240615_143022_a1b2c3d4/
│   ├── _claude_code_metadata.json
│   ├── generated_script.py
│   └── README.md
└── output_20240615_144512_e5f6g7h8/
    ├── _claude_code_metadata.json
    └── refactored_code.py
```

## Best Practices

1. **Be Specific**: Clear, detailed commands produce better results
2. **Use Context**: Chain commands together for complex workflows
3. **Manage Tools**: Only enable tools that are needed for security
4. **Check Outputs**: Use the Reader node to verify generated content
5. **Template Commands**: Save frequently used commands as text files

## License

GNU General Public License v3