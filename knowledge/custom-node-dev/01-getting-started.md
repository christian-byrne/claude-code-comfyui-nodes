# Getting Started with ComfyUI Custom Node Development

## Overview

Custom nodes in ComfyUI allow you to extend the functionality of the system by creating new nodes that can process data, apply effects, generate content, or integrate with external services. This guide will walk you through the fundamentals of custom node development.

## Prerequisites

Before you begin developing custom nodes, ensure you have:

1. **A working ComfyUI installation** - We recommend a manual installation for development work
2. **Python knowledge** - Custom nodes are written in Python, so basic Python understanding is essential
3. **comfy-cli installed** - The command-line tool for scaffolding and managing custom nodes
4. **A code editor** - VS Code, PyCharm, or any Python-friendly editor

## Quick Start: Your First Node

### 1. Scaffold a New Custom Node

Navigate to your ComfyUI custom_nodes directory and use comfy-cli to create a new node:

```bash
cd ComfyUI/custom_nodes
comfy node scaffold
```

Follow the prompts to configure your node package. This creates a complete project structure with all necessary files.

### 2. Basic Node Structure

Every custom node in ComfyUI follows this pattern:

```python
class MyCustomNode:
    """
    A custom node that does something useful
    """
    
    # Display name in the UI
    CATEGORY = "MyNodes/Examples"
    
    @classmethod
    def INPUT_TYPES(cls):
        """Define what inputs this node accepts"""
        return {
            "required": {
                "input_name": ("DATA_TYPE", {
                    "default": default_value,
                    "min": 0,
                    "max": 100
                }),
            },
            "optional": {
                "optional_input": ("DATA_TYPE", {}),
            }
        }
    
    # Define output types
    RETURN_TYPES = ("OUTPUT_TYPE",)
    RETURN_NAMES = ("output_name",)
    
    # Function name to call when node executes
    FUNCTION = "execute"
    
    # Node outputs results (not just passes data)
    OUTPUT_NODE = False
    
    def execute(self, input_name, optional_input=None):
        """Main processing function"""
        # Your processing logic here
        result = process_input(input_name)
        
        # Always return a tuple matching RETURN_TYPES
        return (result,)
```

### 3. Register Your Node

At the end of your module, register the node so ComfyUI can find it:

```python
NODE_CLASS_MAPPINGS = {
    "MyCustomNode": MyCustomNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MyCustomNode": "My Custom Node"
}
```

### 4. Test Your Node

1. Restart ComfyUI
2. Right-click in the UI and search for your node by name
3. Connect inputs and outputs to test functionality

## Core Concepts

### Data Types

ComfyUI uses specific data types for node inputs and outputs. Common types include:

- `IMAGE` - Image tensors (batch of images)
- `LATENT` - Latent space representations
- `CONDITIONING` - Text embeddings and conditioning data
- `MODEL` - AI models
- `CLIP` - CLIP text encoders
- `VAE` - Variational autoencoders
- `STRING`, `INT`, `FLOAT`, `BOOLEAN` - Basic types
- `*` - Special ANY type (use sparingly)

### Node Lifecycle

1. **Discovery** - ComfyUI scans custom_nodes folder on startup
2. **Import** - Python modules are imported
3. **Registration** - Nodes in NODE_CLASS_MAPPINGS are registered
4. **Instantiation** - Node instances created when added to workflow
5. **Execution** - Node's function called during workflow processing

### Input Configuration

The `INPUT_TYPES` method supports rich configuration:

```python
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            # Basic number input with constraints
            "threshold": ("FLOAT", {
                "default": 0.5,
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "display": "slider"
            }),
            
            # Dropdown selection
            "mode": (["option1", "option2", "option3"], {
                "default": "option1"
            }),
            
            # Multi-line text input
            "prompt": ("STRING", {
                "multiline": True,
                "default": "Enter text here"
            }),
        },
        "optional": {
            # Optional image input
            "mask": ("MASK", {}),
        },
        "hidden": {
            # Hidden inputs for internal use
            "unique_id": "UNIQUE_ID"
        }
    }
```

## Development Workflow

### 1. Plan Your Node

- What problem does it solve?
- What inputs does it need?
- What outputs should it produce?
- How does it fit into existing workflows?

### 2. Implement Core Logic

- Start with a minimal working version
- Test with various inputs
- Handle edge cases gracefully
- Add error handling

### 3. Optimize and Polish

- Profile performance for large batches
- Add helpful tooltips and descriptions
- Validate inputs appropriately
- Consider memory usage

### 4. Document and Share

- Write clear documentation
- Include example workflows
- Provide installation instructions
- Consider publishing to ComfyUI Manager

## Best Practices

1. **Follow ComfyUI Conventions**
   - Use existing data types when possible
   - Match the coding style of built-in nodes
   - Implement standard node attributes

2. **Handle Errors Gracefully**
   ```python
   def execute(self, input_data):
       try:
           result = process_data(input_data)
       except Exception as e:
           raise ValueError(f"Processing failed: {str(e)}")
       return (result,)
   ```

3. **Optimize for Batch Processing**
   - Remember IMAGE type is a batch
   - Process entire batches efficiently
   - Avoid loops over individual items when possible

4. **Provide Clear Feedback**
   - Use descriptive node names
   - Add tooltips to inputs
   - Include helpful error messages

## Next Steps

- Read the [Node Interface Reference](./02-node-interface.md) for detailed API documentation
- Explore [Data Types and Type Conversion](./03-data-types.md)
- Learn about [Advanced Features](./04-advanced-features.md)
- Study [Example Implementations](./05-examples.md)

## Resources

- [Official ComfyUI Repository](https://github.com/comfyanonymous/ComfyUI)
- [Built-in Nodes Source](https://github.com/comfyanonymous/ComfyUI/blob/master/nodes.py)
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)
- [Community Discord](https://discord.gg/comfyui)