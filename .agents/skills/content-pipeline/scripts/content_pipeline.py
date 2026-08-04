#!/usr/bin/env python3
"""
Content Pipeline — Scrape → Transcribe → Summarize → Obsidian
Orchestrates yt-dlp, Whisper, LLM, and Obsidian vault writes.

Usage:
    python content_pipeline.py youtube --playlist URL --vault PATH --folder FOLDER
    python content_pipeline.py instagram --username USER --vault PATH --folder FOLDER
    python content_pipeline.py web --url URL --vault PATH --folder FOLDER
    python content_pipeline.py audio --file FILE --vault PATH --folder FOLDER
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def slugify(s: str) -> str:
    """Create a filesystem-safe slug from a string."""
    s = re.sub(r"[^\w\s-]", "", s).strip()
    s = re.sub(r"[-\s]+", "-", s)
    return s.lower()[:60]


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def run_cmd(cmd: list[str], cwd: str | None = None, timeout: int = 300) -> str:
    """Run a shell command and return stdout."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"stderr: {result.stderr[:500]}")
    return result.stdout


def transcribe_audio(audio_path: str, output_dir: str, model: str = "base") -> str:
    """Transcribe audio with Whisper. Returns path to transcript file."""
    print(f"[Whisper] Transcribing {audio_path} ...")
    
    # Try faster-whisper first, fall back to openai-whisper
    try:
        from faster_whisper import WhisperModel
        
        whisper_model = WhisperModel(model, device="cpu", compute_type="int8")
        segments, info = whisper_model.transcribe(audio_path, beam_size=5)
        
        transcript_path = os.path.join(output_dir, "transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(f"# Transcript\n\n")
            f.write(f"Detected language: {info.language}\n\n")
            for seg in segments:
                f.write(f"[{seg.start:.1f}s] {seg.text.strip()}\n")
        
        print(f"[Whisper] Done: {transcript_path}")
        return transcript_path
        
    except ImportError:
        print("[Whisper] faster-whisper not found, trying openai-whisper ...")
        transcript_path = os.path.join(output_dir, "transcript.txt")
        run_cmd([
            "whisper", audio_path,
            "--model", model,
            "--output_format", "txt",
            "--output_dir", output_dir,
        ])
        # Whisper creates file next to input; move it
        base = Path(audio_path).stem
        whisper_out = Path(audio_path).parent / f"{base}.txt"
        if whisper_out.exists():
            os.rename(whisper_out, transcript_path)
        print(f"[Whisper] Done: {transcript_path}")
        return transcript_path


def read_transcript(transcript_path: str) -> str:
    with open(transcript_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_insights(transcript: str, title: str, llm_command: str | None = None) -> dict:
    """Extract insights from transcript using LLM."""
    
    prompt = f"""Analyze this transcript and return a JSON object with these keys:
- summary: one-line summary (≤20 words)
- key_points: list of 3-7 key bullet points
- quotes: list of {{text, timestamp}} best quotes
- tags: list of 5-10 keywords for tagging
- action_items: list of actionable takeaways
- related: list of related concept names for backlinks

Transcript from "{title}":

{transcript[:8000]}
"""
    
    # If an LLM CLI is available, use it. Otherwise return raw transcript for manual processing.
    if llm_command:
        print(f"[LLM] Extracting insights via {llm_command} ...")
        # This is a placeholder — integrate with your preferred LLM CLI
        return {"summary": "LLM extraction not yet automated.", "key_points": [], "quotes": [], "tags": [], "action_items": [], "related": []}
    
    # Fallback: return structure with raw transcript for manual LLM pass
    return {
        "summary": f"Transcript of '{title}'. Send to LLM for summary.",
        "key_points": ["See full transcript below."],
        "quotes": [],
        "tags": ["content-pipeline", "transcribed"],
        "action_items": [],
        "related": [],
        "_raw_transcript": transcript,
    }


def write_obsidian_note(
    title: str,
    insights: dict,
    source_url: str,
    vault_path: str,
    folder: str,
    media_embeds: list[str] | None = None,
) -> str:
    """Write a structured note to the Obsidian vault."""
    
    date = datetime.date.today().isoformat()
    slug = slugify(title)
    folder_path = os.path.join(vault_path, folder)
    ensure_dir(folder_path)
    
    filepath = os.path.join(folder_path, f"{date}-{slug}.md")
    
    # Build tags string
    tags = insights.get("tags", [])
    tags_str = json.dumps(tags)
    
    # Build related links
    related = insights.get("related", [])
    related_links = "\n".join(f"- [[{r}]]" for r in related) if related else ""
    
    # Build quotes
    quotes = insights.get("quotes", [])
    quotes_md = "\n\n".join(
        f'> "{q.get("text", q)}"' + (f" — [{q.get('timestamp', '')}]" if isinstance(q, dict) and q.get("timestamp") else "")
        for q in quotes
    ) if quotes else ""
    
    # Build action items
    actions = insights.get("action_items", [])
    actions_md = "\n".join(f"- [ ] {a}" for a in actions) if actions else ""
    
    # Media embeds
    media_md = ""
    if media_embeds:
        media_md = "\n\n## Media\n\n" + "\n".join(f"![[{m}]]" for m in media_embeds)
    
    content = f"""---
title: "{title}"
date: {date}
tags: {tags_str}
source: "{source_url}"
status: summarized
---

# {title}

## Summary
{insights.get("summary", "")}

## Key Points
{chr(10).join(f"- {p}" for p in insights.get("key_points", []))}

## Quotes
{quotes_md}

## Action Items
{actions_md}

## Related
{related_links}
{media_md}

## Transcript
<details>
<summary>Full transcript (click to expand)</summary>

```
{insights.get("_raw_transcript", "")}
```

</details>
"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[Obsidian] Note written: {filepath}")
    return filepath


# ─── Source Handlers ───


def handle_youtube(args):
    """Download YouTube video/playlist, transcribe, summarize, write to Obsidian."""
    url = args.playlist or args.video
    if not url:
        print("Error: --playlist or --video required")
        sys.exit(1)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"[yt-dlp] Downloading audio to {tmpdir} ...")
        
        cmd = [
            "yt-dlp",
            "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "-o", os.path.join(tmpdir, "%(playlist_index)s - %(title)s.%(ext)s"),
        ]
        if args.playlist:
            cmd.append("--yes-playlist")
        cmd.append(url)
        
        run_cmd(cmd, timeout=600)
        
        # Find downloaded files
        mp3_files = sorted(Path(tmpdir).glob("*.mp3"))
        if not mp3_files:
            print("No audio files downloaded.")
            sys.exit(1)
        
        for mp3 in mp3_files:
            title = mp3.stem
            print(f"\n=== Processing: {title} ===")
            
            # Transcribe
            transcript_path = transcribe_audio(str(mp3), tmpdir, model=args.whisper_model)
            transcript = read_transcript(transcript_path)
            
            # Extract insights
            insights = extract_insights(transcript, title, args.llm)
            insights["_raw_transcript"] = transcript[:50000]  # cap size
            
            # Write to Obsidian
            write_obsidian_note(
                title=title,
                insights=insights,
                source_url=url,
                vault_path=args.vault,
                folder=args.folder,
            )
            
            time.sleep(1)


def handle_instagram(args):
    """Download Instagram saved posts, extract metadata, write to Obsidian."""
    username = args.username
    vault_path = args.vault
    folder = args.folder
    
    print(f"[instaloader] Fetching saved posts for {username} ...")
    print("WARNING: Use an alt account. Never your main.")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        run_cmd([
            "instaloader",
            "--login", username,
            "--no-videos",
            "--no-captions",
            "--metadata-json",
            "--dirname-pattern", os.path.join(tmpdir, "{shortcode}"),
            ":saved",
        ], timeout=300)
        
        # Process each post
        for post_dir in sorted(Path(tmpdir).iterdir()):
            if not post_dir.is_dir():
                continue
            
            meta_file = post_dir / "metadata.json"
            if not meta_file.exists():
                continue
            
            with open(meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            caption = data.get("caption", "") or ""
            hashtags = data.get("hashtags", [])
            date = data.get("date_utc", "")[:10] if data.get("date_utc") else datetime.date.today().isoformat()
            shortcode = data.get("shortcode", post_dir.name)
            
            # Find image
            images = list(post_dir.glob("*.jpg")) + list(post_dir.glob("*.png"))
            image_embed = f"{post_dir.name}/{images[0].name}" if images else None
            
            title = f"Instagram — {caption[:50]}..." if len(caption) > 50 else f"Instagram — {caption}"
            if not caption:
                title = f"Instagram Post — {shortcode}"
            
            insights = {
                "summary": caption[:200] if caption else "No caption.",
                "key_points": [f"Hashtags: {', '.join(f'#{h}' for h in hashtags[:10])}"] if hashtags else [],
                "quotes": [],
                "tags": ["instagram", "saved"] + hashtags[:8],
                "action_items": [],
                "related": [],
            }
            
            media_embeds = [image_embed] if image_embed else None
            
            write_obsidian_note(
                title=title,
                insights=insights,
                source_url=f"https://instagram.com/p/{shortcode}",
                vault_path=vault_path,
                folder=folder,
                media_embeds=media_embeds,
            )


def handle_web(args):
    """Scrape web article with Crawl4AI, summarize, write to Obsidian."""
    url = args.url
    vault_path = args.vault
    folder = args.folder
    
    print(f"[crawl4ai] Scraping {url} ...")
    
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        import asyncio
        
        async def scrape():
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
                return result.markdown
        
        markdown = asyncio.run(scrape())
        
    except ImportError:
        print("crawl4ai not installed. Install with: pip install crawl4ai")
        sys.exit(1)
    
    # Derive title from first heading or URL
    title = url
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    
    insights = {
        "summary": f"Web article scraped from {url}.",
        "key_points": ["See full content in transcript section."],
        "quotes": [],
        "tags": ["article", "web"],
        "action_items": [],
        "related": [],
        "_raw_transcript": markdown[:50000],
    }
    
    write_obsidian_note(
        title=title,
        insights=insights,
        source_url=url,
        vault_path=vault_path,
        folder=folder,
    )


def handle_audio(args):
    """Transcribe local audio file, summarize, write to Obsidian."""
    audio_path = args.file
    title = args.title or Path(audio_path).stem
    
    with tempfile.TemporaryDirectory() as tmpdir:
        transcript_path = transcribe_audio(audio_path, tmpdir, model=args.whisper_model)
        transcript = read_transcript(transcript_path)
        
        insights = extract_insights(transcript, title, args.llm)
        insights["_raw_transcript"] = transcript[:50000]
        
        write_obsidian_note(
            title=title,
            insights=insights,
            source_url=f"file://{audio_path}",
            vault_path=args.vault,
            folder=args.folder,
        )


# ─── CLI ───


def main():
    parser = argparse.ArgumentParser(description="Content Pipeline — scrape, transcribe, summarize, Obsidian")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Global args
    def add_common(p):
        p.add_argument("--vault", required=True, help="Path to Obsidian vault root")
        p.add_argument("--folder", default="Content Pipeline", help="Target folder inside vault")
        p.add_argument("--llm", default=None, help="LLM CLI command for insight extraction (optional)")
        p.add_argument("--whisper-model", default="base", help="Whisper model size (tiny/base/small/medium/large)")
    
    # YouTube
    yt = subparsers.add_parser("youtube", help="Process YouTube video or playlist")
    yt_group = yt.add_mutually_exclusive_group(required=True)
    yt_group.add_argument("--playlist", help="YouTube playlist URL")
    yt_group.add_argument("--video", help="Single YouTube video URL")
    add_common(yt)
    
    # Instagram
    ig = subparsers.add_parser("instagram", help="Process Instagram saved collection")
    ig.add_argument("--username", required=True, help="Instagram username (alt account)")
    add_common(ig)
    
    # Web
    web = subparsers.add_parser("web", help="Scrape web article")
    web.add_argument("--url", required=True, help="Article URL")
    add_common(web)
    
    # Audio
    aud = subparsers.add_parser("audio", help="Transcribe local audio file")
    aud.add_argument("--file", required=True, help="Path to audio file")
    aud.add_argument("--title", help="Note title (default: filename)")
    add_common(aud)
    
    args = parser.parse_args()
    
    if args.command == "youtube":
        handle_youtube(args)
    elif args.command == "instagram":
        handle_instagram(args)
    elif args.command == "web":
        handle_web(args)
    elif args.command == "audio":
        handle_audio(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
