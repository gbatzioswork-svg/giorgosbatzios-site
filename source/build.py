"""Builds giorgosbatzios.com into ../site.   Run: python3 source/build.py

The pages themselves are made by render.mjs (Node), the same code GB EDITOR uses for its instant preview,
so the preview and the real site can never differ. This script runs it and then draws the 1200x630
share-preview cards (needs Pillow; without it the site still builds, just without new cards)."""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "site")

with tempfile.TemporaryDirectory() as tmp:
    cards_file = os.path.join(tmp, "cards.json")
    subprocess.run(["node", os.path.join(HERE, "build.mjs"), "--cards", cards_file], check=True)
    cards = json.load(open(cards_file, encoding="utf-8"))

try:
    sys.path.insert(0, HERE)
    import ogcard
except Exception as err:  # Pillow missing (e.g. preview builds): skip the cards
    print("share cards skipped:", err)
else:
    for c in cards:
        ogcard.make(os.path.join(OUT, c["file"].lstrip("/")), c["title"], c["kicker"], c["footer"], c["tagline"])
    print(len(cards), "share cards")
