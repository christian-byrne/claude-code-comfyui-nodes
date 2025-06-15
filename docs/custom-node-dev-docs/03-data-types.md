# Data Types and Type Conversion

## Understanding ComfyUI's Type System

ComfyUI uses a strongly-typed system where each input and output has a specific type. Understanding these types and how to work with them is crucial for custom node development.

## Core Data Types

### Image Data

#### IMAGE Type
- **Internal Format**: `torch.Tensor` with shape `[B, H, W, C]`
- **Range**: 0.0 to 1.0 (normalized floating point)
- **Channels**: 3 (RGB) or 4 (RGBA)
- **Batch**: B represents batch size (multiple images)

```python
def process_image(self, image):
    # image shape: [batch, height, width, channels]
    batch_size, height, width, channels = image.shape
    
    # Process each image in batch
    for i in range(batch_size):
        single_image = image[i]  # [H, W, C]
        
    # Or process entire batch at once
    inverted = 1.0 - image  # Invert all images
    
    return (inverted,)
```

#### MASK Type
- **Internal Format**: `torch.Tensor` with shape `[H, W]` or `[B, H, W]`
- **Range**: 0.0 to 1.0 (0 = black/transparent, 1 = white/opaque)
- **Channels**: 1 (grayscale)

```python
def create_mask(self, image):
    # Create mask from image luminance
    # image: [B, H, W, C]
    gray = 0.299 * image[:,:,:,0] + 0.587 * image[:,:,:,1] + 0.114 * image[:,:,:,2]
    # gray: [B, H, W]
    
    # Threshold to create binary mask
    mask = (gray > 0.5).float()
    
    return (mask,)
```

### Latent Data

#### LATENT Type
- **Internal Format**: Dictionary with "samples" key
- **Structure**: `{"samples": torch.Tensor}`
- **Shape**: Typically `[B, 4, H/8, W/8]` for SD1.5/SDXL

```python
def process_latent(self, latent):
    samples = latent["samples"]  # [B, C, H, W]
    
    # Modify latent
    samples = samples * 0.9  # Reduce strength
    
    # Return in correct format
    return ({"samples": samples},)
```

### Model Types

#### MODEL Type
- Diffusion model object
- Contains UNet and configuration
- Should not be modified directly

```python
def use_model(self, model, latent):
    # Models are typically passed through
    # Use ComfyUI's sampling functions
    import comfy.sample
    
    # Don't modify model directly
    return (model,)
```

#### CLIP Type
- Text encoder model
- Used for creating conditioning
- Includes tokenizer

```python
def encode_text(self, clip, text):
    tokens = clip.tokenize(text)
    conditioning = clip.encode_from_tokens(tokens)
    return (conditioning,)
```

#### VAE Type
- Variational Autoencoder
- Converts between pixels and latents

```python
def decode_latent(self, vae, latent):
    image = vae.decode(latent["samples"])
    return (image,)
```

### Basic Types

#### STRING Type
```python
"text": ("STRING", {
    "default": "Hello",
    "multiline": True
})
```

#### INT Type
```python
"count": ("INT", {
    "default": 1,
    "min": 0,
    "max": 100
})
```

#### FLOAT Type
```python
"strength": ("FLOAT", {
    "default": 1.0,
    "min": 0.0,
    "max": 10.0,
    "step": 0.01
})
```

#### BOOLEAN Type
```python
"enable": ("BOOLEAN", {
    "default": True,
    "label_on": "Yes",
    "label_off": "No"
})
```

## Type Conversion

### Converting Between Image Formats

#### PIL to ComfyUI
```python
import torch
import numpy as np
from PIL import Image

def pil_to_comfy(pil_image):
    # Convert PIL to numpy
    np_image = np.array(pil_image).astype(np.float32) / 255.0
    
    # Add batch dimension
    if len(np_image.shape) == 2:  # Grayscale
        np_image = np.expand_dims(np_image, axis=2)
    np_image = np.expand_dims(np_image, axis=0)  # [1, H, W, C]
    
    # Convert to torch tensor
    return torch.from_numpy(np_image)
```

#### ComfyUI to PIL
```python
def comfy_to_pil(comfy_image, index=0):
    # Get single image from batch
    image = comfy_image[index].cpu().numpy()
    
    # Convert to 0-255 range
    image = (image * 255).astype(np.uint8)
    
    # Handle different channel counts
    if image.shape[2] == 1:  # Grayscale
        image = image.squeeze(2)
        
    return Image.fromarray(image)
```

### Working with Masks

#### Image to Mask
```python
def image_to_mask(self, image, channel="luminance"):
    if channel == "luminance":
        # Convert to grayscale using luminance formula
        mask = 0.299 * image[:,:,:,0] + 0.587 * image[:,:,:,1] + 0.114 * image[:,:,:,2]
    elif channel == "red":
        mask = image[:,:,:,0]
    elif channel == "green":
        mask = image[:,:,:,1]
    elif channel == "blue":
        mask = image[:,:,:,2]
    elif channel == "alpha" and image.shape[3] > 3:
        mask = image[:,:,:,3]
    else:
        mask = image[:,:,:,0]  # Default to red
        
    return (mask,)
```

#### Mask to Image
```python
def mask_to_image(self, mask):
    # Ensure mask has batch dimension
    if len(mask.shape) == 2:
        mask = mask.unsqueeze(0)
    
    # Convert to RGB by duplicating channels
    mask_rgb = mask.unsqueeze(3).repeat(1, 1, 1, 3)
    
    return (mask_rgb,)
```

## Special Types

### ANY Type (*)
- Matches any input type
- Use sparingly as it can cause issues
- Useful for generic processing nodes

```python
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            "any_input": ("*", {})
        }
    }

def process(self, any_input):
    # Check type at runtime
    if isinstance(any_input, torch.Tensor):
        return self.process_tensor(any_input)
    elif isinstance(any_input, dict):
        return self.process_dict(any_input)
    else:
        return (any_input,)  # Pass through
```

### Union Types
- Specify multiple acceptable types
- Format: "TYPE1,TYPE2,TYPE3"

```python
"number": ("FLOAT,INT", {
    "default": 1.0
})
```

## Type Validation

### Runtime Type Checking
```python
def process(self, image):
    # Validate tensor
    if not isinstance(image, torch.Tensor):
        raise ValueError("Expected tensor input")
    
    # Validate shape
    if len(image.shape) != 4:
        raise ValueError(f"Expected 4D tensor, got {len(image.shape)}D")
    
    # Validate range
    if image.max() > 1.0 or image.min() < 0.0:
        raise ValueError("Image values must be in range [0, 1]")
```

### Safe Type Conversion
```python
def safe_float_conversion(self, value):
    """Safely convert various inputs to float"""
    if isinstance(value, (int, float)):
        return float(value)
    elif isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to float")
    elif isinstance(value, torch.Tensor):
        return value.item() if value.numel() == 1 else value.mean().item()
    else:
        raise TypeError(f"Unsupported type: {type(value)}")
```

## Custom Types

### Creating Custom Types
```python
class CustomDataType:
    def __init__(self, data, metadata=None):
        self.data = data
        self.metadata = metadata or {}
    
    def transform(self):
        # Custom transformation logic
        return self.data

# Use in node
RETURN_TYPES = ("CustomDataType",)

def process(self):
    result = CustomDataType(
        data={"key": "value"},
        metadata={"created": time.time()}
    )
    return (result,)
```

### Type Compatibility
```python
# Define compatible types
class MyCustomImage:
    @classmethod
    def is_compatible(cls, other_type):
        return other_type in ["IMAGE", "MyCustomImage"]
```

## Best Practices

1. **Always Validate Input Types**
   - Check tensor dimensions
   - Verify value ranges
   - Handle edge cases

2. **Preserve Batch Dimensions**
   - Process entire batches when possible
   - Maintain consistent batch sizes

3. **Use Appropriate Precision**
   - Use float32 for images
   - Consider float16 for large models
   - Use int64 for indices

4. **Handle Device Placement**
   ```python
   def process(self, tensor):
       device = tensor.device
       # Create new tensors on same device
       result = torch.zeros_like(tensor, device=device)
   ```

5. **Document Type Expectations**
   - Add comments explaining formats
   - Include examples in docstrings
   - Validate assumptions

## Common Patterns

### Batch Processing
```python
def process_batch(self, images):
    results = []
    for image in images:
        # Process individual image
        result = self.process_single(image)
        results.append(result)
    
    # Stack back into batch
    return (torch.stack(results),)
```

### Type Adapter
```python
class TypeAdapter:
    """Converts between different representations"""
    
    @staticmethod
    def tensor_to_numpy(tensor):
        return tensor.cpu().numpy()
    
    @staticmethod
    def numpy_to_tensor(array):
        return torch.from_numpy(array)
    
    @staticmethod
    def normalize(tensor, min_val=0, max_val=1):
        tensor_min = tensor.min()
        tensor_max = tensor.max()
        return (tensor - tensor_min) / (tensor_max - tensor_min) * (max_val - min_val) + min_val
```

## Next Steps

- Explore [Advanced Features](./04-advanced-features.md)
- See [Example Implementations](./05-examples.md)
- Learn about [Frontend Integration](./06-frontend-integration.md)