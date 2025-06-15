# Node Interface Reference

## Complete Node API

This reference covers all attributes and methods available when creating custom nodes in ComfyUI.

## Required Components

### Class Definition

Every custom node must be a Python class. The class name will be used internally, while the display name can be customized.

```python
class YourNodeClassName:
    """Docstring describing what your node does"""
```

### INPUT_TYPES (Required)

A class method that returns a dictionary defining the node's inputs.

```python
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            # Required inputs must be connected
            "input_name": ("TYPE", options_dict),
        },
        "optional": {
            # Optional inputs can be left unconnected
            "optional_name": ("TYPE", options_dict),
        },
        "hidden": {
            # Hidden inputs not shown in UI
            "unique_id": "UNIQUE_ID",
            "prompt": "PROMPT",
            "extra_pnginfo": "EXTRA_PNGINFO",
        }
    }
```

### RETURN_TYPES (Required)

A tuple defining the types of outputs the node produces.

```python
RETURN_TYPES = ("IMAGE", "MASK")
```

### FUNCTION (Required)

The name of the method to call when the node executes.

```python
FUNCTION = "process"
```

### Execution Method (Required)

The method that performs the node's computation.

```python
def process(self, **kwargs):
    # All inputs from INPUT_TYPES are passed as keyword arguments
    # Must return a tuple matching RETURN_TYPES
    return (output1, output2)
```

## Optional Components

### CATEGORY

Where the node appears in the add node menu. Use "/" for submenu organization.

```python
CATEGORY = "image/filters"
```

### RETURN_NAMES

Human-readable names for outputs (must match RETURN_TYPES length).

```python
RETURN_NAMES = ("processed_image", "generated_mask")
```

### OUTPUT_NODE

Set to `True` if this node produces final outputs (like Save Image).

```python
OUTPUT_NODE = True
```

### OUTPUT_TOOLTIPS

Tooltips for each output socket.

```python
OUTPUT_TOOLTIPS = ("The processed image", "The generated mask")
```

### DESCRIPTION

A description shown in the UI when hovering over the node.

```python
DESCRIPTION = "Applies advanced filtering to images"
```

## Input Type Options

### Basic Input Options

All input types support these options:

```python
{
    "default": value,           # Default value
    "forceInput": True,        # Force connection (no widget)
    "lazy": True,              # Enable lazy evaluation
    "tooltip": "Help text",    # Tooltip on hover
}
```

### Numeric Inputs (INT, FLOAT)

```python
"number": ("FLOAT", {
    "default": 1.0,
    "min": 0.0,
    "max": 10.0,
    "step": 0.01,
    "round": 0.001,           # Round to this precision
    "display": "slider",      # or "number"
})
```

### String Inputs

```python
"text": ("STRING", {
    "default": "Enter text",
    "multiline": True,        # Multi-line text box
    "dynamicPrompts": True,   # Enable dynamic prompts
    "placeholder": "Type here..."
})
```

### Boolean Inputs

```python
"enable": ("BOOLEAN", {
    "default": True,
    "label_on": "Enabled",    # Label when True
    "label_off": "Disabled"   # Label when False
})
```

### Combo Box (Dropdown)

```python
"mode": (["option1", "option2", "option3"], {
    "default": "option1"
})
```

### Image Upload

```python
"image": ("IMAGE", {
    "image_upload": True,     # Enable upload button
})
```

## Advanced Features

### IS_CHANGED Method

Control when the node is re-executed:

```python
@classmethod
def IS_CHANGED(cls, **kwargs):
    # Return a value that changes when node should re-execute
    # Can return hash, timestamp, random value, etc.
    return float("nan")  # Always re-execute
```

### VALIDATE_INPUTS Method

Custom validation before execution:

```python
@classmethod
def VALIDATE_INPUTS(cls, **kwargs):
    # Return True if inputs are valid
    # Return error message string if invalid
    if kwargs.get("value", 0) < 0:
        return "Value must be non-negative"
    return True
```

### Hidden Inputs

Access special system information:

```python
"hidden": {
    "unique_id": "UNIQUE_ID",          # Node's unique ID
    "prompt": "PROMPT",                # Full workflow prompt
    "extra_pnginfo": "EXTRA_PNGINFO",  # PNG metadata dict
    "dynprompt": "DYNPROMPT"           # Dynamic prompt object
}
```

### Lazy Evaluation

Enable on-demand execution:

```python
"input": ("TYPE", {"lazy": True})

# In execution method:
def process(self, input):
    # Input might be a lazy object
    if hasattr(input, '__call__'):
        actual_value = input()  # Evaluate lazy input
```

## Type System

### Built-in Types

```python
# Basic types
"STRING"              # Text strings
"INT"                 # Integers
"FLOAT"               # Floating point numbers
"BOOLEAN"             # True/False values

# Image types
"IMAGE"               # Image tensor [B,H,W,C]
"MASK"                # Mask tensor [H,W] or [B,H,W]
"LATENT"              # Latent representation

# Model types
"MODEL"               # Diffusion model
"CLIP"                # CLIP text encoder
"VAE"                 # Variational autoencoder
"CONDITIONING"        # Text conditioning
"CONTROL_NET"         # ControlNet model

# Advanced types
"SAMPLER"             # Sampling method
"SIGMAS"              # Sigma schedule
"GUIDER"              # Guidance model
"NOISE"               # Noise tensor

# Special types
"*"                   # ANY type (matches anything)
"STRING,FLOAT,INT"    # Union types
```

### Custom Types

You can define custom types:

```python
class MY_CUSTOM_TYPE:
    def __init__(self, data):
        self.data = data

# Use in node:
RETURN_TYPES = ("MY_CUSTOM_TYPE",)
```

## Complete Example

```python
class AdvancedImageProcessor:
    """
    Processes images with multiple effects and options.
    Demonstrates most node interface features.
    """
    
    def __init__(self):
        self.type = "AdvancedImageProcessor"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image to process"
                }),
                "mode": (["blur", "sharpen", "edge_detect"], {
                    "default": "blur"
                }),
                "strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "slider"
                }),
            },
            "optional": {
                "mask": ("MASK", {
                    "tooltip": "Optional mask for selective processing"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("processed", "effect_mask")
    OUTPUT_TOOLTIPS = ("Processed image", "Mask showing affected areas")
    
    FUNCTION = "process_image"
    CATEGORY = "image/processing"
    DESCRIPTION = "Advanced image processing with multiple effects"
    
    def process_image(self, image, mode, strength, mask=None, seed=0, unique_id=None):
        # Processing implementation
        processed = apply_effect(image, mode, strength)
        effect_mask = generate_effect_mask(image, processed)
        
        return (processed, effect_mask)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Re-execute if seed changes
        return kwargs.get("seed", 0)
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        if kwargs.get("strength", 0) < 0:
            return "Strength must be non-negative"
        return True

# Register the node
NODE_CLASS_MAPPINGS = {
    "AdvancedImageProcessor": AdvancedImageProcessor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedImageProcessor": "Advanced Image Processor"
}
```

## Server Communication

For advanced use cases, communicate with the frontend:

```python
from server import PromptServer

def process_image(self, image):
    # Send message to frontend
    PromptServer.instance.send_sync(
        "my_node.message",
        {"text": "Processing complete", "node_id": unique_id}
    )
    return (image,)
```

## Next Steps

- Learn about [Data Types and Type Conversion](./03-data-types.md)
- Explore [Advanced Features](./04-advanced-features.md)
- See [Example Implementations](./05-examples.md)