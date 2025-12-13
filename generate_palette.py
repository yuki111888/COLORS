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
    """Generate lighter and darker shades of a color with proper progression.
    
    Shade 500 is always the base color. Lighter shades (50-400) interpolate
    between white and the base. Darker shades (600-900) interpolate between
    the base and black.
    """
    rgb = hex_to_rgb(hex_color)
    r, g, b = [x / 255.0 for x in rgb]
    h, base_l, base_s = colorsys.rgb_to_hls(r, g, b)
    
    shades = {}
    
    # Shade 500 is always the base color
    shades['500'] = hex_color
    
    # Calculate lighter shades (50-400) by interpolating from white (1.0) to base
    # We use a curve that gives more variation near white
    lighter_ratios = {
        '50': 0.05,   # Very close to white
        '100': 0.15,  # Close to white
        '200': 0.30,  # Getting closer to base
        '300': 0.50,  # Midway
        '400': 0.70   # Close to base
    }
    
    for shade_name, ratio in lighter_ratios.items():
        # Interpolate: white (1.0) -> base (base_l)
        # ratio of 0.0 = white, ratio of 1.0 = base
        lightness = 1.0 - (1.0 - base_l) * ratio
        
        # Ensure we stay above base_l and below 1.0
        lightness = min(0.99, max(base_l + 0.01, lightness))
        
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, lightness, base_s)
        new_rgb = tuple(int(x * 255) for x in (new_r, new_g, new_b))
        shades[shade_name] = rgb_to_hex(new_rgb)
    
    # Calculate darker shades (600-900) by interpolating from base to black (0.0)
    darker_ratios = {
        '600': 0.30,  # Close to base
        '700': 0.50,  # Midway
        '800': 0.70,  # Getting darker
        '900': 0.85   # Very dark
    }
    
    for shade_name, ratio in darker_ratios.items():
        # Interpolate: base (base_l) -> black (0.0)
        # ratio of 0.0 = base, ratio of 1.0 = black
        lightness = base_l * (1.0 - ratio)
        
        # Ensure we stay below base_l and above 0.0
        lightness = max(0.01, min(base_l - 0.01, lightness))
        
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, lightness, base_s)
        new_rgb = tuple(int(x * 255) for x in (new_r, new_g, new_b))
        shades[shade_name] = rgb_to_hex(new_rgb)
    
    # Return in order
    return {name: shades[name] for name in ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900']}

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
    <title>yuki colors</title>
    <link rel="stylesheet" href="palette.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Droid Sans Mono', 'Source Code Pro', 'Courier New', monospace;
            background: #0A0A0A;
            color: #fff;
            padding: 0;
            overflow-x: hidden;
        }
        
        .header {
            padding: 0.5rem 1rem;
            background: #0A0A0A;
            border-bottom: 1px solid #1a1a1a;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header h1 {
            font-size: 1rem;
            font-weight: normal;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #888;
        }
        
        .palette-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0;
        }
        
        .color-block {
            position: relative;
            aspect-ratio: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: transform 0.1s, z-index 0.1s;
            border: none;
        }
        
        .color-block:hover:not(.expanded) {
            transform: scale(1.05);
            z-index: 10;
            box-shadow: 0 0 20px rgba(255,255,255,0.1);
        }
        
        .color-block.expanded {
            z-index: 15;
        }
        
        .color-name {
            font-size: 0.7rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.3rem;
            text-shadow: 0 0 10px rgba(0,0,0,0.8);
        }
        
        .color-hex {
            font-size: 0.65rem;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Droid Sans Mono', 'Source Code Pro', 'Courier New', monospace;
            text-shadow: 0 0 10px rgba(0,0,0,0.8);
        }
        
        .shades-backdrop {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            z-index: 19;
            opacity: 0;
            transition: opacity 0.3s ease-out;
        }
        
        .color-block.expanded .shades-backdrop {
            display: block;
            opacity: 1;
        }
        
        .shades-container {
            display: none;
            position: fixed;
            top: auto;
            left: 0;
            right: 0;
            width: 100vw;
            background: #0A0A0A;
            border-top: 1px solid #1a1a1a;
            border-bottom: 1px solid #1a1a1a;
            z-index: 20;
            grid-template-columns: repeat(10, 1fr);
            gap: 0;
            padding: 0.5rem 0;
            max-width: 100%;
            opacity: 0;
            transform: translateY(-20px);
            transition: opacity 0.3s ease-out, transform 0.3s ease-out;
        }
        
        .color-block.expanded .shades-container {
            display: grid;
            opacity: 1;
            transform: translateY(0);
        }
        
        .palette-grid {
            position: relative;
        }
        
        .shade-block {
            aspect-ratio: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            border: none;
            min-height: 100px;
        }
        
        .shade-label {
            font-size: 0.6rem;
            margin-bottom: 0.3rem;
            text-shadow: 0 0 5px rgba(0,0,0,0.8);
            font-weight: bold;
        }
        
        .shade-hex {
            font-size: 0.55rem;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Droid Sans Mono', 'Source Code Pro', 'Courier New', monospace;
            text-shadow: 0 0 5px rgba(0,0,0,0.8);
        }
        
        .palette-image-section {
            margin-top: 0;
            padding: 0.5rem 1rem;
            background: #0A0A0A;
            border-top: 1px solid #1a1a1a;
        }
        
        .palette-image-section h2 {
            font-size: 0.7rem;
            font-weight: normal;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #888;
            margin-bottom: 0.5rem;
        }
        
        .image-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .btn {
            padding: 0.3rem 0.6rem;
            border: 1px solid #333;
            background: #1a1a1a;
            color: #fff;
            cursor: pointer;
            font-size: 0.65rem;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Droid Sans Mono', 'Source Code Pro', 'Courier New', monospace;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.2s;
        }
        
        .btn:hover {
            background: #2a2a2a;
            border-color: #444;
        }
        
        .btn:active {
            transform: scale(0.95);
        }
        
        .toast {
            position: fixed;
            bottom: 1rem;
            right: 1rem;
            background: #1a1a1a;
            color: #fff;
            padding: 0.5rem 1rem;
            border: 1px solid #333;
            font-size: 0.7rem;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Droid Sans Mono', 'Source Code Pro', 'Courier New', monospace;
            opacity: 0;
            transform: translateY(10px);
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
    <div class="header">
        <h1>COLOR PALETTE</h1>
    </div>
    <div class="palette-grid" id="paletteGrid">
        <div id="toast" class="toast"></div>
"""
    
    for color in colors:
        name_slug = color['name'].lower().replace(' ', '-')
        shades = generate_shades(color['hex'], color['name'])
        text_color = get_text_color(color['hex'])
        
        html += f"""
        <div class="color-block" style="background-color: {color['hex']};" onclick="toggleShades(this, event)">
            <div class="color-name" style="color: {text_color};">{color['name']}</div>
            <div class="color-hex" style="color: {text_color};">{color['hex'].upper()}</div>
            <div class="shades-backdrop"></div>
            <div class="shades-container" onclick="event.stopPropagation()">
"""
        for shade_name, shade_hex in shades.items():
            shade_text_color = get_text_color(shade_hex)
            html += f"""
                <div class="shade-block" style="background-color: {shade_hex};" onclick="event.stopPropagation(); copyHex('{shade_hex}')">
                    <div class="shade-label" style="color: {shade_text_color};">{shade_name}</div>
                    <div class="shade-hex" style="color: {shade_text_color};">{shade_hex.upper()}</div>
                </div>
"""
        html += """
            </div>
        </div>
"""
    
    # Add palette image section
    if len(colors) > 0:
        html += """
    </div>
    <div class="palette-image-section">
        <h2>PALETTE IMAGE</h2>
        <div class="image-actions">
            <button class="btn" onclick="copyImage('palette.png')">COPY IMAGE</button>
            <button class="btn" onclick="downloadImage('palette.png', 'color_palette.png')">DOWNLOAD IMAGE</button>
        </div>
    </div>
"""
    
    html += """
    <script>
        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2000);
        }
        
        function closeAllShades() {
            document.querySelectorAll('.color-block.expanded').forEach(block => {
                block.classList.remove('expanded');
            });
        }
        
        function toggleShades(element, event) {
            // Stop event propagation to prevent backdrop clicks from toggling
            if (event) {
                event.stopPropagation();
            }
            
            // Close all other expanded blocks
            document.querySelectorAll('.color-block.expanded').forEach(block => {
                if (block !== element) {
                    block.classList.remove('expanded');
                }
            });
            
            // Toggle current block
            element.classList.toggle('expanded');
            
            // Position shades container below the clicked block
            if (element.classList.contains('expanded')) {
                const shadesContainer = element.querySelector('.shades-container');
                const rect = element.getBoundingClientRect();
                shadesContainer.style.top = (rect.bottom + window.scrollY) + 'px';
            }
        }
        
        // Close modal when clicking on backdrop or outside
        document.addEventListener('click', function(event) {
            const expandedBlock = document.querySelector('.color-block.expanded');
            if (expandedBlock) {
                const backdrop = expandedBlock.querySelector('.shades-backdrop');
                const shadesContainer = expandedBlock.querySelector('.shades-container');
                const colorName = expandedBlock.querySelector('.color-name');
                const colorHex = expandedBlock.querySelector('.color-hex');
                
                // Close if clicking on backdrop or outside the modal
                if (backdrop && backdrop.contains(event.target)) {
                    expandedBlock.classList.remove('expanded');
                } else if (!shadesContainer.contains(event.target) && 
                          !colorName.contains(event.target) && 
                          !colorHex.contains(event.target) &&
                          !expandedBlock.contains(event.target)) {
                    expandedBlock.classList.remove('expanded');
                }
            }
        });
        
        // Close shades on Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeAllShades();
            }
        });
        
        function copyHex(hex) {
            navigator.clipboard.writeText(hex).then(() => {
                showToast('Copied: ' + hex);
            });
        }
        
        async function copyImage(imagePath) {
            try {
                const response = await fetch(imagePath);
                const blob = await response.blob();
                await navigator.clipboard.write([
                    new ClipboardItem({ [blob.type]: blob })
                ]);
                showToast('Image copied!');
            } catch (err) {
                console.error('Failed to copy image:', err);
                showToast('Copy failed. Try download.');
            }
        }
        
        function downloadImage(imagePath, filename) {
            const link = document.createElement('a');
            link.href = imagePath;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            showToast('Downloaded!');
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
    
    # Image dimensions - use higher resolution for better text quality
    scale = 2  # 2x scale for retina quality
    width = 200 * scale
    height = 200 * scale
    
    # Create image filled with the color (no white background)
    img = Image.new('RGB', (width, height), color=color['hex'])
    draw = ImageDraw.Draw(img)
    
    # Determine text color based on background brightness
    text_color = get_text_color(color['hex'])
    shadow_color = '#000000' if text_color == '#FFFFFF' else '#FFFFFF'
    
    # Try to find a good monospace font
    font_paths = [
        "/System/Library/Fonts/SF-Mono-Regular.otf",  # macOS SF Mono
        "/System/Library/Fonts/Monaco.ttf",  # macOS Monaco
        "/Library/Fonts/Consolas.ttf",  # Windows Consolas (if installed)
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
        "/System/Library/Fonts/Helvetica.ttc",  # Fallback
    ]
    
    name_font = None
    hex_font = None
    
    for font_path in font_paths:
        try:
            name_font = ImageFont.truetype(font_path, 24 * scale)
            hex_font = ImageFont.truetype(font_path, 20 * scale)
            break
        except:
            continue
    
    # If no font found, try default
    if name_font is None:
        try:
            name_font = ImageFont.load_default()
            hex_font = ImageFont.load_default()
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
    total_text_height = name_height + hex_height + (8 * scale)
    start_y = (height - total_text_height) // 2
    
    # Draw name text (centered) with shadow
    name_x = (width - name_width) // 2
    name_y = start_y
    shadow_offset = 2 * scale
    draw.text((name_x + shadow_offset, name_y + shadow_offset), name_text, fill=shadow_color, font=name_font)
    draw.text((name_x, name_y), name_text, fill=text_color, font=name_font)
    
    # Draw hex text (centered, below name) with shadow
    hex_x = (width - hex_width) // 2
    hex_y = start_y + name_height + (8 * scale)
    draw.text((hex_x + shadow_offset, hex_y + shadow_offset), hex_text, fill=shadow_color, font=hex_font)
    draw.text((hex_x, hex_y), hex_text, fill=text_color, font=hex_font)
    
    # Resize back to original size with high-quality resampling
    img = img.resize((200, 200), Image.Resampling.LANCZOS)
    
    # Save image with high quality
    img.save(output_path, 'PNG', optimize=False)
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
    
    # Use higher resolution for better text quality
    scale = 2  # 2x scale for retina quality
    swatch_width = 200 * scale
    swatch_height = 200 * scale
    
    # Total image size (no spacing between squares)
    total_width = cols * swatch_width
    total_height = rows * swatch_height
    
    # Create image (will be filled by individual squares)
    img = Image.new('RGB', (total_width, total_height))
    draw = ImageDraw.Draw(img)
    
    # Try to find a good monospace font
    font_paths = [
        "/System/Library/Fonts/SF-Mono-Regular.otf",  # macOS SF Mono
        "/System/Library/Fonts/Monaco.ttf",  # macOS Monaco
        "/Library/Fonts/Consolas.ttf",  # Windows Consolas (if installed)
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
        "/System/Library/Fonts/Helvetica.ttc",  # Fallback
    ]
    
    name_font = None
    hex_font = None
    
    for font_path in font_paths:
        try:
            name_font = ImageFont.truetype(font_path, 20 * scale)
            hex_font = ImageFont.truetype(font_path, 18 * scale)
            break
        except:
            continue
    
    # If no font found, try default
    if name_font is None:
        try:
            name_font = ImageFont.load_default()
            hex_font = ImageFont.load_default()
        except:
            name_font = ImageFont.load_default()
            hex_font = ImageFont.load_default()
    
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
        total_text_height = name_height + hex_height + (6 * scale)
        start_y = y + (swatch_height - total_text_height) // 2
        
        # Draw name text (centered in this square) with shadow
        name_x = x + (swatch_width - name_width) // 2
        name_y = start_y
        shadow_offset = 2 * scale
        draw.text((name_x + shadow_offset, name_y + shadow_offset), name_text, fill=shadow_color, font=name_font)
        draw.text((name_x, name_y), name_text, fill=text_color, font=name_font)
        
        # Draw hex text (centered, below name) with shadow
        hex_x = x + (swatch_width - hex_width) // 2
        hex_y = start_y + name_height + (6 * scale)
        draw.text((hex_x + shadow_offset, hex_y + shadow_offset), hex_text, fill=shadow_color, font=hex_font)
        draw.text((hex_x, hex_y), hex_text, fill=text_color, font=hex_font)
    
    # Resize back to original size with high-quality resampling
    final_width = cols * 200
    final_height = rows * 200
    img = img.resize((final_width, final_height), Image.Resampling.LANCZOS)
    
    # Save image with high quality
    img.save(output_path, 'PNG', optimize=False)
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
    with open('index.html', 'w') as f:
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
    print("  - index.html (Visual preview)")
    print("  - GUIDELINES.md (Brand guidelines)")
    print("  - tailwind.config.js (Tailwind CSS configuration)")
    if HAS_PIL:
        print("  - Individual color swatch images (.png)")
        print("  - Complete palette image (palette.png)")
    print("\nOpen index.html in your browser to see the palette!")

if __name__ == '__main__':
    main()

