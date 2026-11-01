"""Extract upstream's colour tokens (light and dark) into a flat JSON file.

Usage: python3 -I extract_tokens.py <upstream-checkout> <out.json>

Reads public/styles/tokens.css: the first top-level `:root { ... }` block for
light, and `:root:not([data-theme="light"]) { ... }` inside the
`prefers-color-scheme: dark` media query for dark. Resolves var() references
(dark overrides fall back to light values), and keeps public tokens (no leading
underscore) whose resolved value is a colour.
"""
import json
import pathlib
import re
import sys

COMMENT = re.compile(r"/\*.*?\*/", re.S)
DECL = re.compile(r"--([A-Za-z0-9_-]+)\s*:\s*([^;]+);")
VAR = re.compile(r"var\(\s*--([A-Za-z0-9_-]+)\s*(?:,\s*([^()]*(?:\([^()]*\))?[^()]*))?\)")
COLOUR = re.compile(r"^(#[0-9A-Fa-f]{3,8}|rgba?\([^()]*\))$")


def block_after(css, start):
    """Return the text between the brace that opens at or after `start` and its match."""
    open_at = css.index("{", start)
    depth = 0
    for i in range(open_at, len(css)):
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0:
                return css[open_at + 1 : i]
    raise ValueError("unbalanced braces")


def declarations(block):
    # Only declarations at depth 0 of this block, not nested rules.
    flat, depth = [], 0
    for ch in block:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif depth == 0:
            flat.append(ch)
    return {m.group(1): " ".join(m.group(2).split()) for m in DECL.finditer("".join(flat))}


def resolve(name, table, seen=()):
    value = table.get(name)
    if value is None or name in seen:
        return None

    def sub(m):
        inner = resolve(m.group(1), table, seen + (name,))
        if inner is None and m.group(2):
            inner = m.group(2).strip()
        return inner if inner is not None else m.group(0)

    previous = None
    while previous != value and "var(" in value:
        previous, value = value, VAR.sub(sub, value)
    return value


def colours(table):
    out = {}
    for name in sorted(table):
        if name.startswith("_"):
            continue
        value = resolve(name, table)
        if value and COLOUR.match(value):
            out[name] = value
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: extract_tokens.py <upstream-checkout> <out.json>")
    checkout, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    css = COMMENT.sub("", (checkout / "public" / "styles" / "tokens.css").read_text(encoding="utf-8"))

    root = re.search(r"(?m)^:root\s*\{", css)
    light = declarations(block_after(css, root.start()))

    media = re.search(r"@media[^{]*prefers-color-scheme:\s*dark[^{]*\{", css)
    media_body = block_after(css, media.start())
    dark_root = re.search(r':root:not\(\[data-theme="light"\]\)\s*\{', media_body)
    dark = {**light, **declarations(block_after(media_body, dark_root.start()))}

    result = {"light": colours(light), "dark": colours(dark)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"tokens: {len(result['light'])} light, {len(result['dark'])} dark -> {out}")


if __name__ == "__main__":
    main()
