"""Copy the namespaces the app uses from upstream's locale files into app assets.

Usage: python3 -I extract_locales.py <upstream-checkout> <namespaces.txt> <out-dir>

Keeps upstream's key order so diffs stay small. Removes locale files that
upstream no longer ships. Fails when a listed namespace is missing from en.json,
because then every language would silently lose it.
"""
import json
import pathlib
import sys


def read_namespaces(path):
    names = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.append(line)
    return names


def main():
    if len(sys.argv) != 4:
        sys.exit("usage: extract_locales.py <upstream-checkout> <namespaces.txt> <out-dir>")
    checkout, ns_file, out_dir = (pathlib.Path(a) for a in sys.argv[1:])
    namespaces = read_namespaces(ns_file)
    src_dir = checkout / "public" / "locales"
    out_dir.mkdir(parents=True, exist_ok=True)

    english = json.loads((src_dir / "en.json").read_text(encoding="utf-8"))
    missing = [ns for ns in namespaces if ns not in english]
    if missing:
        sys.exit(f"namespaces missing from upstream en.json: {', '.join(missing)}")

    written = set()
    for src in sorted(src_dir.glob("*.json")):
        data = json.loads(src.read_text(encoding="utf-8"))
        subset = {ns: data[ns] for ns in namespaces if ns in data}
        target = out_dir / src.name
        target.write_text(json.dumps(subset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.add(src.name)

    for stale in out_dir.glob("*.json"):
        if stale.name not in written:
            stale.unlink()
            print(f"locales: removed {stale.name} (no longer upstream)")

    print(f"locales: {len(written)} files, {len(namespaces)} namespaces -> {out_dir}")


if __name__ == "__main__":
    main()
