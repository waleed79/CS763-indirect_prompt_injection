"""Phase 4 Plan 03: emit a QR-code PNG that links to the public GitHub repo.

Used by the poster (CONTEXT D-14, D-15 Section 9 — QR code -> GitHub repo with
replication instructions). Encoded URL was verified via `git remote get-url origin`
in Wave 0 and recorded in 04-WAVE0-NOTES.md.

NOTE: The repo MUST be public before the poster prints; otherwise the QR scan
resolves to a 404. See RESEARCH Pitfall 5 + 04-WAVE0-NOTES.md for visibility check.

Pattern source: scripts/make_figures.py CLI scaffold + qrcode 8.2 README.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import qrcode


# ---------------------------------------------------------------------------
# Core encoder
# ---------------------------------------------------------------------------

def render_qr(url: str, out_path: str, box_size: int = 12, border: int = 4) -> None:
    """Encode *url* as a QR PNG and write atomically to *out_path*.

    Parameters
    ----------
    url:       URL to encode (no .git suffix; must be resolvable in a phone browser)
    out_path:  Destination file path (str). Written atomically (tmp + rename).
    box_size:  Pixels per QR module. Default 12 -> ~600 px native at auto version.
    border:    Quiet-zone width in modules. Minimum 4 per QR spec; default 4.
    """
    qr = qrcode.QRCode(
        version=None,                                        # auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # 15% recovery
        box_size=box_size,                                   # ~12 px/module -> ~600 px image
        border=border,                                       # quiet zone modules
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # Convert to RGB so the PNG is > 2 KB (bilevel 1-bit PNGs compress to ~1 KB which
    # is below the poster-print size check; RGB is the correct format for print workflows).
    pil_img = img.get_image().convert("RGB")
    # Atomic write -- same idiom as make_figures.save_atomic
    tmp = out_path + ".tmp"
    pil_img.save(tmp, format="PNG")
    os.replace(tmp, out_path)


# ---------------------------------------------------------------------------
# CLI plumbing (mirrors make_figures.py scaffold)
# ---------------------------------------------------------------------------

def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase 4 -- emit GitHub-repo QR PNG for the poster."
    )
    parser.add_argument(
        "--output",
        default="figures/qr_github.png",
    )
    parser.add_argument(
        "--url",
        default="https://github.com/waleed79/CS763-indirect_prompt_injection",
        help=(
            "Repo URL to encode (verified via git remote get-url origin 2026-05-02;"
            " .git stripped)"
        ),
    )
    parser.add_argument("--box-size", type=int, default=12)
    parser.add_argument("--border", type=int, default=4)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point.  Returns 0 on success, 2 on error."""
    args = make_parser().parse_args(argv or [])
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        render_qr(args.url, str(out_path), args.box_size, args.border)
        print(f"[OK] wrote {out_path} (encodes: {args.url})")
        return 0
    except Exception as e:  # noqa: BLE001
        print(
            f"[ERROR] qr generation failed: {type(e).__name__}: {e}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
