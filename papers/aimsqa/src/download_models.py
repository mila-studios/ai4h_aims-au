"""Check for the AIMS-QA model weights and explain where to get them.

The weights are too large to keep in the git repository (the classifier alone is
1.47 GB, and GitHub's free Git LFS allowance is 1 GB in total), so they are hosted
externally. Run this after cloning to see what is missing.

The ModernBERT backbone (answerdotai/ModernBERT-large) is not listed here: it is
downloaded automatically by transformers on first use.
"""

from pathlib import Path

DRIVE_FOLDER = "https://drive.google.com/drive/folders/1MqAGkXt4-6S6go0ctsPkLQKvkwgLu7GZ"

REQUIRED = [
    (
        Path("models/context_classifier.pth"),
        "1.47 GB",
        f"Download 'au.pth' from {DRIVE_FOLDER}\n"
        "     and save it as models/context_classifier.pth",
    ),
    (
        Path("models/sentencebert_retriever/model.safetensors"),
        "87 MB",
        "Not yet publicly released. Open an issue if you need it:\n"
        "     https://github.com/mila-ai4h/ai4h_aims-au/issues",
    ),
]


def main() -> None:
    missing = [(p, size, how) for p, size, how in REQUIRED if not p.exists()]

    if not missing:
        print("All model weights present. You can run pipeline.py.")
        return

    print(f"{len(missing)} of {len(REQUIRED)} model file(s) missing:\n")
    for path, size, how in missing:
        print(f"  {path}  ({size})")
        print(f"     {how}\n")
    print("Agent 1 needs the classifier. Agent 2 (the RAG Watchdog fallback) needs")
    print("the retriever; without it, questions Agent 1 cannot answer are skipped.")


if __name__ == "__main__":
    main()
