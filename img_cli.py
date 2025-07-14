# img_cli.py
"""
Interactive CLI for managing product pictures.

Commands
--------
list               Show every image found under IMG_ROOT
index              (Re)build image_index.json
find <ref>         Print absolute path of picture whose filename starts with <ref>
exit / quit        Leave the CLI
"""

from __future__ import annotations
import json, os, re, sys
from pathlib import Path
from typing import Dict, List

# --- config ----------------------------------------------------
IMG_ROOT = Path(__file__).parent        # same folder; change if you like
INDEX_FILE = IMG_ROOT / "image_index.json"
VALID_EXT  = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
REF_RE     = re.compile(r"^\s*(\d+(?:\.\d+)*)")   # grabs 4.1.2 etc.
# ---------------------------------------------------------------


# ---------- core helpers ---------------------------------------
def _scan() -> List[Path]:
    return [p for p in IMG_ROOT.rglob("*") if p.suffix.lower() in VALID_EXT]

def build_index() -> Dict[str, str]:
    idx: Dict[str, str] = {}
    for p in _scan():
        m = REF_RE.match(p.name)
        if not m:
            continue
        ref = m.group(1)
        idx.setdefault(ref, str(p.resolve()))
    INDEX_FILE.write_text(json.dumps(idx, indent=2))
    return idx

def load_index() -> Dict[str, str]:
    if not INDEX_FILE.exists():
        print("No index file – type 'index' first.")
        return {}
    return json.loads(INDEX_FILE.read_text())
# ---------------------------------------------------------------


# ---------- interactive shell ----------------------------------
BANNER = (
    "\n📷  Product-Image CLI  –  type 'help' for commands\n"
    f"🗂  Image folder: {IMG_ROOT}\n"
)

def main() -> None:
    print(BANNER)
    while True:
        try:
            cmd = input("img> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye!")
            break

        if not cmd:
            continue

        if cmd in {"exit", "quit"}:
            print("bye!")
            break

        if cmd == "help":
            print(__doc__)
            continue

        if cmd == "list":
            files = _scan()
            for p in files:
                m = REF_RE.match(p.name)
                ref = m.group(1) if m else "—"
                print(f"{ref:10}  {p.relative_to(IMG_ROOT)}")
            print(f"\n({len(files)} files)")
            continue

        if cmd == "index":
            idx = build_index()
            print(f"Indexed {len(idx)} refs ➜ {INDEX_FILE}")
            continue

        if cmd.startswith("find "):
            ref = cmd.split(maxsplit=1)[1]
            idx = load_index()
            if not idx:
                continue
            path = idx.get(ref)
            if path:
                print(path)
            else:
                print(f"❌  No image for ref '{ref}'")
            continue

        print("Unknown command – type 'help'.")

# ---------------------------------------------------------------
if __name__ == "__main__":
    main()
