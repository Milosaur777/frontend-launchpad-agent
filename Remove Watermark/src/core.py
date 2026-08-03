"""Batch processing engine — runs watermark removal + AVIF conversion in background."""

from __future__ import annotations

import enum
import queue
import threading
from datetime import datetime, timezone
from pathlib import Path

from config import SUPPORTED_FORMATS


class BatchState(enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    CANCELLED = "cancelled"
    DONE = "done"


class BatchOptions:
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        visible: bool = True,
        metadata: bool = True,
        invisible: bool = True,
        gpu_available: bool = False,
        gpu_type: str = "cpu",
        avif: bool = False,
        avif_quality: int = 75,
        selected_files: list[Path] | None = None,
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.visible = visible
        self.metadata = metadata
        self.invisible = invisible
        self.gpu_available = gpu_available
        self.gpu_type = gpu_type
        self.avif = avif
        self.avif_quality = avif_quality
        self.selected_files = selected_files


def scan_images(directory: Path) -> list[Path]:
    files = []
    for f in sorted(directory.iterdir()):
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS:
            files.append(f)
    return files


def _next_available(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


class BatchEngine:
    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._state = BatchState.IDLE
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.progress_queue: queue.Queue[tuple[int, int]] = queue.Queue()
        self.file_done_queue: queue.Queue[Path] = queue.Queue()
        self.overwrite_choice: str | None = None
        self.overwrite_event = threading.Event()
        self.overwrite_pending = False
        self.overwrite_filename: str = ""
        self.cancelled_files: set[str] = set()

    @property
    def state(self) -> BatchState:
        return self._state

    def request_overwrite(self, filename: str) -> str:
        self.cancelled_files.discard(filename)
        self.overwrite_choice = None
        self.overwrite_event.clear()
        self.overwrite_pending = True
        self.overwrite_filename = filename
        self.log_queue.put(f"[{ts()}] ⚠  File exists: {filename} — awaiting user decision")
        self.overwrite_event.wait()
        return self.overwrite_choice or "cancel"

    def respond_overwrite(self, choice: str) -> None:
        self.overwrite_choice = choice
        self.overwrite_pending = False
        self.overwrite_event.set()

    def cancel(self) -> None:
        self._stop_event.set()

    def start(self, options: BatchOptions) -> None:
        if self._state == BatchState.RUNNING:
            return
        self._stop_event.clear()
        self.cancelled_files.clear()
        self._state = BatchState.RUNNING
        self._thread = threading.Thread(
            target=self._run, args=(options,), daemon=True
        )
        self._thread.start()

    def _run(self, options: BatchOptions) -> None:
        # Use selected files if provided, otherwise scan directory
        if options.selected_files:
            files = options.selected_files
        else:
            files = scan_images(options.input_dir)
        total = len(files)

        if total == 0:
            self.log_queue.put(f"[{ts()}] No images found in {options.input_dir}")
            self._state = BatchState.DONE
            return

        options.output_dir.mkdir(parents=True, exist_ok=True)

        self.log_queue.put(f"[{ts()}] Found {total} image(s)")
        self.log_queue.put(f"[{ts()}] Input:  {options.input_dir}")
        self.log_queue.put(f"[{ts()}] Output: {options.output_dir}")
        modes = []
        if options.visible: modes.append("Visible")
        if options.metadata: modes.append("Metadata")
        if options.invisible: modes.append("Invisible")
        if options.avif: modes.append(f"AVIF (q={options.avif_quality})")
        self.log_queue.put(f"[{ts()}] Modes: {', '.join(modes) if modes else 'None'}")
        self.log_queue.put(f"[{ts()}] " + "─" * 50)

        processed = 0
        skipped = 0
        errors = 0

        for i, filepath in enumerate(files, 1):
            if self._stop_event.is_set():
                self.log_queue.put(f"[{ts()}] ❌ Batch cancelled by user")
                self._state = BatchState.CANCELLED
                return

            out_path = self._resolve_output(filepath, options)
            if out_path is None:
                skipped += 1
                processed += 1
                self.progress_queue.put((processed, total))
                continue

            self.log_queue.put(
                f"[{ts()}] [{i}/{total}] Processing {filepath.name}..."
            )

            try:
                self._process_single(filepath, out_path, options)
                self.log_queue.put(
                    f"[{ts()}] ✅  {filepath.name}  →  {out_path.name}"
                )
                self.file_done_queue.put(out_path)
            except Exception as exc:
                self.log_queue.put(
                    f"[{ts()}] ❌  {filepath.name}  FAILED: {exc}"
                )
                errors += 1

            processed += 1
            self.progress_queue.put((processed, total))

        self.log_queue.put(f"[{ts()}] " + "─" * 50)
        self.log_queue.put(
            f"[{ts()}] Done! {processed - skipped - errors} cleaned, "
            f"{skipped} skipped, {errors} errors"
        )
        self._state = BatchState.DONE

    def _resolve_output(self, src: Path, options: BatchOptions) -> Path | None:
        out = options.output_dir / src.name
        if not out.exists():
            return out

        self.overwrite_choice = None
        self.overwrite_event.clear()
        self.overwrite_pending = True
        self.overwrite_filename = src.name
        self.log_queue.put(
            f"[{ts()}] ⚠  File exists: {src.name} — awaiting user decision"
        )
        self.overwrite_event.wait(timeout=120)

        choice = self.overwrite_choice
        self.overwrite_pending = False
        if choice == "overwrite":
            return out
        elif choice == "number":
            return _next_available(out)
        else:
            self._stop_event.set()
            return None

    def _process_single(self, src: Path, dst: Path, options: BatchOptions) -> None:
        """Process a single image through the pipeline."""
        import cv2

        img = cv2.imread(str(src))
        if img is None:
            raise ValueError(f"Cannot read image: {src}")

        # Step 1: Visible watermarks
        if options.visible:
            try:
                from remove_ai_watermarks.gemini_engine import GeminiEngine
                engine = GeminiEngine()
                result = engine.detect_watermark(img)
                if result and result.detected:
                    img = engine.remove_watermark(img)
                    self.log_queue.put(f"[{ts()}]    → Visible watermark removed")
            except ImportError:
                self.log_queue.put(f"[{ts()}]    → remove-ai-watermarks not installed")
            except Exception as e:
                self.log_queue.put(f"[{ts()}]    → Visible pass error: {e}")

        # Step 2: Invisible watermarks (GPU only)
        if options.invisible and options.gpu_available:
            try:
                from remove_ai_watermarks.invisible_engine import InvisibleEngine
                ie = InvisibleEngine(pipeline="controlnet")
                temp_in = dst.parent / f"_temp_{dst.name}"
                temp_out = dst.parent / f"_temp_out_{dst.name}"
                cv2.imwrite(str(temp_in), img)
                ie.remove_watermark(temp_in, temp_out)
                regenerated = cv2.imread(str(temp_out))
                if regenerated is not None:
                    img = regenerated
                    self.log_queue.put(f"[{ts()}]    → Invisible watermark removed")
                temp_in.unlink(missing_ok=True)
                temp_out.unlink(missing_ok=True)
            except ImportError:
                pass
            except Exception as e:
                self.log_queue.put(f"[{ts()}]    → Invisible pass error: {e}")

        # Step 3: Metadata stripping
        if options.metadata:
            try:
                from remove_ai_watermarks.metadata import has_ai_metadata, remove_ai_metadata
                if has_ai_metadata(dst):
                    remove_ai_metadata(dst, dst)
                    self.log_queue.put(f"[{ts()}]    → Metadata stripped")
            except ImportError:
                pass
            except Exception:
                pass

        # Step 4: Save (or AVIF conversion)
        if options.avif:
            try:
                from PIL import Image as PILImage
                # Convert BGR to RGB
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = PILImage.fromarray(rgb_img)
                # Change extension to .avif
                avif_dst = dst.with_suffix(".avif")
                pil_img.save(str(avif_dst), "AVIF", quality=options.avif_quality)
                self.log_queue.put(
                    f"[{ts()}]    → Converted to AVIF (q={options.avif_quality})"
                )
            except ImportError:
                # Pillow not available, save original
                cv2.imwrite(str(dst), img)
                self.log_queue.put(f"[{ts()}]    → Pillow not installed, saved original format")
            except Exception as e:
                cv2.imwrite(str(dst), img)
                self.log_queue.put(f"[{ts()}]    → AVIF failed ({e}), saved original")
        else:
            cv2.imwrite(str(dst), img)

    def process_single_preview(self, src: Path, tmp_dir: Path) -> Path | None:
        try:
            import cv2
            tmp_dir.mkdir(parents=True, exist_ok=True)
            dst = tmp_dir / f"preview_{src.name}"

            img = cv2.imread(str(src))
            if img is None:
                return None

            try:
                from remove_ai_watermarks.gemini_engine import GeminiEngine
                engine = GeminiEngine()
                result = engine.detect_watermark(img)
                if result and result.detected:
                    img = engine.remove_watermark(img)
            except ImportError:
                pass

            cv2.imwrite(str(dst), img)
            return dst
        except Exception:
            return None


def ts() -> str:
    return datetime.now(tz=timezone.utc).strftime("%H:%M:%S")
