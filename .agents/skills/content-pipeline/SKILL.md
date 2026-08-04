---
name: content-pipeline
description: |
  Scrape YouTube playlists, Instagram saved collections, podcasts, or web articles;
  transcribe audio with Whisper; extract key insights with LLM; write structured
  summaries to Obsidian vault with tags, backlinks, and folder organization.
---

# Content Pipeline — Scrape → Transcribe → Summarize → Obsidian

End-to-end pipeline for turning any content (YouTube, Instagram, podcasts, web) into structured, searchable Obsidian notes.

## When to Use

- Saving YouTube playlists for offline reference and quick recall
- Archiving Instagram saved posts/collections before they disappear
- Processing podcast episodes into searchable bullet points
- Building a personal knowledge base from web research
- Creating summary decks from long-form video content

## Architecture

```
Input Source (URL / playlist / collection)
    ↓
[Downloader]  yt-dlp (YouTube/audio)  |  instaloader (Instagram)  |  crawl4ai (web)
    ↓
[Transcriber]  openai-whisper / faster-whisper  (audio → text)
    ↓
[Extractor]  LLM (key points, quotes, topics, action items)
    ↓
[Formatter]  Markdown with frontmatter, tags, backlinks
    ↓
[Sink]  Obsidian MCP  |  direct vault path  |  stdout
```

## Prerequisites

```bash
# Audio pipeline
pip install yt-dlp openai-whisper

# Optional: faster-whisper (4× speed, same accuracy)
pip install faster-whisper

# Instagram (if needed)
pip install instaloader

# Web scraping (already installed via Crawl4AI)
# crawl4ai is available globally
```

## Pipeline A — YouTube Playlist to Obsidian

### Step 1 — Download Audio

```bash
# Single video
yt-dlp -x --audio-format mp3 --audio-quality 0 \
  -o "%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"

# Entire playlist
yt-dlp -x --audio-format mp3 --audio-quality 0 \
  -o "%(playlist_index)s - %(title)s.%(ext)s" \
  --yes-playlist \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

Flags:
- `-x` extract audio only
- `--audio-quality 0` best quality
- `--yes-playlist` download all items

### Step 2 — Transcribe with Whisper

```bash
# Standard Whisper (CPU, accurate)
whisper "01 - Video Title.mp3" --model medium --language en --output_format txt

# Faster Whisper (GPU recommended, 4× speed)
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cuda', compute_type='float16')
segments, info = model.transcribe('01 - Video Title.mp3', beam_size=5)
with open('transcript.txt', 'w', encoding='utf-8') as f:
    for seg in segments:
        f.write(f'[{seg.start:.1f}s] {seg.text}\n')
"
```

### Step 3 — Extract Insights with LLM

Prompt template (send transcript to LLM):

```
Analyze this transcript and extract:
1. **One-line summary** (≤20 words)
2. **Key points** (3-7 bullets)
3. **Best quotes** (verbatim, with timestamps)
4. **Topics / tags** (5-10 keywords)
5. **Action items** (if any)
6. **Related concepts** (for backlinks)

Transcript:
[PASTE]
```

### Step 4 — Write to Obsidian

Option 1 — Obsidian MCP (if vault is connected):
Use `obsidian` MCP tools to create note with proper path.

Option 2 — Direct file write (vault path known):

```python
import datetime
import re

def slugify(s):
    return re.sub(r'[^\w\s-]', '', s).strip().replace(' ', '-').lower()[:60]

def write_obsidian_note(title, content, tags, vault_path, folder="Content Pipeline"):
    slug = slugify(title)
    date = datetime.date.today().isoformat()
    filepath = f"{vault_path}/{folder}/{date}-{slug}.md"
    
    frontmatter = f"""---
title: "{title}"
date: {date}
tags: {tags}
source: "YouTube"
status: summarized
---

"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    return filepath
```

## Pipeline B — Instagram Saved Collection

### Step 1 — Export Saved Posts

```bash
# Log in with alt account (NEVER main account)
instaloader --login ALT_USERNAME --filename-pattern={date_utc}_{shortcode} \
  --no-videos --no-captions --metadata-json \
  :saved
```

This downloads:
- Images from saved posts
- `metadata.json` per post with caption, hashtags, date, location

### Step 2 — Batch Process

```python
import json, glob, os

for meta_file in glob.glob("*/metadata.json"):
    with open(meta_file) as f:
        data = json.load(f)
    
    caption = data.get("caption", "")
    hashtags = data.get("hashtags", [])
    date = data.get("date_utc", "")[:10]
    
    # Send caption to LLM for summary
    # Write to Obsidian with image embed
    note = f"""## Caption
{caption}

## Hashtags
{', '.join(f'#{h}' for h in hashtags)}

## Image
![[{os.path.basename(os.path.dirname(meta_file))}.jpg]]
"""
```

## Pipeline C — Web Article → Obsidian

Using Crawl4AI (already installed):

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
import asyncio

async def scrape_article(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown

# Then send markdown to LLM for summary, write to Obsidian
```

## Pipeline D — Podcast / Audio File

Same as Pipeline A Steps 2-4. Just point Whisper at the audio file instead of yt-dlp output.

## Automated Orchestration Script

`scripts/content_pipeline.py` (included in this skill) provides:

```bash
# YouTube playlist → Obsidian
python content_pipeline.py youtube \
  --playlist "https://youtube.com/playlist?list=..." \
  --vault "F:/10. Setup/8. Backup/Obsidian Notes/Evergreen" \
  --folder "Learning/YouTube"

# Instagram saved → Obsidian
python content_pipeline.py instagram \
  --username ALT_USERNAME \
  --vault ".../Evergreen" \
  --folder "Content/Instagram"

# Single web article → Obsidian
python content_pipeline.py web \
  --url "https://..." \
  --vault ".../Evergreen" \
  --folder "Articles"
```

## Output Format (Obsidian Note)

```markdown
---
title: "The Art of Web Design — Fireship"
date: 2025-08-04
tags: [web-design, css, youtube, frontend]
source: "https://youtube.com/watch?v=..."
status: summarized
---

# The Art of Web Design — Fireship

## Summary
A 10-minute crash course on modern CSS layout techniques including Grid, Container Queries, and Subgrid.

## Key Points
- CSS Grid is now supported in 96% of browsers — safe to use in production
- Container Queries let components respond to their own width, not viewport
- Subgrid enables nested grids to align across parent tracks
- `:has()` selector unlocks parent-selection logic without JS

## Quotes
> "Grid is no longer the future. It's the present." — [2:14]

## Action Items
- [ ] Refactor dashboard layout to use Container Queries
- [ ] Test Subgrid in Safari TP

## Related
- [[CSS Grid Mastery]]
- [[Container Queries Deep Dive]]
- #web-design #css #youtube
```

## Safety & Ethics

| Rule | Why |
|---|---|
| Use alt accounts for Instagram | Ban risk — platforms detect scrapers |
| Never scrape private content | Violates ToS and privacy |
| Respect robots.txt for web | Good citizenship |
| Keep downloaded audio local | Don't redistribute copyrighted content |
| Rate-limit requests | Add `sleep(1-3)` between API calls |

## Quick Reference

| Task | Command |
|---|---|
| Download YouTube audio | `yt-dlp -x --audio-format mp3 URL` |
| Transcribe audio | `whisper file.mp3 --model medium` |
| Scrape web article | `crawl4ai` Python API |
| Instagram saved | `instaloader --login USER :saved` |
| Write to Obsidian | MCP `obsidian` or direct file write |

## Dependencies

- `yt-dlp` — YouTube/audio downloader
- `openai-whisper` or `faster-whisper` — Transcription
- `instaloader` — Instagram scraping
- `crawl4ai` — Web scraping (already installed)
- Obsidian MCP or direct vault access
