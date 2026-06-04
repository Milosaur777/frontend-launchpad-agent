# Web Image Optimization

Every image used on any web page must be converted to **AVIF** format.

## Size Targets

| Source size | Target size | Quality |
|---|---|---|
| >500kb | ≤60kb | 50-60% |
| ≤500kb | ≤80% of original | 70-80% |

## Requirements

- Convert all raster images (PNG, JPG, WebP) to `.avif`
- Preserve aspect ratio
- Strip EXIF metadata
- Use `sharp` or `squoosh` CLI — never ship raw PNG/JPEG
- Use `next/image` with AVIF format in `format` prop where available
- Add descriptive `alt` text on every image

## Conversion Commands

```bash
# sharp
npx sharp input.jpg --avif --quality 55 -o output.avif

# ImageMagick
magick input.jpg -quality 55 -define heic:target-size=60k output.avif

# squoosh (npm install -g @squoosh/cli)
npx @squoosh/cli --avif '{"quality":55}' input.jpg
```

## Browser Support

AVIF has 95%+ global browser support. Only provide `<picture>` fallback if IE11 is required:

```html
<picture>
  <source srcset="image.avif" type="image/avif" />
  <img src="image.jpg" alt="description" />
</picture>
```
