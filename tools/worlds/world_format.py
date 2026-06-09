#!/usr/bin/env python3
"""Standardize the structure of Gazebo world (.sdf) files.

Reorders the top-level children of <world> into the project's three-section
layout and inserts section banners, **without changing any element's content**:

    1. PHYSICS & GPS COORDINATE  physics, gravity, magnetic_field, atmosphere,
                                 wind, spherical_coordinates
    2. ENVIRONMENT & LIGHT       scene, light(s)
    3. WORLD MODELS              ground_plane, include, model, ...

See ../docs/world-structure.md for the full convention.

Safety: every run self-checks that the output is well-formed XML and that the
multiset of world elements is unchanged (no element added, removed or altered).

Usage:
    world_format.py --all                 # format every worlds/*.sdf in place
    world_format.py worlds/uwb.sdf a.sdf  # format the given files in place
    world_format.py uwb default           # bare names resolve to worlds/<name>.sdf
    world_format.py --all --check         # report only; exit 1 if any file would change
"""
import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
# this script lives in tools/worlds/ ; the world files are in ../../worlds
WORLDS_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "worlds"))

# tag -> section index (0,1,2); anything unlisted goes to section 3 (models).
G1 = {"physics", "gravity", "magnetic_field", "atmosphere", "wind", "spherical_coordinates"}
G2 = {"scene", "light"}

# canonical stable order inside sections 1 and 2 (section 3 keeps original order)
ORDER = {
    "physics": 0, "gravity": 1, "magnetic_field": 2, "atmosphere": 3,
    "wind": 4, "spherical_coordinates": 5,
    "scene": 0, "light": 1,
}

BANNERS = [
    "    <!-- ===================== 1. PHYSICS & GPS COORDINATE ===================== -->",
    "    <!-- ===================== 2. ENVIRONMENT & LIGHT ===================== -->",
    "    <!-- ===================== 3. WORLD MODELS ===================== -->",
]


def group_of(name):
    if name in G1:
        return 0
    if name in G2:
        return 1
    return 2


def split_top_nodes(inner):
    """Return ordered [(kind, name, text)] for the direct children of <world>.

    kind is 'comment' or 'element'; element text is the full subtree, verbatim.
    """
    nodes = []
    i, n, depth, node_start = 0, len(inner), 0, None
    while i < n:
        if inner[i] != "<":
            i += 1
            continue
        if inner.startswith("<!--", i):
            end = inner.find("-->", i) + 3
            if depth == 0:
                nodes.append(("comment", None, inner[i:end]))
            i = end
            continue
        if inner.startswith("<?", i):
            i = inner.find("?>", i) + 2
            continue
        if inner.startswith("</", i):
            gt = inner.find(">", i) + 1
            depth -= 1
            if depth == 0:
                text = inner[node_start:gt]
                m = re.match(r"<\s*([\w:.\-]+)", text)
                nodes.append(("element", m.group(1), text))
                node_start = None
            i = gt
            continue
        gt = inner.find(">", i) + 1
        tag = inner[i:gt]
        m = re.match(r"<\s*([\w:.\-]+)", tag)
        name = m.group(1)
        if tag.rstrip().endswith("/>"):
            if depth == 0:
                nodes.append(("element", name, inner[i:gt]))
        else:
            if depth == 0:
                node_start = i
            depth += 1
        i = gt
    return nodes


def world_inner(text):
    m = re.search(r"<world\b[^>]*>(.*)</world>", text, re.S)
    return m.group(1) if m else None


def reorder(text):
    """Return normalized text, or None if there is no <world> element."""
    mw = re.search(r"<world\b[^>]*>", text)
    if not mw:
        return None
    open_end = mw.end()
    close = text.rfind("</world>")
    if close == -1:
        return None
    preamble = text[:open_end]
    inner = text[open_end:close]
    postamble = text[close:]

    nodes = split_top_nodes(inner)

    buckets = [[], [], []]
    pending = []  # leading comments attach to the following element
    for kind, name, t in nodes:
        if kind == "comment":
            if "=====" in t:  # drop previously inserted section banners (idempotent)
                continue
            pending.append(t.strip())
            continue
        buckets[group_of(name)].append((pending[:], t.strip(), name))
        pending = []
    if pending:  # trailing comments -> models section
        buckets[2].append((pending[:], None, None))

    for gi in (0, 1):
        buckets[gi].sort(key=lambda it: ORDER.get(it[2], 99))

    def emit(item):
        comments, el = item[0], item[1]
        out = ["    " + c for c in comments]
        if el is not None:
            out.append("    " + el)
        return "\n".join(out)

    parts = [preamble.rstrip("\n")]
    for gi in range(3):
        if not buckets[gi]:
            continue
        parts.append("")
        parts.append(BANNERS[gi])
        for item in buckets[gi]:
            parts.append(emit(item))
    parts.append("")
    parts.append(postamble if postamble.startswith("  ") else "  " + postamble)

    result = "\n".join(parts)
    if not result.endswith("\n"):
        result += "\n"
    return result


def element_signature(inner):
    """Multiset of whitespace-normalized element texts (comments excluded)."""
    sig = {}
    for kind, name, t in split_top_nodes(inner):
        if kind != "element":
            continue
        key = re.sub(r"\s+", " ", t.strip())
        sig[key] = sig.get(key, 0) + 1
    return sig


def process(path, check):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")

    before = world_inner(text)
    if before is None:
        return ("skip", "no <world>", None)

    new_text = reorder(text)
    if new_text is None:
        return ("skip", "no <world>", None)

    # safety check 1: well-formed XML
    try:
        ET.fromstring(new_text.encode("utf-8"))
    except ET.ParseError as e:
        return ("fail", f"XML error: {e}", None)

    # safety check 2: no element added/removed/altered
    if element_signature(before) != element_signature(world_inner(new_text)):
        return ("fail", "element set changed - aborted", None)

    g = [0, 0, 0]
    for kind, name, t in split_top_nodes(world_inner(new_text)):
        if kind == "element":
            g[group_of(name)] += 1
    stats = f"g1={g[0]} g2={g[1]} g3={g[2]}"

    changed = new_text != text
    if check:
        return ("diff" if changed else "ok", stats, None)

    if changed:
        data = new_text.encode("utf-8")
        if bom:
            data = b"\xef\xbb\xbf" + data
        open(path, "wb").write(data)
    return ("formatted" if changed else "ok", stats, None)


def resolve(arg):
    if os.path.isfile(arg):
        return arg
    cand = os.path.join(WORLDS_DIR, arg if arg.endswith(".sdf") else arg + ".sdf")
    return cand


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="world files or bare names (resolve to worlds/<name>.sdf)")
    ap.add_argument("--all", action="store_true", help="process every worlds/*.sdf")
    ap.add_argument("--check", action="store_true", help="report only; exit 1 if any file is not normalized")
    args = ap.parse_args()

    if args.all:
        targets = sorted(glob.glob(os.path.join(WORLDS_DIR, "*.sdf")))
    elif args.files:
        targets = [resolve(f) for f in args.files]
    else:
        ap.error("pass world files/names, or --all")

    rc = 0
    for path in targets:
        if not os.path.isfile(path):
            print(f"MISSING  {path}")
            rc = 1
            continue
        status, info, _ = process(path, args.check)
        name = os.path.basename(path)
        if status == "fail":
            print(f"FAIL     {name:24s} {info}")
            rc = 1
        elif status == "diff":
            print(f"NEEDS-FMT {name:23s} {info}")
            rc = 1
        elif status == "formatted":
            print(f"FORMATTED {name:23s} {info}")
        elif status == "skip":
            print(f"SKIP     {name:24s} {info}")
        else:
            print(f"OK       {name:24s} {info}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
