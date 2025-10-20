#!/usr/bin/env python3
"""
Script to resize an image to 1280x720 and save it to input_reference/
"""

import os
from PIL import Image
import sys

def resize_image(input_path, output_path, target_size=(1280, 720)):
    """
    Resize an image to the target size while maintaining aspect ratio
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path to save the resized image
        target_size (tuple): Target size as (width, height)
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Get original dimensions
            original_width, original_height = img.size
            print(f"Original image size: {original_width}x{original_height}")
            
            # Calculate the scaling factor to fit within target size while maintaining aspect ratio
            scale_width = target_size[0] / original_width
            scale_height = target_size[1] / original_height
            scale = min(scale_width, scale_height)
            
            # Calculate new dimensions
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            print(f"Resizing to: {new_width}x{new_height}")
            
            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a new image with the target size and paste the resized image centered
            final_img = Image.new('RGB', target_size, (0, 0, 0))  # Black background
            
            # Calculate position to center the image
            x_offset = (target_size[0] - new_width) // 2
            y_offset = (target_size[1] - new_height) // 2
            
            # Paste the resized image onto the final image
            final_img.paste(resized_img, (x_offset, y_offset))
            
            # Save the final image
            final_img.save(output_path, 'JPEG', quality=95)
            print(f"Image saved to: {output_path}")
            
    except Exception as e:
        print(f"Error processing image: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Check if image path is provided as command line argument
    if len(sys.argv) > 1:
        input_image = sys.argv[1]
    else:
        # Look for common image files in current directory
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        input_image = None
        
        for file in os.listdir('.'):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                input_image = file
                break
        
        if not input_image:
            print("No image file found. Please provide the path to the image as an argument:")
            print("python resize_image.py path/to/your/image.jpg")
            sys.exit(1)
    
    # Ensure input_reference directory exists
    output_dir = "/Users/recarnot/dev/Sora2/input_reference"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename based on input filename
    base_name = os.path.splitext(os.path.basename(input_image))[0]
    output_image = os.path.join(output_dir, f"{base_name}_1280x720.jpg")
    
    print(f"Processing image: {input_image}")
    print(f"Output will be saved to: {output_image}")
    
    if resize_image(input_image, output_image):
        print("✅ Image resizing completed successfully!")
    else:
        print("❌ Failed to resize image.")
