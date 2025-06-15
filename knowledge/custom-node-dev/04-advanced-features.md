# Advanced Custom Node Features

## Frontend Integration

### Adding JavaScript Extensions

Create a web extension to add custom UI behavior:

```javascript
// web/js/my_extension.js
app.registerExtension({
    name: "my.custom.extension",
    
    async setup() {
        // Called once when extension loads
        console.log("Extension loaded");
    },
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Modify node definition before registration
        if (nodeData.name === "MyCustomNode") {
            // Add custom behavior
        }
    },
    
    nodeCreated(node) {
        // Called when any node is created
        if (node.type === "MyCustomNode") {
            // Add custom widgets or modify node
            this.addCustomWidget(node);
        }
    },
    
    addCustomWidget(node) {
        // Add a custom widget to the node
        const widget = node.addWidget("button", "Click Me", null, () => {
            alert("Button clicked!");
        });
    }
});
```

Enable in `__init__.py`:
```python
WEB_DIRECTORY = "./web/js"
__all__ = ['NODE_CLASS_MAPPINGS', 'WEB_DIRECTORY']
```

### Server-Client Communication

Send messages from server to client:

```python
from server import PromptServer

class InteractiveNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.5}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    FUNCTION = "process"
    
    def process(self, value, unique_id):
        # Send progress updates
        PromptServer.instance.send_sync(
            "my_node.progress",
            {
                "node_id": unique_id,
                "progress": 0.5,
                "message": "Processing..."
            }
        )
        
        # Process...
        result = value * 2
        
        # Send completion
        PromptServer.instance.send_sync(
            "my_node.complete",
            {
                "node_id": unique_id,
                "result": result
            }
        )
        
        return (result,)
```

Client-side listener:
```javascript
app.api.addEventListener("my_node.progress", (event) => {
    const { node_id, progress, message } = event.detail;
    // Update UI
});
```

## Lazy Evaluation

Implement nodes that only execute when needed:

```python
class LazyProcessorNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trigger": ("BOOLEAN", {"default": False}),
                "expensive_input": ("IMAGE", {"lazy": True}),
            }
        }
    
    FUNCTION = "process"
    
    def process(self, trigger, expensive_input):
        if not trigger:
            # Don't evaluate expensive input
            return (None,)
        
        # Only evaluate when needed
        if callable(expensive_input):
            actual_image = expensive_input()
        else:
            actual_image = expensive_input
            
        # Process the image
        result = self.expensive_operation(actual_image)
        return (result,)
```

## Dynamic Inputs

Create nodes with variable numbers of inputs:

```python
class DynamicInputNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_count": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 10
                }),
            }
        }
    
    FUNCTION = "process"
    
    def process(self, input_count, **kwargs):
        # Access dynamic inputs
        results = []
        for i in range(input_count):
            input_key = f"input_{i}"
            if input_key in kwargs:
                results.append(kwargs[input_key])
        
        return (results,)
```

## Custom Widgets

### Remote Data Source Widget

Create a widget that fetches data from an API:

```python
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            "model_name": ("STRING", {
                "default": "",
                "remote": {
                    "route": "/api/models",
                    "refresh_button": True,
                    "refresh": 60000,  # Refresh every minute
                }
            }),
        }
    }
```

### Multi-Select Widget

```python
"options": (["option1", "option2", "option3"], {
    "default": ["option1"],
    "multi_select": {
        "placeholder": "Select options...",
        "chip": True
    }
})
```

## Node Expansion

Create nodes that dynamically generate other nodes:

```python
class ExpanderNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "count": ("INT", {"default": 3}),
                "operation": (["add", "multiply"], {}),
            }
        }
    
    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "expand"
    
    def expand(self, count, operation):
        # This is a placeholder - actual expansion happens elsewhere
        return (0.0,)
    
    @classmethod
    def expand_node(cls, node, context):
        """Called during graph expansion"""
        count = node.inputs["count"]
        operation = node.inputs["operation"]
        
        # Create a subgraph
        nodes = []
        for i in range(count):
            node_data = {
                "type": "MathOperation",
                "inputs": {"operation": operation}
            }
            nodes.append(node_data)
        
        return {
            "nodes": nodes,
            "connections": [...]  # Define connections
        }
```

## Caching and Optimization

### Implement Smart Caching

```python
class CachedProcessor:
    def __init__(self):
        self.cache = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {}),
                "settings": ("STRING", {}),
            }
        }
    
    FUNCTION = "process"
    
    def process(self, image, settings):
        # Create cache key
        cache_key = self.compute_cache_key(image, settings)
        
        # Check cache
        if cache_key in self.cache:
            print("Using cached result")
            return self.cache[cache_key]
        
        # Process
        result = self.expensive_processing(image, settings)
        
        # Cache result
        self.cache[cache_key] = (result,)
        
        # Limit cache size
        if len(self.cache) > 10:
            # Remove oldest entry
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        
        return (result,)
    
    def compute_cache_key(self, image, settings):
        # Create unique key from inputs
        import hashlib
        image_hash = hashlib.md5(image.cpu().numpy().tobytes()).hexdigest()
        settings_hash = hashlib.md5(settings.encode()).hexdigest()
        return f"{image_hash}_{settings_hash}"
```

### Memory Management

```python
import torch
import gc

class MemoryEfficientNode:
    def process(self, large_input):
        # Process in chunks to save memory
        chunk_size = 10
        results = []
        
        for i in range(0, len(large_input), chunk_size):
            chunk = large_input[i:i+chunk_size]
            
            # Process chunk
            with torch.no_grad():
                result = self.process_chunk(chunk)
                results.append(result)
            
            # Clear GPU cache if needed
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        # Combine results
        final_result = torch.cat(results)
        
        # Force garbage collection
        gc.collect()
        
        return (final_result,)
```

## Error Handling and Validation

### Comprehensive Input Validation

```python
class RobustNode:
    @classmethod
    def VALIDATE_INPUTS(cls, image, scale_factor, mode):
        # Check image
        if not isinstance(image, torch.Tensor):
            return "Image must be a tensor"
        
        if len(image.shape) != 4:
            return f"Image must be 4D tensor, got {len(image.shape)}D"
        
        if image.shape[3] not in [3, 4]:
            return f"Image must have 3 or 4 channels, got {image.shape[3]}"
        
        # Check scale factor
        if scale_factor <= 0:
            return "Scale factor must be positive"
        
        if scale_factor > 10:
            return "Scale factor too large (max 10)"
        
        # Check mode
        valid_modes = ["bilinear", "nearest", "bicubic"]
        if mode not in valid_modes:
            return f"Invalid mode. Must be one of: {valid_modes}"
        
        return True
    
    def process(self, image, scale_factor, mode):
        try:
            # Process with error handling
            result = self.scale_image(image, scale_factor, mode)
            
        except torch.cuda.OutOfMemoryError:
            # Handle GPU OOM
            torch.cuda.empty_cache()
            # Try with CPU
            result = self.scale_image(image.cpu(), scale_factor, mode)
            
        except Exception as e:
            # Log error and provide helpful message
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Processing failed: {str(e)}")
        
        return (result,)
```

## Progress Reporting

### Long-Running Operations

```python
import time
from comfy.cli_args import args

class ProgressNode:
    def process(self, items):
        total = len(items)
        results = []
        
        for i, item in enumerate(items):
            # Update progress
            if not args.disable_smart_memory:
                comfy.model_management.throw_exception_if_processing_interrupted()
            
            # Report progress
            progress = (i + 1) / total
            self.report_progress(progress, f"Processing item {i+1}/{total}")
            
            # Process item
            result = self.process_item(item)
            results.append(result)
            
            # Yield to other processes
            time.sleep(0.001)
        
        return (results,)
    
    def report_progress(self, progress, message):
        # Could send to frontend or log
        print(f"Progress: {progress:.1%} - {message}")
```

## Custom Scheduling

### Conditional Execution

```python
class ConditionalNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {}),
                "if_true": ("IMAGE", {"lazy": True}),
                "if_false": ("IMAGE", {"lazy": True}),
            }
        }
    
    FUNCTION = "execute"
    
    def execute(self, condition, if_true, if_false):
        # Only evaluate the needed branch
        if condition:
            result = if_true() if callable(if_true) else if_true
        else:
            result = if_false() if callable(if_false) else if_false
        
        return (result,)
```

### Loop Implementation

```python
class LoopNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "iterations": ("INT", {"default": 5}),
                "initial_value": ("FLOAT", {"default": 1.0}),
            }
        }
    
    FUNCTION = "loop"
    
    def loop(self, iterations, initial_value):
        value = initial_value
        
        for i in range(iterations):
            # In practice, this would call other nodes
            value = self.iteration_step(value, i)
        
        return (value,)
```

## Testing and Debugging

### Unit Testing Custom Nodes

```python
# test_my_node.py
import unittest
import torch
from my_custom_nodes import MyImageProcessor

class TestMyImageProcessor(unittest.TestCase):
    def setUp(self):
        self.node = MyImageProcessor()
        
    def test_basic_processing(self):
        # Create test image
        test_image = torch.rand(1, 256, 256, 3)
        
        # Process
        result = self.node.process(test_image, strength=0.5)
        
        # Verify
        self.assertEqual(result[0].shape, test_image.shape)
        self.assertTrue(torch.all(result[0] >= 0))
        self.assertTrue(torch.all(result[0] <= 1))
    
    def test_batch_processing(self):
        # Test with batch
        batch_image = torch.rand(5, 256, 256, 3)
        result = self.node.process(batch_image, strength=0.5)
        
        self.assertEqual(result[0].shape[0], 5)

if __name__ == "__main__":
    unittest.main()
```

### Debug Utilities

```python
class DebugNode:
    """Node for debugging workflows"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any_input": ("*", {}),
                "label": ("STRING", {"default": "Debug"}),
            }
        }
    
    RETURN_TYPES = ("*",)
    FUNCTION = "debug"
    OUTPUT_NODE = True
    
    def debug(self, any_input, label):
        print(f"\n=== {label} ===")
        print(f"Type: {type(any_input)}")
        
        if isinstance(any_input, torch.Tensor):
            print(f"Shape: {any_input.shape}")
            print(f"Device: {any_input.device}")
            print(f"dtype: {any_input.dtype}")
            print(f"Min: {any_input.min():.4f}")
            print(f"Max: {any_input.max():.4f}")
            print(f"Mean: {any_input.mean():.4f}")
        elif isinstance(any_input, dict):
            print(f"Keys: {list(any_input.keys())}")
        elif isinstance(any_input, (list, tuple)):
            print(f"Length: {len(any_input)}")
        
        print("================\n")
        
        return (any_input,)
```

## Next Steps

- See [Example Implementations](./05-examples.md)
- Learn about [Frontend Integration](./06-frontend-integration.md)
- Explore [Publishing and Distribution](./07-publishing.md)