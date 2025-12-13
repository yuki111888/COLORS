# Color Palette Generator

A simple tool to generate beautiful color palettes, CSS variables, and brand guidelines from a simple text file.

## Quick Start

1. **Add your colors** to `colors.txt` in this format:
   ```
   fd0000 # fire red
   ff6b35 # sunset orange
   4ecdc4 # turquoise
   ```

2. **Generate the palette**:
   ```bash
   python3 generate_palette.py
   ```

3. **View your palette**:
   Open `preview.html` in your browser to see a visual preview of all your colors and their shades.
   - Each color has a downloadable swatch image (like Adobe's color tool)
   - Copy images to clipboard or download them locally
   - View the complete palette as a single image

## File Format

The `colors.txt` file uses a simple format:
```
[hex_code] # [color name]
```

Examples:
- `fd0000 # fire red`
- `ff6b35 # sunset orange`
- `4ecdc4 # turquoise blue`

**Note:** Hex codes should be 6 characters (no `#` prefix in the file).

## Generated Files

After running the generator, you'll get:

- **`palette.css`** - CSS variables and utility classes for all your colors
- **`preview.html`** - Interactive preview with copy/download buttons for images
- **`GUIDELINES.md`** - Brand guidelines and usage recommendations
- **`tailwind.config.js`** - Tailwind CSS configuration with your color palette
- **Individual color swatch images** - PNG files for each color (e.g., `fire-red.png`)
- **`palette.png`** - Combined image showing all colors in your palette

## Using the CSS

### CSS Variables

All colors are available as CSS variables:

```css
.my-element {
    background-color: var(--color-fire-red);
    color: var(--color-fire-red-900);
}
```

### Utility Classes

Quick utility classes are also available:

```html
<div class="bg-fire-red text-white">Content</div>
<div class="border-fire-red">Bordered element</div>
```

### Color Shades

Each color automatically generates 10 shades (50-900):
- `--color-fire-red-50` (lightest)
- `--color-fire-red-100`
- `--color-fire-red-200`
- ...
- `--color-fire-red-900` (darkest)

## Using with Tailwind CSS

The generator creates a `tailwind.config.js` file that you can use in your Tailwind projects.

### Setup

1. Copy `tailwind.config.js` to your project, or merge it into your existing Tailwind config
2. Make sure to update the `content` array with your project's file paths

### Usage

Once configured, use your colors with Tailwind utility classes:

```html
<div class="bg-fire-red-500 text-white">Primary button</div>
<div class="bg-fire-red-100 text-fire-red-900">Light background</div>
<div class="border-fire-red-300">Bordered element</div>
```

All shades (50-900) are available for each color:
- `bg-fire-red-50` through `bg-fire-red-900`
- `text-fire-red-50` through `text-fire-red-900`
- `border-fire-red-50` through `border-fire-red-900`

## Workflow

1. Discover a new color you love
2. Add it to `colors.txt` with a descriptive name
3. Run `python3 generate_palette.py`
4. Check `preview.html` to see how it looks
5. Use the CSS variables in your projects!

## Tips

- Use descriptive names for your colors (e.g., "fire red" instead of "red1")
- The generator automatically creates harmonious shades for each color
- All shades are calculated to maintain color harmony
- Check `GUIDELINES.md` for accessibility and usage recommendations

## Requirements

- Python 3.6+
- Pillow (for image generation): `pip install Pillow`

**Note:** The script will work without Pillow, but image generation will be skipped. Install Pillow to generate color swatch images.

