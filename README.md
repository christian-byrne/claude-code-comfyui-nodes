# Claude Code ComfyUI Nodes

ComfyUI nodes for integrating Claude Code SDK - enables AI-powered code generation, analysis, and assistance within ComfyUI workflows.

![Claude Code ComfyUI Nodes](https://github.com/user-attachments/assets/a62f5c4a-29f8-47e2-be2f-38868aaa7689)

## Overview

This node pack provides a stateless, command-based interface to Claude Code within ComfyUI. Unlike traditional chat interfaces, these nodes operate as single-shot commands, making them perfect for automation workflows similar to n8n, Zapier, or Make.

## Key Features

- **Stateless Command Execution**: Each node execution is independent, with explicit memory/context passing
- **Folder-Based Output Management**: All outputs are organized in timestamped folders
- **Context Chaining**: Convert previous outputs into memory for subsequent commands
- **Argument Substitution**: Use variables in commands and memory (e.g., `${PROJECT_NAME}`)
- **Tool Control**: Fine-grained control over which tools Claude can use
- **Command Library**: Pre-built commands in dropdown menu for common tasks
- **Memory Templates**: Reusable context files for consistent workflows

## Nodes

### 1. Claude Code Execute

The main execution node that runs Claude Code commands.

**Inputs:**
- `command_source`: Choose between "file" (dropdown) or "text" (custom)
- `command_file`: Dropdown of commands from `/commands` folder
- `command`: Custom command text (when not using file)
- `model`: Choose between "default", "sonnet" or "opus" models
- `max_turns`: Maximum iterations Claude can take (1-512)
- `memory`: Optional context from Memory Builder node
- `arguments`: Arguments from Arguments Builder node
- `tools`: Tool configuration from Tools Config node
- `previous_output`: Output from previous execution
- `mcp_config`: MCP configuration from MCP Manager

**Outputs:**
- `output`: CLAUDE_OUTPUT for chaining
- `response`: Claude's final response text
- `metadata`: JSON metadata about the execution

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

### 4. Claude Memory Builder

Build memory/context from various sources including dropdown selection.

**Inputs:**
- `memory_type`: "text", "file", "memory_file", "claude_md", or "combined"
- `memory_file`: Dropdown of files from `/memories` folder
- `text_memory`: Direct text input
- `file_path`: Path to any file
- `claude_md_content`: CLAUDE.md formatted content
- `append_to`: Previous memory to append to

**Outputs:**
- `memory`: CLAUDE_MEMORY for chaining
- `memory_text`: Plain text version

### 5. Claude Arguments Builder

Build arguments for variable substitution in commands.

**Inputs:**
- `arguments`: JSON object with key-value pairs
- `append_to`: Previous arguments to merge with

**Outputs:**
- `arguments`: CLAUDE_ARGUMENTS for chaining
- `arguments_json`: JSON string

### 6. Claude Tools Config

Configure which tools Claude can use.

**Inputs:**
- `preset`: Tool presets (all, read_only, file_ops, code_dev, web, minimal, none)
- `custom_tools`: Additional tools to add
- `remove_tools`: Tools to remove from preset
- Various boolean toggles for tool categories
- `skip_permissions`: Skip permission prompts

**Outputs:**
- `tools`: CLAUDE_TOOLS configuration
- `tools_list`: Comma-separated tool list
- `skip_permissions`: Boolean flag

### 7. Claude MCP Manager

Configure Model Context Protocol servers.

**Inputs:**
- `action`: list, enable, disable, or config
- `mcp_name`: Name of MCP server
- `mcp_config`: JSON configuration
- `list_format`: Output format for listing

**Outputs:**
- `mcp_info`: Status information
- `mcp_config`: MCP_CONFIG for chaining
- `mcp_data`: Raw MCP data

### 8. Claude Reddit Scraper

Scrape Reddit posts and comments using Playwright MCP.

**Inputs:**
- `source_type`: url, subreddit, search, or user
- `source`: Reddit URL or search term
- `scrape_mode`: comments, posts, both, or metadata
- `max_items`: Maximum items to scrape
- `sort_by`: Sort order for posts
- `include_metadata`: Include detailed metadata
- `max_comment_depth`: Thread depth to scrape

**Outputs:**
- `output`: CLAUDE_OUTPUT for chaining
- `scraped_data`: JSON data
- `summary`: Text summary
- `item_count`: Number of items scraped

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

1. Add a "Claude Code Execute" node
2. Set `command_source` to "file" and select a command from dropdown
   OR set to "text" and enter custom command:
   ```markdown
   Create a Python script that generates fibonacci numbers.
   Include error handling and type hints.
   ```
3. Set model to "sonnet" and max_turns to 8
4. Execute the workflow
5. Check the output folder for generated files

### Using Command and Memory Files

1. Place command files in `/commands` folder (`.md` or `.txt`)
2. Place memory/context files in `/memories` folder
3. Use dropdowns in Execute and Memory Builder nodes
4. Combine with Arguments Builder for dynamic values

### Reddit to Video Workflow

1. Add "Claude Reddit Scraper" node
   - Set source to "programming" 
   - Set scrape_mode to "comments"
2. Connect output to "Claude Code Execute" node
3. Select "reddit-video-script-simple.md" from command dropdown
4. Execute to generate TikTok/YouTube script

### Chaining Commands

1. First Execute node generates code
2. Connect output to "Claude Code Context Builder"
3. Connect memory output to second Execute node
4. Second command references and builds upon the first

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

## Folder Structure

```
claude-code-comfyui-nodes/
├── commands/                    # Command library (dropdown in Execute node)
│   ├── reddit-video-script-simple.md
│   └── your-custom-command.md
├── memories/                    # Memory templates (dropdown in Memory node)
│   ├── reddit-video-context.md
│   └── your-project-context.md
├── claude_code_outputs/         # All execution outputs
│   ├── output_20240615_143022/
│   └── reddit_scrape_20240615/
└── src/                        # Node implementations
```

## Output Organization

All outputs are stored in `claude_code_outputs/` with timestamped folders:
- Execute node: `output_YYYYMMDD_HHMMSS_[id]`
- Reddit scraper: `reddit_scrape_YYYYMMDD_HHMMSS_[id]`
- Each folder contains generated files and `_claude_code_metadata.json`

## Best Practices

1. **Be Specific**: Clear, detailed commands produce better results
2. **Use Context**: Chain commands together for complex workflows
3. **Manage Tools**: Only enable tools that are needed for security
4. **Check Outputs**: Use the Reader node to verify generated content
5. **Template Commands**: Save frequently used commands as text files

## License

GNU General Public License v3