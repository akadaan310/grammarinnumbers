"""Authoring aid: add bibliography entries from a JSON object on stdin (key -> entry).
Refuses to overwrite an existing key; keeps the file sorted by key."""
import json, os, sys
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content", "bibliography.json")
bib = json.load(open(p, encoding="utf8"))
new = json.load(sys.stdin)
for k, v in new.items():
    if k in bib:
        sys.exit(f"key exists: {k}")
    for f in ("label", "authors", "year", "title", "venue", "verification"):
        assert f in v, (k, f)
    bib[k] = v
json.dump(dict(sorted(bib.items())), open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(f"{len(new)} added; {len(bib)} entries")
