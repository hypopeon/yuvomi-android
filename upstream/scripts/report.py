"""Write the Markdown report for an upstream sync PR.

Usage:
  python3 -I report.py --old-spec A.json --new-spec B.json --used operations-used.txt \
      --changelog CHANGELOG.md --old-version 2.83.0 --new-version 2.84.0 \
      [--old-en old/en.json --new-en new/en.json]

Prints Markdown on stdout. The first line is `<!-- upstream-sync: breaking -->`
when an operation the app uses disappeared or changed, so the workflow can
label the PR without parsing the rest.
"""
import argparse
import json
import pathlib
import re

METHODS = ("get", "post", "put", "patch", "delete")
HEADING = re.compile(r"^## \[(\d+(?:\.\d+)*)\]")
NOTABLE = re.compile(r"deprecat|breaking|/api/v1|api token|openapi|removed", re.I)


def operations(spec):
    ops = {}
    for path, item in spec.get("paths", {}).items():
        for method, op in item.items():
            if method in METHODS:
                ops[f"{method.upper()} {path}"] = op
    return ops


def read_used(path):
    used = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            method, route = line.split(None, 1)
            used.append(f"{method.upper()} {route.strip()}")
    return used


def changed_parts(old, new):
    return [k for k in sorted(set(old) | set(new))
            if json.dumps(old.get(k), sort_keys=True) != json.dumps(new.get(k), sort_keys=True)]


def version_key(v):
    return tuple(int(p) for p in v.split("."))


def changelog_sections(text, old, new):
    lo, hi = version_key(old), version_key(new)
    sections, current, keep = [], [], False
    for line in text.splitlines():
        m = HEADING.match(line)
        if m or line.startswith("## [Unreleased]"):
            if keep and current:
                sections.append(current)
            current = [line]
            keep = bool(m) and lo < version_key(m.group(1)) <= hi
        elif keep:
            current.append(line)
    if keep and current:
        sections.append(current)
    return sections


def bullets(lines):
    """Join wrapped CHANGELOG lines into whole entries (one per `-`/`*` bullet or paragraph)."""
    entries, current = [], []
    for line in lines:
        stripped = line.strip()
        starts = stripped.startswith(("- ", "* ", "### ")) or not stripped
        if starts and current:
            entries.append(" ".join(current))
            current = []
        if stripped and not stripped.startswith("### "):
            current.append(re.sub(r"^[-*]\s+", "", stripped) if not current else stripped)
    if current:
        entries.append(" ".join(current))
    return entries


def shorten(text, limit=240):
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + " …"


def flatten(obj, prefix=""):
    keys = set()
    for k, v in obj.items():
        name = f"{prefix}.{k}" if prefix else k
        keys |= flatten(v, name) if isinstance(v, dict) else {name}
    return keys


def main():
    ap = argparse.ArgumentParser()
    for name in ("old-spec", "new-spec", "used", "changelog", "old-version", "new-version"):
        ap.add_argument(f"--{name}", required=True)
    ap.add_argument("--old-en")
    ap.add_argument("--new-en")
    a = ap.parse_args()

    old_spec = json.loads(pathlib.Path(a.old_spec).read_text()) if pathlib.Path(a.old_spec).exists() else {}
    new_spec = json.loads(pathlib.Path(a.new_spec).read_text())
    old_ops, new_ops = operations(old_spec), operations(new_spec)
    used = read_used(a.used)

    missing = [op for op in used if op not in new_ops]
    deprecated = [op for op in used if new_ops.get(op, {}).get("deprecated")]
    changed = {op: changed_parts(old_ops[op], new_ops[op])
               for op in used if op in old_ops and op in new_ops}
    changed = {op: parts for op, parts in changed.items() if parts}
    breaking = bool(missing or deprecated)

    out = [f"<!-- upstream-sync: {'breaking' if breaking else 'ok'} -->",
           f"## Upstream sync: {a.old_version} → {a.new_version}", ""]

    out += ["### Operations this app uses", ""]
    if not (missing or deprecated or changed):
        out.append(f"All {len(used)} operations are present and unchanged.")
    for op in missing:
        out.append(f"- **MISSING** `{op}`: no longer in the OpenAPI document.")
    for op in deprecated:
        out.append(f"- **DEPRECATED** `{op}`: works for at least 90 days from this release.")
    for op, parts in changed.items():
        out.append(f"- changed `{op}`: {', '.join(parts)}. Check the diff of `upstream/openapi.json`.")
    out.append("")

    added = sorted(set(new_ops) - set(old_ops))
    removed = sorted(set(old_ops) - set(new_ops))
    other_changed = sum(1 for op in set(old_ops) & set(new_ops)
                        if op not in changed and changed_parts(old_ops[op], new_ops[op]))
    out += ["### Whole API", "",
            "| Added | Removed | Changed |", "|---|---|---|",
            f"| {len(added)} | {len(removed)} | {other_changed} |", ""]
    if removed:
        out += ["Removed operations:", ""] + [f"- `{op}`" for op in removed] + [""]

    if a.old_en and a.new_en and pathlib.Path(a.old_en).exists():
        old_keys = flatten(json.loads(pathlib.Path(a.old_en).read_text(encoding="utf-8")))
        new_keys = flatten(json.loads(pathlib.Path(a.new_en).read_text(encoding="utf-8")))
        gone, new = sorted(old_keys - new_keys), sorted(new_keys - old_keys)
        out += ["### Strings (English, shipped namespaces)", "",
                f"{len(new)} added, {len(gone)} removed.", ""]
        if gone:
            out += ["Removed keys (the i18n test fails if the app uses one):", ""]
            out += [f"- `{k}`" for k in gone[:100]] + [""]

    sections = changelog_sections(pathlib.Path(a.changelog).read_text(encoding="utf-8"),
                                  a.old_version, a.new_version)
    notable = [entry for s in sections for entry in bullets(s[1:]) if NOTABLE.search(entry)]
    out += ["### CHANGELOG", ""]
    if notable:
        out += ["Entries mentioning the API, deprecations or removals:", ""]
        out += [f"- {shorten(entry)}" for entry in notable[:40]]
        out.append("")
    out += ["<details><summary>Release headings in this range</summary>", ""]
    out += [s[0] for s in sections] + ["", "</details>", ""]

    print("\n".join(out))


if __name__ == "__main__":
    main()
