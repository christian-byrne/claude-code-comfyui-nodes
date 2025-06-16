from typing import Tuple, List


class ClaudeCodeTools:
    """
    Configure which tools Claude Code can use.
    Provides presets and custom tool selection.
    """
    
    CATEGORY = "claude_code/helpers"
    
    # Tool presets
    PRESETS = {
        "all": "Read,Write,Edit,MultiEdit,Bash,Grep,Glob,LS,WebFetch,WebSearch",
        "read_only": "Read,Grep,Glob,LS",
        "file_ops": "Read,Write,Edit,MultiEdit,Grep,Glob,LS",
        "code_dev": "Read,Write,Edit,MultiEdit,Bash,Grep,Glob,LS",
        "web": "WebFetch,WebSearch",
        "minimal": "Read,Write",
        "none": "",
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (list(cls.PRESETS.keys()), {
                    "default": "code_dev",
                    "tooltip": "Tool preset to use"
                }),
                "custom_tools": ("STRING", {
                    "default": "",
                    "tooltip": "Additional tools to add (comma-separated)"
                }),
                "remove_tools": ("STRING", {
                    "default": "",
                    "tooltip": "Tools to remove from preset (comma-separated)"
                }),
            },
            "optional": {
                "file_read": ("BOOLEAN", {"default": True}),
                "file_write": ("BOOLEAN", {"default": True}),
                "file_edit": ("BOOLEAN", {"default": True}),
                "bash": ("BOOLEAN", {"default": True}),
                "search": ("BOOLEAN", {"default": True}),
                "web": ("BOOLEAN", {"default": False}),
                "skip_permissions": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Skip permission prompts (adds --dangerously-skip-permissions)"
                }),
            }
        }
    
    RETURN_TYPES = ("CLAUDE_TOOLS", "STRING", "BOOLEAN")
    RETURN_NAMES = ("tools", "tools_list", "skip_permissions")
    DESCRIPTION = "Configure which tools Claude Code can use"
    FUNCTION = "configure_tools"
    
    OUTPUT_NODE = False
    
    def configure_tools(
        self,
        preset: str,
        custom_tools: str = "",
        remove_tools: str = "",
        file_read: bool = True,
        file_write: bool = True,
        file_edit: bool = True,
        bash: bool = True,
        search: bool = True,
        web: bool = False,
        skip_permissions: bool = False,
    ) -> Tuple[str, str, bool]:
        """Configure tool list."""
        
        # Start with preset
        tools_str = self.PRESETS.get(preset, "")
        tools_set = set(tool.strip() for tool in tools_str.split(",") if tool.strip())
        
        # Apply boolean toggles (only if using custom selection)
        if preset == "none":
            if file_read:
                tools_set.update(["Read", "LS"])
            if file_write:
                tools_set.add("Write")
            if file_edit:
                tools_set.update(["Edit", "MultiEdit"])
            if bash:
                tools_set.add("Bash")
            if search:
                tools_set.update(["Grep", "Glob"])
            if web:
                tools_set.update(["WebFetch", "WebSearch"])
        
        # Add custom tools
        if custom_tools:
            custom_set = set(tool.strip() for tool in custom_tools.split(",") if tool.strip())
            tools_set.update(custom_set)
        
        # Remove specified tools
        if remove_tools:
            remove_set = set(tool.strip() for tool in remove_tools.split(",") if tool.strip())
            tools_set.difference_update(remove_set)
        
        # Convert back to comma-separated string
        tools_list = sorted(list(tools_set))
        tools_str = ",".join(tools_list)
        
        # Include skip_permissions in the tools string for the Execute node
        tools_config = f"{tools_str}|skip_permissions:{skip_permissions}"
        return (tools_config, tools_str, skip_permissions)