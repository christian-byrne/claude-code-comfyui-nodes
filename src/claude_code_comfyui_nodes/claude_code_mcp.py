import json
import subprocess
from typing import Tuple, List, Dict, Any


class ClaudeCodeMCP:
    """
    Configure MCP (Model Context Protocol) servers for Claude Code.
    Allows listing, enabling, and configuring MCP servers.
    """
    
    CATEGORY = "claude_code/helpers"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "action": (["list", "enable", "disable", "config"], {
                    "default": "list",
                    "tooltip": "MCP action to perform"
                }),
            },
            "optional": {
                "mcp_name": ("STRING", {
                    "default": "",
                    "tooltip": "Name of the MCP server"
                }),
                "mcp_config": ("STRING", {
                    "multiline": True,
                    "default": '{}',
                    "tooltip": "MCP configuration (JSON)"
                }),
                "list_format": (["names", "full", "json"], {
                    "default": "names",
                    "tooltip": "Format for listing MCPs"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "MCP_CONFIG", "JSON")
    RETURN_NAMES = ("mcp_info", "mcp_config", "mcp_data")
    DESCRIPTION = "Configure MCP servers for Claude Code"
    FUNCTION = "manage_mcp"
    
    OUTPUT_NODE = False
    
    def get_mcp_list(self) -> List[Dict[str, Any]]:
        """Get list of configured MCPs."""
        try:
            result = subprocess.run(
                ["claude", "mcp", "list", "--json"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return []
        except Exception:
            return []
    
    def manage_mcp(
        self,
        action: str,
        mcp_name: str = "",
        mcp_config: str = '{}',
        list_format: str = "names",
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        """Manage MCP servers."""
        
        if action == "list":
            mcp_list = self.get_mcp_list()
            
            if list_format == "names":
                # Just return names
                names = [mcp.get("name", "") for mcp in mcp_list]
                info = "Configured MCPs:\n" + "\n".join(f"- {name}" for name in names)
            elif list_format == "full":
                # Return detailed info
                info_parts = ["Configured MCPs:"]
                for mcp in mcp_list:
                    info_parts.append(f"\n- {mcp.get('name', 'Unknown')}")
                    info_parts.append(f"  Command: {mcp.get('command', 'N/A')}")
                    if mcp.get('args'):
                        info_parts.append(f"  Args: {' '.join(mcp.get('args', []))}")
                info = "\n".join(info_parts)
            else:  # json
                info = json.dumps(mcp_list, indent=2)
            
            return (info, "listed", mcp_list)
        
        elif action == "enable":
            if not mcp_name:
                return ("Error: MCP name required", "error", [])
            
            try:
                # Parse config
                config_dict = json.loads(mcp_config) if mcp_config else {}
                
                # Build command
                cmd = ["claude", "mcp", "add-json", "--scope", "user", mcp_name, json.dumps(config_dict)]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                
                if result.returncode == 0:
                    return (f"Successfully enabled MCP: {mcp_name}", f"enabled:{mcp_name}", self.get_mcp_list())
                else:
                    return (f"Error enabling MCP: {result.stderr}", "error", [])
                    
            except json.JSONDecodeError:
                return ("Error: Invalid JSON configuration", "error", [])
            except Exception as e:
                return (f"Error: {str(e)}", "error", [])
        
        elif action == "disable":
            if not mcp_name:
                return ("Error: MCP name required", "error", [])
            
            try:
                cmd = ["claude", "mcp", "remove", "--scope", "user", mcp_name]
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                
                if result.returncode == 0:
                    return (f"Successfully disabled MCP: {mcp_name}", f"disabled:{mcp_name}", self.get_mcp_list())
                else:
                    return (f"Error disabling MCP: {result.stderr}", "error", [])
                    
            except Exception as e:
                return (f"Error: {str(e)}", "error", [])
        
        elif action == "config":
            # Return example configurations
            examples = {
                "slack": {
                    "command": "npx",
                    "args": ["-y", "slack-mcp-server@latest", "--transport", "stdio"],
                    "env": {
                        "SLACK_MCP_XOXC_TOKEN": "your-xoxc-token",
                        "SLACK_MCP_XOXD_TOKEN": "your-xoxd-token"
                    }
                },
                "browser-tools": {
                    "command": "browser-tools-mcp"
                },
                "notion": {
                    "command": "notion-mcp-server",
                    "env": {
                        "NOTION_TOKEN": "your-notion-token"
                    }
                },
                "figma": {
                    "command": "figma-developer-mcp",
                    "args": ["--figma-api-key=your-api-key", "--stdio"]
                }
            }
            
            info = "Example MCP Configurations:\n\n"
            info += json.dumps(examples, indent=2)
            
            return (info, "config", [examples])
        
        return ("Unknown action", "error", [])