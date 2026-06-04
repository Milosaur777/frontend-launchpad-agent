<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Image Optimization Rule (Mandatory)

Every image used on any web page **must** be converted to **AVIF** format. Rules:

- **Convert all raster images** (PNG, JPG, WebP) to `.avif`
- **Source >500kb → target ≤60kb** by lowering quality to 50-60%
- **Source ≤500kb → target ≤80% of original** with quality 70-80%
- Use `sharp` or `squoosh` CLI for conversion — never ship raw PNG/JPEG
- Preserve aspect ratio; strip EXIF metadata
- AVIF support: 95%+ of modern browsers — provide `<picture>` fallback only if IE11 is required

```bash
# Example with sharp (Node.js)
npx sharp input.jpg --avif --quality 55 -o output.avif

# Example with ImageMagick
magick input.jpg -quality 55 -define heic:target-size=60k output.avif
```
