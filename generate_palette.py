#!/usr/bin/env python3
"""
Color Palette Generator
Reads colors from colors.txt and generates CSS, HTML preview, and brand guidelines.
"""

import re
import colorsys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def hex_to_hsl(hex_color):
    """Convert hex color to HSL tuple."""
    rgb = hex_to_rgb(hex_color)
    r, g, b = [x / 255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s * 100, l * 100)

def generate_shades(hex_color, name):
    """Generate lighter and darker shades of a color."""
    rgb = hex_to_rgb(hex_color)
    r, g, b = [x / 255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    
    shades = {}
    shade_names = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900']
    lightness_values = [0.95, 0.85, 0.75, 0.65, 0.55, l, 0.45, 0.35, 0.25, 0.15]
    
    for shade_name, lightness in zip(shade_names, lightness_values):
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, lightness, s)
        new_rgb = tuple(int(x * 255) for x in (new_r, new_g, new_b))
        shades[shade_name] = rgb_to_hex(new_rgb)
    
    return shades

def parse_colors_file(file_path):
    """Parse colors.txt and extract color definitions."""
    colors = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Match pattern: hex_code # name
            match = re.match(r'([0-9a-fA-F]{6})\s*#\s*(.+)', line)
            if match:
                hex_code = '#' + match.group(1).lower()
                name = match.group(2).strip()
                colors.append({
                    'hex': hex_code,
                    'name': name,
                    'rgb': hex_to_rgb(hex_code),
                    'hsl': hex_to_hsl(hex_code)
                })
    return colors

def generate_css(colors):
    """Generate CSS file with color variables."""
    css = ":root {\n"
    css += "  /* Primary Colors */\n"
    
    for color in colors:
        name_slug = color['name'].lower().replace(' ', '-')
        r, g, b = color['rgb']
        h, s, l = color['hsl']
        
        css += f"  --color-{name_slug}: {color['hex']};\n"
        css += f"  --color-{name_slug}-rgb: {r}, {g}, {b};\n"
        css += f"  --color-{name_slug}-hsl: {h:.1f}, {s:.1f}%, {l:.1f}%;\n"
        
        # Generate shades
        shades = generate_shades(color['hex'], color['name'])
        css += f"\n  /* {color['name']} Shades */\n"
        for shade_name, shade_hex in shades.items():
            css += f"  --color-{name_slug}-{shade_name}: {shade_hex};\n"
    
    css += "}\n\n"
    
    # Generate utility classes
    css += "/* Utility Classes */\n"
    for color in colors:
        name_slug = color['name'].lower().replace(' ', '-')
        css += f".bg-{name_slug} {{ background-color: var(--color-{name_slug}); }}\n"
        css += f".text-{name_slug} {{ color: var(--color-{name_slug}); }}\n"
        css += f".border-{name_slug} {{ border-color: var(--color-{name_slug}); }}\n"
    
    return css

def generate_html_preview(colors):
    """Generate HTML preview page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Color Palette Preview</title>
    <link rel="stylesheet" href="palette.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 2rem;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            color: #333;
            margin-bottom: 2rem;
            font-size: 2.5rem;
        }
        
        .color-group {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .color-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .color-swatch {
            width: 80px;
            height: 80px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .color-info h2 {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        
        .color-details {
            display: flex;
            gap: 1rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .shades-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .shade-item {
            text-align: center;
        }
        
        .shade-swatch {
            width: 100%;
            height: 80px;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }
        
        .shade-label {
            font-size: 0.75rem;
            color: #666;
            font-weight: 500;
        }
        
        .shade-hex {
            font-size: 0.7rem;
            color: #999;
            font-family: 'Monaco', 'Courier New', monospace;
        }
        
        code {
            background: #f0f0f0;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.85em;
        }
        
        .image-section {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid #e0e0e0;
        }
        
        .image-container {
            position: relative;
            display: block;
            margin: 1rem 0;
        }
        
        .palette-image-section .image-container {
            margin: 0;
        }
        
        .color-image {
            max-width: 100%;
            height: auto;
            display: block;
        }
        
        .palette-image-section .color-image {
            width: 100%;
            height: auto;
        }
        
        .image-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-copy {
            background: #333;
            color: white;
        }
        
        .btn-copy:hover {
            background: #555;
        }
        
        .btn-download {
            background: #4CAF50;
            color: white;
        }
        
        .btn-download:hover {
            background: #45a049;
        }
        
        .btn:active {
            transform: scale(0.98);
        }
        
        .palette-image-section {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid #e0e0e0;
        }
        
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: #333;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s;
            z-index: 1000;
        }
        
        .toast.show {
            opacity: 1;
            transform: translateY(0);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Color Palette</h1>
        <div id="toast" class="toast"></div>
"""
    
    for color in colors:
        name_slug = color['name'].lower().replace(' ', '-')
        r, g, b = color['rgb']
        h, s, l = color['hsl']
        shades = generate_shades(color['hex'], color['name'])
        
        image_filename = f"{name_slug}.png"
        html += f"""
        <div class="color-group">
            <div class="color-header">
                <div class="color-swatch" style="background-color: {color['hex']};"></div>
                <div class="color-info">
                    <h2>{color['name']}</h2>
                    <div class="color-details">
                        <span><strong>HEX:</strong> <code>{color['hex']}</code></span>
                        <span><strong>RGB:</strong> <code>rgb({r}, {g}, {b})</code></span>
                        <span><strong>HSL:</strong> <code>hsl({h:.1f}, {s:.1f}%, {l:.1f}%)</code></span>
                    </div>
                </div>
            </div>
            <div class="shades-grid">
"""
        for shade_name, shade_hex in shades.items():
            html += f"""
                <div class="shade-item">
                    <div class="shade-swatch" style="background-color: {shade_hex};"></div>
                    <div class="shade-label">{shade_name}</div>
                    <div class="shade-hex">{shade_hex}</div>
                </div>
"""
        html += f"""
            </div>
            <div class="image-section">
                <h3 style="margin-bottom: 1rem; font-size: 1.2rem;">Color Swatch</h3>
                <div class="image-container">
                    <img src="{image_filename}" alt="{color['name']} color swatch" class="color-image" id="img-{name_slug}">
                    <div class="image-actions">
                        <button class="btn btn-copy" onclick="copyImage('{image_filename}')">
                            📋 Copy Image
                        </button>
                        <button class="btn btn-download" onclick="downloadImage('{image_filename}', '{color['name'].replace(' ', '_')}_swatch.png')">
                            💾 Download Image
                        </button>
                    </div>
                </div>
            </div>
        </div>
"""
    
    # Add palette image section if multiple colors
    if len(colors) > 0:
        html += """
        <div class="color-group palette-image-section">
            <h2 style="margin-bottom: 1.5rem;">Complete Palette</h2>
            <div class="image-container">
                <img src="palette.png" alt="Complete color palette" class="color-image" id="img-palette">
                <div class="image-actions">
                    <button class="btn btn-copy" onclick="copyImage('palette.png')">
                        📋 Copy Image
                    </button>
                    <button class="btn btn-download" onclick="downloadImage('palette.png', 'color_palette.png')">
                        💾 Download Image
                    </button>
                </div>
            </div>
        </div>
"""
    
    html += """
    </div>
    <script>
        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2000);
        }
        
        async function copyImage(imagePath) {
            try {
                const response = await fetch(imagePath);
                const blob = await response.blob();
                await navigator.clipboard.write([
                    new ClipboardItem({ [blob.type]: blob })
                ]);
                showToast('Image copied to clipboard!');
            } catch (err) {
                console.error('Failed to copy image:', err);
                showToast('Failed to copy image. Try downloading instead.');
            }
        }
        
        function downloadImage(imagePath, filename) {
            const link = document.createElement('a');
            link.href = imagePath;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            showToast('Image downloaded!');
        }
    </script>
</body>
</html>
"""
    return html

def generate_guidelines(colors):
    """Generate brand guidelines document."""
    guidelines = f"""# Color Palette Brand Guidelines

## Overview
This document outlines the color palette and usage guidelines for the brand.

## Primary Colors

"""
    
    for color in colors:
        r, g, b = color['rgb']
        h, s, l = color['hsl']
        name_slug = color['name'].lower().replace(' ', '-')
        
        guidelines += f"""### {color['name']}

**Hex:** `{color['hex']}`  
**RGB:** `rgb({r}, {g}, {b})`  
**HSL:** `hsl({h:.1f}, {s:.1f}%, {l:.1f}%)`  
**CSS Variable:** `var(--color-{name_slug})`

**Usage:**
- Primary brand color
- Use for key CTAs and important elements
- Maintains brand identity

**Shades Available:**
- 50 (lightest) to 900 (darkest)
- Access via CSS variable: `var(--color-{name_slug}-[50-900])`

---

"""
    
    guidelines += """
## Usage Guidelines

### Do's
- Use primary colors for brand elements and CTAs
- Use lighter shades (50-300) for backgrounds
- Use medium shades (400-600) for primary actions
- Use darker shades (700-900) for text and emphasis
- Maintain sufficient contrast ratios for accessibility (WCAG AA minimum)

### Don'ts
- Don't use colors that clash with the brand palette
- Don't use colors at full opacity on light backgrounds without consideration
- Don't mix too many colors in a single design
- Don't use dark shades on dark backgrounds

## CSS Usage

Import the palette CSS file:
```css
@import 'palette.css';
```

Use CSS variables:
```css
.my-element {
    background-color: var(--color-fire-red);
    color: var(--color-fire-red-900);
}
```

Use utility classes:
```html
<div class="bg-fire-red text-white">Content</div>
```

## Accessibility

All color combinations should meet WCAG 2.1 Level AA contrast requirements:
- Normal text: 4.5:1 contrast ratio
- Large text: 3:1 contrast ratio
- UI components: 3:1 contrast ratio

Test your color combinations using tools like:
- WebAIM Contrast Checker
- Chrome DevTools Accessibility panel
"""
    
    return guidelines

def generate_tailwind_config(colors):
    """Generate Tailwind CSS configuration file."""
    config = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [],
  theme: {
    extend: {
      colors: {
"""
    
    for color in colors:
        name_slug = color['name'].lower().replace(' ', '-')
        shades = generate_shades(color['hex'], color['name'])
        
        config += f"        '{name_slug}': {{\n"
        for shade_name, shade_hex in shades.items():
            # Remove # from hex for Tailwind
            hex_without_hash = shade_hex.lstrip('#')
            config += f"          '{shade_name}': '#{hex_without_hash}',\n"
        config += "        },\n"
    
    config += """      },
    },
  },
  plugins: [],
}
"""
    return config

def get_text_color(hex_color):
    """Determine if text should be white or black based on color brightness."""
    rgb = hex_to_rgb(hex_color)
    # Calculate relative luminance
    r, g, b = [x / 255.0 for x in rgb]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return '#FFFFFF' if luminance < 0.5 else '#000000'

def generate_color_image(color, output_path):
    """Generate a color swatch image with name and hex code on the square, no white space."""
    if not HAS_PIL:
        return False
    
    # Image dimensions
    width = 200
    height = 200
    
    # Create image filled with the color (no white background)
    img = Image.new('RGB', (width, height), color=color['hex'])
    draw = ImageDraw.Draw(img)
    
    # Determine text color based on background brightness
    text_color = get_text_color(color['hex'])
    shadow_color = '#000000' if text_color == '#FFFFFF' else '#FFFFFF'
    
    # Fonts for name and hex
    try:
        name_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        hex_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except:
        try:
            name_font = ImageFont.truetype("arial.ttf", 20)
            hex_font = ImageFont.truetype("arial.ttf", 18)
        except:
            name_font = ImageFont.load_default()
            hex_font = ImageFont.load_default()
    
    # Get text dimensions
    name_text = color['name'].upper()
    hex_text = color['hex'].upper()
    
    name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
    hex_bbox = draw.textbbox((0, 0), hex_text, font=hex_font)
    
    name_width = name_bbox[2] - name_bbox[0]
    name_height = name_bbox[3] - name_bbox[1]
    hex_width = hex_bbox[2] - hex_bbox[0]
    hex_height = hex_bbox[3] - hex_bbox[1]
    
    # Total text height with spacing
    total_text_height = name_height + hex_height + 8
    start_y = (height - total_text_height) // 2
    
    # Draw name text (centered)
    name_x = (width - name_width) // 2
    name_y = start_y
    draw.text((name_x + 2, name_y + 2), name_text, fill=shadow_color, font=name_font)
    draw.text((name_x, name_y), name_text, fill=text_color, font=name_font)
    
    # Draw hex text (centered, below name)
    hex_x = (width - hex_width) // 2
    hex_y = start_y + name_height + 8
    draw.text((hex_x + 2, hex_y + 2), hex_text, fill=shadow_color, font=hex_font)
    draw.text((hex_x, hex_y), hex_text, fill=text_color, font=hex_font)
    
    # Save image
    img.save(output_path, 'PNG', quality=95)
    return True

def generate_palette_image(colors, output_path):
    """Generate a combined palette image with all colors, no white space."""
    if not HAS_PIL:
        return False
    
    num_colors = len(colors)
    if num_colors == 0:
        return False
    
    # Calculate grid layout
    cols = min(3, num_colors)  # Max 3 columns
    rows = (num_colors + cols - 1) // cols
    
    # Individual swatch size (no spacing)
    swatch_width = 200
    swatch_height = 200
    
    # Total image size (no spacing between squares)
    total_width = cols * swatch_width
    total_height = rows * swatch_height
    
    # Create image (will be filled by individual squares)
    img = Image.new('RGB', (total_width, total_height))
    draw = ImageDraw.Draw(img)
    
    # Draw each color swatch
    for idx, color in enumerate(colors):
        row = idx // cols
        col = idx % cols
        
        x = col * swatch_width
        y = row * swatch_height
        
        # Draw color square filling entire area
        draw.rectangle(
            [x, y, x + swatch_width, y + swatch_height],
            fill=color['hex']
        )
        
        # Determine text color based on background brightness
        text_color = get_text_color(color['hex'])
        shadow_color = '#000000' if text_color == '#FFFFFF' else '#FFFFFF'
        
        # Fonts for name and hex
        try:
            name_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
            hex_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except:
            try:
                name_font = ImageFont.truetype("arial.ttf", 18)
                hex_font = ImageFont.truetype("arial.ttf", 16)
            except:
                name_font = ImageFont.load_default()
                hex_font = ImageFont.load_default()
        
        # Get text dimensions
        name_text = color['name'].upper()
        hex_text = color['hex'].upper()
        
        name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
        hex_bbox = draw.textbbox((0, 0), hex_text, font=hex_font)
        
        name_width = name_bbox[2] - name_bbox[0]
        name_height = name_bbox[3] - name_bbox[1]
        hex_width = hex_bbox[2] - hex_bbox[0]
        hex_height = hex_bbox[3] - hex_bbox[1]
        
        # Total text height with spacing
        total_text_height = name_height + hex_height + 6
        start_y = y + (swatch_height - total_text_height) // 2
        
        # Draw name text (centered in this square)
        name_x = x + (swatch_width - name_width) // 2
        name_y = start_y
        draw.text((name_x + 2, name_y + 2), name_text, fill=shadow_color, font=name_font)
        draw.text((name_x, name_y), name_text, fill=text_color, font=name_font)
        
        # Draw hex text (centered, below name)
        hex_x = x + (swatch_width - hex_width) // 2
        hex_y = start_y + name_height + 6
        draw.text((hex_x + 2, hex_y + 2), hex_text, fill=shadow_color, font=hex_font)
        draw.text((hex_x, hex_y), hex_text, fill=text_color, font=hex_font)
    
    # Save image
    img.save(output_path, 'PNG', quality=95)
    return True

def main():
    """Main function to generate all files."""
    colors_file = Path('colors.txt')
    if not colors_file.exists():
        print("Error: colors.txt not found!")
        return
    
    print("Parsing colors from colors.txt...")
    colors = parse_colors_file(colors_file)
    
    if not colors:
        print("No colors found in colors.txt!")
        return
    
    print(f"Found {len(colors)} color(s)")
    
    print("Generating CSS file...")
    css_content = generate_css(colors)
    with open('palette.css', 'w') as f:
        f.write(css_content)
    
    print("Generating HTML preview...")
    html_content = generate_html_preview(colors)
    with open('preview.html', 'w') as f:
        f.write(html_content)
    
    print("Generating brand guidelines...")
    guidelines_content = generate_guidelines(colors)
    with open('GUIDELINES.md', 'w') as f:
        f.write(guidelines_content)
    
    print("Generating Tailwind config...")
    tailwind_config = generate_tailwind_config(colors)
    with open('tailwind.config.js', 'w') as f:
        f.write(tailwind_config)
    
    # Generate images if PIL is available
    if HAS_PIL:
        print("Generating color swatch images...")
        for color in colors:
            name_slug = color['name'].lower().replace(' ', '-')
            image_path = f"{name_slug}.png"
            if generate_color_image(color, image_path):
                print(f"  ✓ Generated {image_path}")
        
        print("Generating palette image...")
        if generate_palette_image(colors, 'palette.png'):
            print("  ✓ Generated palette.png")
    else:
        print("\n⚠️  PIL/Pillow not installed. Skipping image generation.")
        print("   Install with: pip install Pillow")
    
    print("\n✅ All files generated successfully!")
    print("  - palette.css (CSS variables and utilities)")
    print("  - preview.html (Visual preview)")
    print("  - GUIDELINES.md (Brand guidelines)")
    print("  - tailwind.config.js (Tailwind CSS configuration)")
    if HAS_PIL:
        print("  - Individual color swatch images (.png)")
        print("  - Complete palette image (palette.png)")
    print("\nOpen preview.html in your browser to see the palette!")

if __name__ == '__main__':
    main()

