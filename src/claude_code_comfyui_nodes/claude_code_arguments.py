import json
from typing import Tuple, Dict, Any


class ClaudeCodeArguments:
    """
    Build arguments for variable substitution in Claude Code commands.
    Supports JSON input, key-value pairs, and merging multiple argument sets.
    """
    
    CATEGORY = "claude_code/helpers"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_mode": (["json", "key_value", "merge"], {
                    "default": "json",
                    "tooltip": "How to input arguments"
                }),
            },
            "optional": {
                "json_arguments": ("STRING", {
                    "multiline": True,
                    "default": '{\n  "PROJECT_NAME": "MyProject",\n  "LANGUAGE": "Python"\n}',
                    "tooltip": "JSON object with argument key-value pairs"
                }),
                "key": ("STRING", {
                    "default": "",
                    "tooltip": "Argument key (for key_value mode)"
                }),
                "value": ("STRING", {
                    "default": "",
                    "tooltip": "Argument value (for key_value mode)"
                }),
                "base_arguments": ("CLAUDE_ARGUMENTS", {
                    "tooltip": "Base arguments to merge with"
                }),
                "merge_arguments": ("CLAUDE_ARGUMENTS", {
                    "tooltip": "Arguments to merge (for merge mode)"
                }),
            }
        }
    
    RETURN_TYPES = ("CLAUDE_ARGUMENTS", "STRING")
    RETURN_NAMES = ("arguments", "arguments_json")
    DESCRIPTION = "Build arguments for variable substitution in Claude Code commands"
    FUNCTION = "build_arguments"
    
    OUTPUT_NODE = False
    
    def build_arguments(
        self,
        input_mode: str,
        json_arguments: str = '{}',
        key: str = "",
        value: str = "",
        base_arguments: str = '{}',
        merge_arguments: str = '{}',
    ) -> Tuple[str, str]:
        """Build arguments dictionary."""
        
        # Parse base arguments if provided
        try:
            base_dict = json.loads(base_arguments) if base_arguments else {}
        except json.JSONDecodeError:
            base_dict = {}
        
        result_dict = base_dict.copy()
        
        if input_mode == "json":
            try:
                args_dict = json.loads(json_arguments)
                if isinstance(args_dict, dict):
                    result_dict.update(args_dict)
            except json.JSONDecodeError as e:
                # Return error as arguments
                result_dict["_error"] = f"Invalid JSON: {str(e)}"
        
        elif input_mode == "key_value":
            if key:
                result_dict[key] = value
        
        elif input_mode == "merge":
            try:
                merge_dict = json.loads(merge_arguments) if merge_arguments else {}
                if isinstance(merge_dict, dict):
                    result_dict.update(merge_dict)
            except json.JSONDecodeError:
                pass
        
        # Convert back to JSON string
        result_json = json.dumps(result_dict, indent=2)
        
        return (result_json, result_json)