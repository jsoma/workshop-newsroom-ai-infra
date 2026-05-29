#!/usr/bin/env python
"""Benchmark local GLM-OCR on one page from a PDF in data/pdfs."""

from __future__ import annotations

import argparse
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

import fitz


PDF_DIR = Path("data/pdfs")
DEFAULT_MODEL_ID = "zai-org/GLM-OCR"
DEFAULT_PROMPT = "Text Recognition:"


@dataclass
class PreparedPage:
    pdf_path: Path
    page_number: int
    image_path: Path
    image_width: int
    image_height: int
    render_seconds: float
    image_size_bytes: int


def resolve_pdf_path(value: str | None) -> Path:
    if value:
        candidate = Path(value)
        if not candidate.exists():
            candidate = PDF_DIR / value
    else:
        pdfs = sorted(PDF_DIR.glob("*.pdf"))
        if not pdfs:
            raise SystemExit(f"No PDFs found in {PDF_DIR}")
        candidate = pdfs[0]

    if not candidate.exists():
        raise SystemExit(f"PDF not found: {candidate}")
    if candidate.suffix.lower() != ".pdf":
        raise SystemExit(f"Expected a PDF file, got: {candidate}")

    return candidate


def render_page(
    pdf_path: Path,
    page_number: int,
    dpi: int,
    image_format: str,
    jpeg_quality: int,
    output_dir: Path,
) -> PreparedPage:
    render_started = time.perf_counter()
    with fitz.open(pdf_path) as pdf:
        if page_number < 1 or page_number > pdf.page_count:
            raise SystemExit(
                f"Page {page_number} is outside the PDF range 1-{pdf.page_count}"
            )

        page = pdf.load_page(page_number - 1)
        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(dpi / 72, dpi / 72),
            alpha=False,
        )

    image_path = output_dir / f"{pdf_path.stem}-page-{page_number}.{image_format}"
    if image_format == "jpeg":
        image_bytes = pixmap.tobytes("jpeg", jpg_quality=jpeg_quality)
    else:
        image_bytes = pixmap.tobytes("png")

    image_path.write_bytes(image_bytes)
    render_seconds = time.perf_counter() - render_started

    return PreparedPage(
        pdf_path=pdf_path,
        page_number=page_number,
        image_path=image_path,
        image_width=pixmap.width,
        image_height=pixmap.height,
        render_seconds=render_seconds,
        image_size_bytes=len(image_bytes),
    )


def select_device(torch_module, requested: str) -> str:
    if requested != "auto":
        return requested
    if torch_module.cuda.is_available():
        return "cuda"
    if (
        hasattr(torch_module.backends, "mps")
        and torch_module.backends.mps.is_available()
    ):
        return "mps"
    return "cpu"


def select_dtype(torch_module, requested: str, device: str):
    if requested == "float32":
        return torch_module.float32
    if requested == "float16":
        return torch_module.float16
    if requested == "bfloat16":
        return torch_module.bfloat16
    if device == "cuda":
        return (
            torch_module.bfloat16
            if torch_module.cuda.is_bf16_supported()
            else torch_module.float16
        )
    if device == "mps":
        return torch_module.float16
    return torch_module.float32


def sync_device(torch_module, device: str) -> None:
    if device == "cuda":
        torch_module.cuda.synchronize()
    elif device == "mps" and hasattr(torch_module, "mps"):
        torch_module.mps.synchronize()


def describe_device(torch_module, device: str) -> str:
    if device == "cuda":
        index = torch_module.cuda.current_device()
        name = torch_module.cuda.get_device_name(index)
        free_bytes, total_bytes = torch_module.cuda.mem_get_info(index)
        total_gb = total_bytes / 1_000_000_000
        free_gb = free_bytes / 1_000_000_000
        return f"cuda:{index} ({name}, {free_gb:.1f}/{total_gb:.1f} GB free)"
    if device == "mps":
        return "mps (Apple Metal)"
    return device


def load_glm_ocr(model_id: str, device: str, dtype_name: str):
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor

    torch_dtype = select_dtype(torch, dtype_name, device)

    load_started = time.perf_counter()
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForImageTextToText.from_pretrained(
        model_id,
        dtype=torch_dtype,
        low_cpu_mem_usage=True,
    )
    model = model.to(device)
    model.eval()
    sync_device(torch, device)
    load_seconds = time.perf_counter() - load_started

    return processor, model, torch, torch_dtype, load_seconds


def run_glm_ocr(
    processor,
    model,
    torch_module,
    device: str,
    image_path: Path,
    prompt: str,
    max_new_tokens: int,
) -> tuple[str, float, float]:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "url": str(image_path)},
                {"type": "text", "text": prompt},
            ],
        }
    ]

    preprocess_started = time.perf_counter()
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    inputs.pop("token_type_ids", None)
    sync_device(torch_module, device)
    preprocess_seconds = time.perf_counter() - preprocess_started

    generate_started = time.perf_counter()
    with torch_module.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )
    sync_device(torch_module, device)
    generate_seconds = time.perf_counter() - generate_started

    input_token_count = inputs["input_ids"].shape[1]
    generated_text = processor.decode(
        generated_ids[0][input_token_count:],
        skip_special_tokens=True,
    ).strip()

    return generated_text, preprocess_seconds, generate_seconds


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OCR one page from data/pdfs with GLM-OCR and report timing.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--pdf",
        help="PDF path, or a filename inside data/pdfs. Defaults to the first PDF.",
    )
    parser.add_argument("--page", type=positive_int, default=1)
    parser.add_argument(
        "--dpi",
        type=positive_int,
        default=150,
        help="Lower DPI is much faster locally; raise it for small text or scans.",
    )
    parser.add_argument(
        "--image-format",
        choices=["jpeg", "png"],
        default="jpeg",
        help="JPEG is smaller; PNG can preserve sharper scans.",
    )
    parser.add_argument("--jpeg-quality", type=positive_int, default=85)
    parser.add_argument("--runs", type=positive_int, default=1)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "mps", "cuda"],
        default="auto",
        help="Local inference device. auto prefers CUDA, then Apple MPS, then CPU.",
    )
    parser.add_argument(
        "--dtype",
        choices=["auto", "float32", "float16", "bfloat16"],
        default="auto",
        help="Model dtype. auto uses fp16 on GPU/MPS and fp32 on CPU.",
    )
    parser.add_argument("--max-new-tokens", type=positive_int, default=4096)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--tmp-dir",
        type=Path,
        default=Path(".glm-ocr-benchmark"),
        help="Where to write the rendered page image.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to save the OCR markdown from the last run.",
    )
    parser.add_argument(
        "--preview-chars",
        type=int,
        default=1200,
        help="Number of OCR characters to print after timing. Use 0 to suppress.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render the page, but skip model loading and OCR.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pdf_path = resolve_pdf_path(args.pdf)
    args.tmp_dir.mkdir(parents=True, exist_ok=True)
    page = render_page(
        pdf_path=pdf_path,
        page_number=args.page,
        dpi=args.dpi,
        image_format=args.image_format,
        jpeg_quality=args.jpeg_quality,
        output_dir=args.tmp_dir,
    )

    image_mb = page.image_size_bytes / 1_000_000

    print(f"PDF: {page.pdf_path}")
    print(f"Page: {page.page_number}")
    print(
        f"Rendered image: {page.image_width}x{page.image_height} "
        f"{args.image_format} ({image_mb:.2f} MB)"
    )
    print(f"Image path: {page.image_path}")
    print(f"Render: {page.render_seconds:.3f}s")

    if args.dry_run:
        print("Dry run: skipped local model load and OCR.")
        return

    import torch

    device = select_device(torch, args.device)
    print(f"Model: {args.model_id}")
    print(f"Device: {describe_device(torch, device)}")

    processor, model, torch_module, torch_dtype, load_seconds = load_glm_ocr(
        model_id=args.model_id,
        device=device,
        dtype_name=args.dtype,
    )
    print(f"Dtype: {torch_dtype}")
    print(f"Model load: {load_seconds:.3f}s")

    preprocess_times: list[float] = []
    generate_times: list[float] = []
    markdown = ""

    for index in range(1, args.runs + 1):
        markdown, preprocess_seconds, generate_seconds = run_glm_ocr(
            processor=processor,
            model=model,
            torch_module=torch_module,
            device=device,
            image_path=page.image_path,
            prompt=args.prompt,
            max_new_tokens=args.max_new_tokens,
        )
        preprocess_times.append(preprocess_seconds)
        generate_times.append(generate_seconds)
        run_seconds = preprocess_seconds + generate_seconds

        print(
            f"Run {index}: preprocess {preprocess_seconds:.3f}s, "
            f"generate {generate_seconds:.3f}s, "
            f"total {run_seconds:.3f}s "
            f"({1 / run_seconds:.2f} pages/sec warm), "
            f"{len(markdown):,} markdown chars"
        )

    first_total = page.render_seconds + load_seconds + preprocess_times[0] + generate_times[0]
    print(f"Cold total with render+model load+OCR: {first_total:.3f}s")
    print(f"Cold throughput: {1 / first_total:.2f} pages/sec")

    if len(generate_times) > 1:
        warm_totals = [
            preprocess_seconds + generate_seconds
            for preprocess_seconds, generate_seconds in zip(
                preprocess_times,
                generate_times,
            )
        ]
        mean_time = statistics.mean(warm_totals)
        print(f"Warm avg across {len(warm_totals)} runs: {mean_time:.3f}s")
        print(f"Warm avg throughput: {1 / mean_time:.2f} pages/sec")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Saved OCR markdown: {args.output}")

    if args.preview_chars > 0 and markdown:
        print("\n--- OCR preview ---")
        print(markdown[: args.preview_chars].strip())


if __name__ == "__main__":
    main()
