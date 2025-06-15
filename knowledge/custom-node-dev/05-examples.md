# Example Custom Node Implementations

## Complete Working Examples

These examples demonstrate various custom node patterns and best practices.

## 1. Image Processing Node

A complete image filter node with multiple options:

```python
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image, ImageFilter

class AdvancedImageFilter:
    """
    Advanced image filtering with multiple algorithms and options.
    Demonstrates image processing, batch handling, and mask support.
    """
    
    def __init__(self):
        self.type = "AdvancedImageFilter"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Input image to filter"}),
                "filter_type": ([
                    "gaussian_blur",
                    "motion_blur", 
                    "unsharp_mask",
                    "edge_enhance",
                    "emboss",
                    "find_edges",
                    "contour"
                ], {
                    "default": "gaussian_blur"
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
                    "tooltip": "Optional mask for selective filtering"
                }),
                "blend_mode": (["normal", "multiply", "screen", "overlay"], {
                    "default": "normal"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("filtered_image",)
    OUTPUT_TOOLTIPS = ("The filtered image",)
    
    FUNCTION = "apply_filter"
    CATEGORY = "image/filters"
    DESCRIPTION = "Apply various image filters with adjustable strength"
    
    def apply_filter(self, image, filter_type, strength, mask=None, blend_mode="normal"):
        # Handle batch processing
        batch_size = image.shape[0]
        results = []
        
        for i in range(batch_size):
            # Get single image
            single_image = image[i]
            
            # Apply filter
            filtered = self._apply_single_filter(single_image, filter_type, strength)
            
            # Apply mask if provided
            if mask is not None:
                single_mask = mask[i] if len(mask.shape) == 3 else mask
                filtered = self._apply_mask(single_image, filtered, single_mask)
            
            # Blend with original
            if blend_mode != "normal":
                filtered = self._blend_images(single_image, filtered, blend_mode, strength)
            
            results.append(filtered)
        
        # Stack results back into batch
        result_batch = torch.stack(results)
        return (result_batch,)
    
    def _apply_single_filter(self, image, filter_type, strength):
        """Apply filter to single image"""
        
        if filter_type == "gaussian_blur":
            sigma = strength * 2.0
            kernel_size = int(sigma * 4) | 1  # Ensure odd
            return self._gaussian_blur(image, kernel_size, sigma)
            
        elif filter_type == "motion_blur":
            return self._motion_blur(image, int(strength * 10) + 1)
            
        elif filter_type == "unsharp_mask":
            return self._unsharp_mask(image, strength)
            
        elif filter_type in ["edge_enhance", "emboss", "find_edges", "contour"]:
            # Convert to PIL for these filters
            pil_image = self._tensor_to_pil(image)
            
            if filter_type == "edge_enhance":
                filtered = pil_image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            elif filter_type == "emboss":
                filtered = pil_image.filter(ImageFilter.EMBOSS)
            elif filter_type == "find_edges":
                filtered = pil_image.filter(ImageFilter.FIND_EDGES)
            else:  # contour
                filtered = pil_image.filter(ImageFilter.CONTOUR)
            
            # Convert back to tensor
            result = self._pil_to_tensor(filtered)
            
            # Blend with original based on strength
            return image * (1 - strength) + result * strength
        
        return image
    
    def _gaussian_blur(self, image, kernel_size, sigma):
        """Apply Gaussian blur using PyTorch"""
        # Add batch and channel dimensions for conv2d
        image = image.permute(2, 0, 1).unsqueeze(0)  # [1, C, H, W]
        
        # Create Gaussian kernel
        kernel = self._create_gaussian_kernel(kernel_size, sigma)
        kernel = kernel.expand(image.shape[1], 1, kernel_size, kernel_size)
        
        # Apply convolution
        blurred = F.conv2d(image, kernel, padding=kernel_size//2, groups=image.shape[1])
        
        # Convert back to [H, W, C]
        return blurred.squeeze(0).permute(1, 2, 0)
    
    def _create_gaussian_kernel(self, size, sigma):
        """Create 2D Gaussian kernel"""
        coords = torch.arange(size, dtype=torch.float32)
        coords -= size // 2
        
        g = torch.exp(-(coords ** 2) / (2 * sigma ** 2))
        g /= g.sum()
        
        return g.unsqueeze(0) * g.unsqueeze(1)
    
    def _motion_blur(self, image, size):
        """Apply motion blur"""
        # Create motion kernel (horizontal)
        kernel = torch.zeros(size, size)
        kernel[size // 2, :] = 1.0 / size
        
        # Apply to each channel
        image = image.permute(2, 0, 1).unsqueeze(0)
        kernel = kernel.unsqueeze(0).unsqueeze(0).expand(image.shape[1], 1, size, size)
        
        blurred = F.conv2d(image, kernel, padding=size//2, groups=image.shape[1])
        
        return blurred.squeeze(0).permute(1, 2, 0)
    
    def _unsharp_mask(self, image, strength):
        """Apply unsharp mask sharpening"""
        # Blur the image
        blurred = self._gaussian_blur(image, 5, 1.0)
        
        # Create mask
        mask = image - blurred
        
        # Apply sharpening
        sharpened = image + mask * strength
        
        # Clamp values
        return torch.clamp(sharpened, 0, 1)
    
    def _apply_mask(self, original, filtered, mask):
        """Apply mask to blend original and filtered images"""
        # Ensure mask has 3 channels
        if len(mask.shape) == 2:
            mask = mask.unsqueeze(2).expand(-1, -1, 3)
        
        return original * (1 - mask) + filtered * mask
    
    def _blend_images(self, img1, img2, mode, opacity):
        """Blend two images using various modes"""
        if mode == "multiply":
            blended = img1 * img2
        elif mode == "screen":
            blended = 1 - (1 - img1) * (1 - img2)
        elif mode == "overlay":
            mask = img1 > 0.5
            blended = torch.where(
                mask,
                1 - 2 * (1 - img1) * (1 - img2),
                2 * img1 * img2
            )
        else:  # normal
            blended = img2
        
        # Apply opacity
        return img1 * (1 - opacity) + blended * opacity
    
    def _tensor_to_pil(self, tensor):
        """Convert tensor to PIL Image"""
        array = (tensor.cpu().numpy() * 255).astype(np.uint8)
        return Image.fromarray(array)
    
    def _pil_to_tensor(self, pil_image):
        """Convert PIL Image to tensor"""
        array = np.array(pil_image).astype(np.float32) / 255.0
        return torch.from_numpy(array).to(tensor.device)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always re-execute to see changes
        return float("nan")

# Register the node
NODE_CLASS_MAPPINGS = {
    "AdvancedImageFilter": AdvancedImageFilter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedImageFilter": "Advanced Image Filter"
}
```

## 2. Batch Processing Node

Handle multiple images with different operations:

```python
class BatchImageProcessor:
    """
    Process batches of images with different operations per image.
    Demonstrates dynamic inputs and batch handling.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Batch of images to process"}),
                "operation": ([
                    "rotate_sequence",
                    "brightness_gradient",
                    "color_shift",
                    "zoom_sequence"
                ], {"default": "rotate_sequence"}),
                "start_value": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.1
                }),
                "end_value": ("FLOAT", {
                    "default": 1.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.1
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process_batch"
    CATEGORY = "image/batch"
    
    def process_batch(self, images, operation, start_value, end_value):
        batch_size = images.shape[0]
        results = []
        
        # Calculate value for each image in sequence
        for i in range(batch_size):
            t = i / max(1, batch_size - 1)  # Normalize to 0-1
            value = start_value + (end_value - start_value) * t
            
            image = images[i]
            
            if operation == "rotate_sequence":
                angle = value * 360
                result = self._rotate_image(image, angle)
                
            elif operation == "brightness_gradient":
                result = torch.clamp(image * (1 + value), 0, 1)
                
            elif operation == "color_shift":
                result = self._color_shift(image, value)
                
            elif operation == "zoom_sequence":
                scale = 1 + value
                result = self._zoom_image(image, scale)
            
            results.append(result)
        
        return (torch.stack(results),)
    
    def _rotate_image(self, image, angle):
        """Rotate image by angle degrees"""
        # Convert to PIL for rotation
        pil_img = Image.fromarray((image.cpu().numpy() * 255).astype(np.uint8))
        rotated = pil_img.rotate(angle, expand=False, fillcolor=(0, 0, 0))
        
        # Convert back
        array = np.array(rotated).astype(np.float32) / 255.0
        return torch.from_numpy(array).to(image.device)
    
    def _color_shift(self, image, shift):
        """Shift colors in HSV space"""
        # Simple RGB channel rotation
        shifted = torch.zeros_like(image)
        if shift > 0:
            shifted[:, :, 0] = image[:, :, 1] * shift + image[:, :, 0] * (1 - shift)
            shifted[:, :, 1] = image[:, :, 2] * shift + image[:, :, 1] * (1 - shift)
            shifted[:, :, 2] = image[:, :, 0] * shift + image[:, :, 2] * (1 - shift)
        else:
            shift = -shift
            shifted[:, :, 0] = image[:, :, 2] * shift + image[:, :, 0] * (1 - shift)
            shifted[:, :, 1] = image[:, :, 0] * shift + image[:, :, 1] * (1 - shift)
            shifted[:, :, 2] = image[:, :, 1] * shift + image[:, :, 2] * (1 - shift)
        
        return shifted
    
    def _zoom_image(self, image, scale):
        """Zoom image by scale factor"""
        h, w = image.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        
        # Add batch dimension for interpolation
        img_batch = image.permute(2, 0, 1).unsqueeze(0)
        
        # Resize
        resized = F.interpolate(img_batch, size=(new_h, new_w), mode='bilinear', align_corners=False)
        resized = resized.squeeze(0).permute(1, 2, 0)
        
        # Crop or pad to original size
        if scale > 1:
            # Crop center
            start_h = (new_h - h) // 2
            start_w = (new_w - w) // 2
            result = resized[start_h:start_h+h, start_w:start_w+w]
        else:
            # Pad
            pad_h = (h - new_h) // 2
            pad_w = (w - new_w) // 2
            result = torch.zeros_like(image)
            result[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = resized
        
        return result
```

## 3. Model Integration Node

Integrate with external models or APIs:

```python
import json
import requests
import base64
from io import BytesIO

class ExternalAPINode:
    """
    Integrate with external APIs for processing.
    Demonstrates async operations and error handling.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {}),
                "api_endpoint": ("STRING", {
                    "default": "http://localhost:8000/process",
                    "multiline": False
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "parameters": ("STRING", {
                    "default": "{}",
                    "multiline": True,
                    "tooltip": "JSON parameters for the API"
                }),
            },
            "optional": {
                "timeout": ("INT", {
                    "default": 30,
                    "min": 1,
                    "max": 300
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("processed_image", "api_response")
    FUNCTION = "call_api"
    CATEGORY = "api/external"
    
    def call_api(self, image, api_endpoint, api_key, parameters, timeout=30):
        try:
            # Parse parameters
            params = json.loads(parameters)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON parameters: {e}")
        
        # Convert image to base64
        pil_image = self._tensor_to_pil(image[0])  # First image in batch
        
        # Prepare request
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Build request payload
        payload = {
            "image": img_base64,
            "parameters": params
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            # Make API request
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract processed image
            if "image" in result:
                processed_img = self._base64_to_tensor(result["image"])
            else:
                raise ValueError("No image in API response")
            
            # Return processed image and response
            return (processed_img, json.dumps(result, indent=2))
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
    
    def _tensor_to_pil(self, tensor):
        """Convert tensor to PIL Image"""
        array = (tensor.cpu().numpy() * 255).astype(np.uint8)
        return Image.fromarray(array)
    
    def _base64_to_tensor(self, base64_str):
        """Convert base64 string to tensor"""
        img_data = base64.b64decode(base64_str)
        pil_image = Image.open(BytesIO(img_data))
        
        array = np.array(pil_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(array)
        
        # Add batch dimension
        return tensor.unsqueeze(0)
```

## 4. Custom Widget Node

Node with custom UI components:

```python
class ColorPaletteNode:
    """
    Generate color palettes with custom UI.
    Demonstrates custom widgets and client-server communication.
    """
    
    def __init__(self):
        self.colors = []
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "palette_size": ("INT", {
                    "default": 5,
                    "min": 2,
                    "max": 10
                }),
                "base_color": ("STRING", {
                    "default": "#ff0000",
                    "multiline": False,
                    "tooltip": "Base color in hex format"
                }),
                "harmony_type": ([
                    "complementary",
                    "analogous",
                    "triadic",
                    "split_complementary",
                    "monochromatic"
                ], {"default": "complementary"}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("palette_image", "color_list")
    FUNCTION = "generate_palette"
    CATEGORY = "color/palette"
    
    def generate_palette(self, palette_size, base_color, harmony_type, unique_id):
        # Convert hex to RGB
        base_rgb = self._hex_to_rgb(base_color)
        
        # Generate palette based on harmony type
        colors = self._generate_colors(base_rgb, harmony_type, palette_size)
        
        # Create palette image
        palette_image = self._create_palette_image(colors)
        
        # Create color list string
        color_list = json.dumps([self._rgb_to_hex(c) for c in colors])
        
        # Send to frontend for custom display
        from server import PromptServer
        PromptServer.instance.send_sync(
            "color_palette.update",
            {
                "node_id": unique_id,
                "colors": [self._rgb_to_hex(c) for c in colors]
            }
        )
        
        return (palette_image, color_list)
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb):
        """Convert RGB tuple to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
    
    def _generate_colors(self, base_rgb, harmony_type, count):
        """Generate color harmony"""
        import colorsys
        
        # Convert to HSV for easier manipulation
        h, s, v = colorsys.rgb_to_hsv(*base_rgb)
        colors = [base_rgb]
        
        if harmony_type == "complementary":
            # Add complementary color
            comp_h = (h + 0.5) % 1.0
            colors.append(colorsys.hsv_to_rgb(comp_h, s, v))
            
            # Fill rest with variations
            for i in range(2, count):
                var_s = s * (0.5 + (i / count) * 0.5)
                var_v = v * (0.5 + (i / count) * 0.5)
                colors.append(colorsys.hsv_to_rgb(h if i % 2 == 0 else comp_h, var_s, var_v))
                
        elif harmony_type == "analogous":
            # Colors adjacent on color wheel
            step = 0.083  # 30 degrees
            for i in range(1, count):
                new_h = (h + step * (i - count//2)) % 1.0
                colors.append(colorsys.hsv_to_rgb(new_h, s, v))
                
        elif harmony_type == "triadic":
            # Three colors equally spaced
            colors.append(colorsys.hsv_to_rgb((h + 0.333) % 1.0, s, v))
            colors.append(colorsys.hsv_to_rgb((h + 0.667) % 1.0, s, v))
            
            # Fill rest with variations
            for i in range(3, count):
                idx = i % 3
                base_h = [h, (h + 0.333) % 1.0, (h + 0.667) % 1.0][idx]
                var_s = s * (0.7 + (i / count) * 0.3)
                colors.append(colorsys.hsv_to_rgb(base_h, var_s, v))
                
        elif harmony_type == "split_complementary":
            # Base + two colors adjacent to complement
            comp_h = (h + 0.5) % 1.0
            colors.append(colorsys.hsv_to_rgb((comp_h - 0.083) % 1.0, s, v))
            colors.append(colorsys.hsv_to_rgb((comp_h + 0.083) % 1.0, s, v))
            
            # Fill rest
            for i in range(3, count):
                var_v = v * (0.5 + (i / count) * 0.5)
                colors.append(colorsys.hsv_to_rgb(h, s, var_v))
                
        else:  # monochromatic
            # Variations in saturation and value
            for i in range(1, count):
                var_s = s * (i / count)
                var_v = v * (0.3 + (i / count) * 0.7)
                colors.append(colorsys.hsv_to_rgb(h, var_s, var_v))
        
        return colors[:count]
    
    def _create_palette_image(self, colors):
        """Create visual representation of palette"""
        swatch_width = 128
        swatch_height = 128
        
        width = swatch_width * len(colors)
        height = swatch_height
        
        # Create image tensor
        image = torch.zeros(1, height, width, 3)
        
        for i, color in enumerate(colors):
            x_start = i * swatch_width
            x_end = (i + 1) * swatch_width
            
            for c in range(3):
                image[0, :, x_start:x_end, c] = color[c]
        
        return image
```

## 5. Data Processing Node

Process non-image data:

```python
class DataAnalysisNode:
    """
    Analyze and visualize data from various sources.
    Demonstrates handling of non-image data types.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data": ("STRING", {
                    "multiline": True,
                    "default": "1,2,3,4,5\n2,4,6,8,10",
                    "tooltip": "CSV data or JSON array"
                }),
                "data_type": (["csv", "json", "time_series"], {
                    "default": "csv"
                }),
                "visualization": (["line_chart", "bar_chart", "scatter", "heatmap"], {
                    "default": "line_chart"
                }),
                "width": ("INT", {
                    "default": 512,
                    "min": 256,
                    "max": 2048
                }),
                "height": ("INT", {
                    "default": 512,
                    "min": 256,
                    "max": 2048
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("visualization", "statistics")
    FUNCTION = "analyze_data"
    CATEGORY = "data/analysis"
    
    def analyze_data(self, data, data_type, visualization, width, height):
        # Parse data
        parsed_data = self._parse_data(data, data_type)
        
        # Calculate statistics
        stats = self._calculate_statistics(parsed_data)
        
        # Create visualization
        vis_image = self._create_visualization(
            parsed_data, visualization, width, height
        )
        
        # Format statistics as JSON
        stats_json = json.dumps(stats, indent=2)
        
        return (vis_image, stats_json)
    
    def _parse_data(self, data, data_type):
        """Parse input data based on type"""
        if data_type == "csv":
            lines = data.strip().split('\n')
            parsed = []
            for line in lines:
                values = [float(x.strip()) for x in line.split(',')]
                parsed.append(values)
            return parsed
            
        elif data_type == "json":
            return json.loads(data)
            
        else:  # time_series
            values = [float(x.strip()) for x in data.split(',')]
            return [list(range(len(values))), values]
    
    def _calculate_statistics(self, data):
        """Calculate basic statistics"""
        import statistics
        
        flat_data = []
        for row in data:
            if isinstance(row, list):
                flat_data.extend(row)
            else:
                flat_data.append(row)
        
        if not flat_data:
            return {}
        
        return {
            "count": len(flat_data),
            "mean": statistics.mean(flat_data),
            "median": statistics.median(flat_data),
            "stdev": statistics.stdev(flat_data) if len(flat_data) > 1 else 0,
            "min": min(flat_data),
            "max": max(flat_data)
        }
    
    def _create_visualization(self, data, vis_type, width, height):
        """Create visualization using matplotlib"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(width/100, height/100))
        
        if vis_type == "line_chart":
            for i, row in enumerate(data):
                ax.plot(row, label=f"Series {i+1}")
            ax.legend()
            
        elif vis_type == "bar_chart":
            if len(data) == 1:
                ax.bar(range(len(data[0])), data[0])
            else:
                x = np.arange(len(data[0]))
                width_bar = 0.8 / len(data)
                for i, row in enumerate(data):
                    ax.bar(x + i * width_bar, row, width_bar, label=f"Series {i+1}")
                ax.legend()
                
        elif vis_type == "scatter":
            if len(data) >= 2:
                ax.scatter(data[0], data[1])
            else:
                ax.scatter(range(len(data[0])), data[0])
                
        else:  # heatmap
            im = ax.imshow(data, cmap='viridis', aspect='auto')
            plt.colorbar(im, ax=ax)
        
        ax.set_title(f"{vis_type.replace('_', ' ').title()}")
        plt.tight_layout()
        
        # Convert to image tensor
        fig.canvas.draw()
        buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close(fig)
        
        # Convert to tensor and normalize
        tensor = torch.from_numpy(buf.copy()).float() / 255.0
        # Add batch dimension
        return tensor.unsqueeze(0)
```

## Testing Your Nodes

Create a test file to verify your nodes work correctly:

```python
# test_nodes.py
import sys
import torch
sys.path.append('../..')  # Path to ComfyUI

from custom_nodes.my_nodes import *

def test_image_filter():
    # Create test image
    test_image = torch.rand(1, 256, 256, 3)
    
    # Create node instance
    node = AdvancedImageFilter()
    
    # Test each filter type
    for filter_type in ["gaussian_blur", "edge_enhance", "emboss"]:
        result = node.apply_filter(
            image=test_image,
            filter_type=filter_type,
            strength=0.5
        )
        
        assert result[0].shape == test_image.shape
        print(f"✓ {filter_type} test passed")

if __name__ == "__main__":
    test_image_filter()
    print("All tests passed!")
```

## Next Steps

- Learn about [Frontend Integration](./06-frontend-integration.md)
- Explore [Publishing and Distribution](./07-publishing.md)
- Read [Best Practices and Tips](./08-best-practices.md)