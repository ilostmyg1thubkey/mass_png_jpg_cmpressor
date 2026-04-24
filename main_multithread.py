#!/usr/bin/env python3
"""
Parallel Recursive Image Processor
Refactored for multi-process concurrency to efficiently handle CPU-bound image operations.
"""

import argparse
import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Tuple

from PIL import Image
from PIL.Image import Resampling

# ---------------------------------------------------------------------------
# Configuration Constants
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = frozenset({".png", ".jpeg", ".jpg"})
MAX_SIDE_THRESHOLD = 7000
MAX_FILENAME_LENGTH = 126
APPEND_SUFFIX = "edit_by_compress"
TARGET_FORMAT = "WEBP"
WEBP_QUALITY = 80
WEBP_METHOD = 5

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-7s] %(message)s",
    datefmt="%H:%M:%S",
    force=True,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Worker Function (Must be module-level for multiprocessing pickling)
# ---------------------------------------------------------------------------
def process_single_image(img_path: Path,webp_quality:int,webp_compress_metod:int) -> Tuple[Path, bool, str]:
    """
    Worker function that processes a single image file.
    Handles resizing, format conversion, renaming, saving, and safe deletion.
    Returns a tuple of (original_path, success_bool, error_message).
    """
    try:
        with Image.open(img_path) as img:
            # 1. Conditional Resizing
            width, height = img.size
            max_dim = max(width, height)
            min_dim = min(width, height)

            if max_dim > MAX_SIDE_THRESHOLD and (max_dim - min_dim) < 2 * min_dim:
                scale_factor = MAX_SIDE_THRESHOLD / max_dim
                new_width = int(round(width * scale_factor))
                new_height = int(round(height * scale_factor))
                img = img.resize((new_width, new_height), Resampling.LANCZOS)

            # 2. Filename Modification
            original_stem = img_path.stem
            if len(original_stem) > MAX_FILENAME_LENGTH:
                original_stem = original_stem[:MAX_FILENAME_LENGTH]

            new_filename = f"{original_stem}{APPEND_SUFFIX}.webp"
            dest_path = img_path.parent / new_filename

            # 3. Format Conversion & Save (Overwrites by default)
            # Pillow automatically preserves alpha/transparency for RGBA/LA/PA modes
            img.save(
                str(dest_path),
                format=TARGET_FORMAT,
                quality=webp_quality,
                method=webp_compress_metod,
                lossless=False,
            )

        # 4. Safe Deletion (executed only after successful save & context manager exit)
        img_path.unlink(missing_ok=True)
        return img_path, True, ""

    except Image.DecompressionBombError as e:
        return img_path, False, f"Decompression bomb detected ({e})"
    except OSError as e:
        return img_path, False, f"I/O operation failed ({e})"
    except Exception as e:
        return img_path, False, f"Unexpected processing error ({e})"


# ---------------------------------------------------------------------------
# Main Orchestration Function
# ---------------------------------------------------------------------------
def process_directory(target_dir: Path, webp_quality:int ,webp_compress_metod:int, max_workers: int | None = None) -> None:
    """
    Recursively collects valid image paths and distributes them across a process pool.
    """
    if not target_dir.is_dir():
        logger.error(f"Invalid or non-existent directory: {target_dir}")
        return

    logger.info(f"Scanning: {target_dir}")
    # Eagerly collect paths to avoid filesystem iteration during parallel execution
    valid_files = [
        p for p in target_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
    ]

    if not valid_files:
        logger.info("No valid image files found in the target directory.")
        return

    logger.info(f"Found {len(valid_files)} image(s). Starting parallel processing...")
    success_count = 0
    failure_count = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Map futures to their originating paths for tracking
        future_to_path = {executor.submit(process_single_image, f,webp_quality,webp_compress_metod): f for f in valid_files}

        for future in as_completed(future_to_path):
            orig_path, success, error_msg = future.result()
            if success:
                success_count += 1
                logger.info(f"✅ Processed: {orig_path.name}")
            else:
                failure_count += 1
                logger.warning(f"❌ Failed: {orig_path.name} | Reason: {error_msg}")

    logger.info(f"Batch complete. Success: {success_count} | Failed: {failure_count}")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parallel recursive image compressor (WebP conversion)."
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Target directory path to recursively process.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes. Defaults to CPU count.",
    )

    parser.add_argument(
        "--webp_quality",
        type=int,
        default=WEBP_QUALITY,
        help=f"Webp quality 1-100. Defaults to {WEBP_QUALITY}",
    )

    parser.add_argument(
        "--webp_compress_metod",
        type=int,
        default=WEBP_METHOD,
        help=f"Number of webp compress metod 1-6. Defaults {WEBP_METHOD}",
    )
    args = parser.parse_args()
    print(args)
    
    # Optional: Adjust worker count based on available CPU cores
    if args.workers:
        os.cpu_count()  # Just a reference; ProcessPoolExecutor handles default gracefully
    process_directory(args.directory, max_workers=args.workers, webp_quality= args.webp_quality ,webp_compress_metod=args.webp_compress_metod)


if __name__ == "__main__":
    main()
