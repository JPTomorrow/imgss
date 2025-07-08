#!/usr/bin/env python3
"""
Image Atlas Generator
Creates a texture atlas from multiple images in a directory.
Supports .png, .jpeg, .jpg, .webm, and .webp formats.
"""

import os
import sys
import math
from PIL import Image
import argparse
from typing import List, Tuple, Dict

class ImageAtlasGenerator:
    def __init__(self, input_dir: str, output_path: str, output_name: str, sprite_width: int, sprite_height: int, atlas_width: int, atlas_height: int):
        self.input_dir = input_dir
        self.output_path = output_path
        self.output_name = output_name
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.atlas_width = atlas_width
        self.atlas_height = atlas_height
        self.supported_formats = {'.png', '.jpeg', '.jpg', '.webm', '.webp'}
        
    def get_image_files(self) -> List[str]:
        """Get all supported image files from the input directory."""
        image_files = []
        
        if not os.path.exists(self.input_dir):
            raise FileNotFoundError(f"Input directory '{self.input_dir}' does not exist")
            
        for filename in os.listdir(self.input_dir):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in self.supported_formats:
                image_files.append(os.path.join(self.input_dir, filename))
                
        return sorted(image_files)
    
    def calculate_grid_size(self, num_images: int) -> Tuple[int, int]:
        """Calculate optimal grid dimensions for the given number of images."""
        if num_images == 0:
            return 1, 1
            
        # Try to make the grid as square as possible
        # cols = math.ceil(math.sqrt(num_images))
        cols = math.floor(math.sqrt((self.atlas_width / self.sprite_width) * num_images))
        print(cols)
        rows = math.ceil(num_images / cols)
        
        return cols, rows
    
    def resize_image_to_fit(self, image: Image.Image, cell_width: int, cell_height: int) -> Image.Image:
        """Resize image to fit within cell dimensions while maintaining aspect ratio."""
        # Calculate scaling factor to fit within cell
        scale_x = cell_width / image.width
        scale_y = cell_height / image.height
        scale = min(scale_x, scale_y)
        
        # Calculate new dimensions
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        
        # Resize image
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def create_atlas(self) -> Dict[str, Dict]:
        """Create the texture atlas and return mapping information."""
        image_files = self.get_image_files()
        
        if not image_files:
            raise ValueError("No supported image files found in the input directory")
            
        print(f"Found {len(image_files)} images to process")
        
        # Calculate grid dimensions
        cols, rows = self.calculate_grid_size(len(image_files))
        print(f"Using {cols}x{rows} grid layout")
        
        # Calculate cell dimensions
        # cell_width = self.atlas_width // cols
        # cell_height = self.atlas_height // rows
        cell_width = self.sprite_width
        cell_height = self.sprite_height
        
        print(f"Each cell will be {cell_width}x{cell_height} pixels")
        
        # Create the atlas canvas
        atlas = Image.new('RGBA', (self.atlas_width, self.atlas_height), (0, 0, 0, 0))
        
        # Store mapping information
        atlas_mapping = {}
        
        # Process each image
        for i, image_path in enumerate(image_files):
            try:
                # Calculate grid position
                col = i % cols
                row = i // cols
                
                # Calculate position in atlas
                x = col * cell_width
                y = row * cell_height
                
                # Load and process image
                print(f"Processing: {os.path.basename(image_path)}")
                
                with Image.open(image_path) as img:
                    # Convert to RGBA if necessary
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # Resize to fit cell
                    resized_img = self.resize_image_to_fit(img, cell_width, cell_height)
                    
                    # Center the image in the cell
                    paste_x = x + (cell_width - resized_img.width) // 2
                    paste_y = y + (cell_height - resized_img.height) // 2
                    
                    # Paste into atlas
                    atlas.paste(resized_img, (paste_x, paste_y), resized_img)
                    
                    # Store mapping information
                    filename = os.path.basename(image_path)
                    atlas_mapping[filename] = {
                        'x': paste_x,
                        'y': paste_y,
                        'width': resized_img.width,
                        'height': resized_img.height,
                        'cell_x': x,
                        'cell_y': y,
                        'cell_width': cell_width,
                        'cell_height': cell_height,
                        'original_size': (img.width, img.height)
                    }
                    
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                continue
        
        # Save the atlas
        atlas.save(self.output_path + ("" if self.output_path.endswith("/") else "/") + self.output_name + "-atlus.png", 'PNG')
        print(f"Atlas saved to: {self.output_path}")
        
        return atlas_mapping
    
    def save_mapping_file(self, mapping: Dict[str, Dict], mapping_path: str = None):
        """Save the atlas mapping information to a file."""
        if mapping_path is None:
            mapping_path = os.path.splitext(self.output_path)[0] + '_mapping.txt'
        
        with open(mapping_path, 'w') as f:
            f.write("# Image Atlas Mapping\n")
            f.write(f"# Atlas Size: {self.atlas_width}x{self.atlas_height}\n")
            f.write("# Format: filename | x, y, width, height | cell_x, cell_y, cell_width, cell_height | original_width, original_height\n\n")
            
            for filename, info in mapping.items():
                f.write(f"{filename} | {info['x']}, {info['y']}, {info['width']}, {info['height']} | "
                       f"{info['cell_x']}, {info['cell_y']}, {info['cell_width']}, {info['cell_height']} | "
                       f"{info['original_size'][0]}, {info['original_size'][1]}\n")
        
        print(f"Mapping file saved to: {mapping_path}")

def main():
    parser = argparse.ArgumentParser(description='Create a texture atlas from multiple images')
    parser.add_argument('input_dir', help='Directory containing input images')
    parser.add_argument('output_path', help='Output path for the atlas PNG file')
    parser.add_argument('output_name', help='Name for the atlas PNG file')
    parser.add_argument('--sprite-width', type=int, default=32, help='individual sprite width in pixels (default: 32)')
    parser.add_argument('--sprite-height', type=int, default=32, help='individual sprite height in pixels (default: 32)')
    parser.add_argument('--width', type=int, default=512, help='Atlas width in pixels (default: 512)')
    parser.add_argument('--height', type=int, default=512, help='Atlas height in pixels (default: 512)')
    parser.add_argument('--mapping', help='Path to save mapping file (default: output_path with _mapping.txt suffix)')
    
    args = parser.parse_args()
    
    try:
        # Create atlas generator
        generator = ImageAtlasGenerator(
            input_dir=args.input_dir,
            output_path=args.output_path,
            output_name=args.output_name,
            sprite_width=args.sprite_width,
            sprite_height=args.sprite_height,
            atlas_width=args.width,
            atlas_height=args.height
        )
        
        # Generate atlas
        mapping = generator.create_atlas()
        
        # Save mapping file
        generator.save_mapping_file(mapping, args.mapping)
        
        print("\nAtlas generation complete!")
        print(f"- Atlas: {args.output_path}")
        print(f"- Processed {len(mapping)} images")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()