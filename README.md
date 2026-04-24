
# 🖼️ Parallel WebP Image Compressor
![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-green) ![Status: Stable](https://img.shields.io/badge/Status-Stable-success)

## 📖 Description
A high-performance, multi-process CLI utility that recursively traverses directories to conditionally resize, convert, and compress images into WebP format. Optimized for modern multi-core systems, it safely handles I/O operations, preserves transparency, and manages original files with atomic deletion logic.

## ✨ Features
- **Parallel Processing:** Leverages `ProcessPoolExecutor` to bypass Python's GIL, utilizing all available CPU cores for maximum throughput.
- **Conditional Resizing:** Automatically scales down images exceeding 7000px on the largest side while maintaining strict aspect ratios and skipping extreme aspect ratios.
- **Lossy WebP Conversion:** Encodes images using `quality=80` and `compression_method=5` by default, with full CLI configurability.
- **Transparency Preservation:** Natively maintains alpha channels for PNG inputs without manual color-mode conversion.
- **Safe Atomic I/O:** Writes to a local temporary buffer before copying to the target directory, ensuring compatibility with FUSE/MTP mounts (e.g., GVFS, Android devices) and preventing `[Errno 95]` syscall rejections.
- **Filename Sanitization:** Truncates names exceeding 126 characters and appends a customizable suffix (`edit_by_compress`) before safely overwriting existing files.

## 📦 Installation
This project requires Python 3.10+ and the `Pillow` library.

```bash
# Clone the repository
git clone https://github.com/your-username/parallel-webp-compressor.git
cd parallel-webp-compressor

# Install the sole dependency
pip install Pillow
```

## 🚀 Usage
Run the script directly from the command line. Specify the target directory and optional worker count.

```bash
# Basic usage (uses all available CPU cores)
python main_multithread.py /path/to/images/

# Advanced usage with custom workers and compression settings
python main_multithread.py /path/to/images/ --workers 8 --webp_quality 90 --webp_compress_method 6
```

## ⚙️ Configuration & CLI Arguments
| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `directory` | `Path` | *(Required)* | Target directory to recursively scan and process. |
| `--workers` | `int` | `os.cpu_count()` | Number of parallel worker processes. |
| `--webp_quality` | `int` | `80` | WebP encoding quality (1-100). Lower values yield smaller files. |
| `--webp_compress_method` | `int` | `5` | WebP compression effort (0-6). Higher values are slower but produce smaller files. |

> **Note:** The original image file is only deleted *after* the WebP file has been successfully verified and written to the target directory.

## 🤝 Contributing
Contributions are highly encouraged! Please follow these steps:
1. Fork the repository and create your feature branch (`git checkout -b feature/amazing-feature`).
2. Ensure your code adheres to PEP 8 standards and includes comprehensive type hints.
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request detailing your changes and testing methodology.

## 📄 License
Distributed under the **MIT License**. See `LICENSE` for more information.
