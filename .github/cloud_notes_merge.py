#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fold the notes Nii Okai wrote in the app (any device, synced through his Google account)
into the published journal file, data/commentary.js.

  cloud_notes_merge.py <commentary.js> [--also <other commentary.js>] [--from-json <file>]

Reads /published/<book> from Firestore over plain HTTPS (the rules make that path readable;
it holds only what is already public on the website). Applies exactly what the app itself
would: new notes are added, edited notes updated when the edit is newer, deleted notes
removed. Nothing else in the file is touched. --also unions in notes from another copy of
the file (used on the Mac so a publish from there can never drop notes the website already
folded in). Prints a one-line summary; exit 0 = ok, 2 = could not reach Firestore.
"""
import sys, json, io, os, re, urllib.request

PROJECT = "nii-okai-bible-commentary"
URL = "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/published?pageSize=300" % PROJECT

def unwrap(v):
    """Firestore REST typed value -> plain Python."""
    if "stringValue" in v: return v["stringValue"]
    if "integerValue" in v: return int(v["integerValue"])
    if "doubleValue" in v: return v["doubleValue"]
    if "booleanValue" in v: return v["booleanValue"]
    if "nullValue" in v: return None
    if "mapValue" in v: return {k: unwrap(x) for k, x in (v["mapValue"].get("fields") or {}).items()}
    if "arrayValue" in v: return [unwrap(x) for x in (v["arrayValue"].get("values") or [])]
    if "timestampValue" in v: return v["timestampValue"]
    return None

def fetch_published(from_json=None):
    if from_json:
        raw = json.load(open(from_json, encoding="utf-8"))
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "nii-okai-journal/1.0"})
        raw = json.load(urllib.request.urlopen(req, timeout=30))
    out = {}
    for d in raw.get("documents", []):
        book = d["name"].rsplit("/", 1)[-1]
        f = {k: unwrap(v) for k, v in (d.get("fields") or {}).items()}
        out[book] = {"n": f.get("n") or {}, "x": f.get("x") or {}}
    return out

def load_seed(path):
    raw = io.open(path, encoding="utf-8").read()
    i = raw.index("{")
    return raw[:i], json.loads(raw[i:].rstrip().rstrip(";"))

def index(seed):
    ix = {}
    for b, chs in seed.items():
        for ch, vs in chs.items():
            for v, arr in vs.items():
                for nt in arr:
                    if nt.get("id"): ix[nt["id"]] = (b, ch, v, nt)
    return ix

def stamp(nt): return str(nt.get("edited") or nt.get("date") or "")

def remove(seed, b, ch, v, nid):
    arr = seed[b][ch][v]
    seed[b][ch][v] = [n for n in arr if n.get("id") != nid]
    if not seed[b][ch][v]:
        del seed[b][ch][v]
        if not seed[b][ch]: del seed[b][ch]
        if not seed[b]: del seed[b]

def main():
    args = sys.argv[1:]
    if not args: print(__doc__); sys.exit(1)
    path = args[0]; also = None; from_json = None
    if "--also" in args: also = args[args.index("--also") + 1]
    if "--from-json" in args: from_json = args[args.index("--from-json") + 1]

    head, seed = load_seed(path)
    ix = index(seed)
    added = updated = removed = unioned = 0

    # 1. union with another copy of the file (Mac <-> website), by note id — adds only
    if also and os.path.exists(also):
        try:
            _, other = load_seed(also)
            for b, ch, v, nt in index(other).values():
                if nt["id"] not in ix:
                    seed.setdefault(b, {}).setdefault(ch, {}).setdefault(v, []).append(nt)
                    ix[nt["id"]] = (b, ch, v, nt); unioned += 1
        except Exception as e:
            print("warning: could not read %s (%s)" % (also, e))

    # 2. what the app synced to the account
    try:
        pub = fetch_published(from_json)
    except Exception as e:
        print("could not reach Firestore: %s" % e); sys.exit(2)

    for b, doc in pub.items():
        n, x = doc["n"], doc["x"]
        for nid, r in n.items():
            if not isinstance(r, dict) or not r.get("t"): continue
            if nid in x and str(x[nid]) > str(r.get("e") or r.get("d") or ""): continue   # deleted after it was written
            loc = ix.get(nid)
            if loc:
                b0, ch0, v0, nt = loc
                if str(r.get("e") or "") > stamp(nt) and nt.get("text") != r["t"]:
                    nt["text"] = r["t"]; nt["edited"] = r["e"]; updated += 1
            else:
                nt = {"id": nid, "text": r["t"], "date": r.get("d") or "", "src": r.get("s") or "user"}
                if r.get("e"): nt["edited"] = r["e"]
                seed.setdefault(b, {}).setdefault(str(r.get("c")), {}).setdefault(str(r.get("v")), []).append(nt)
                ix[nid] = (b, str(r.get("c")), str(r.get("v")), nt); added += 1
        for nid, ts in x.items():
            loc = ix.get(nid)
            if not loc: continue
            b0, ch0, v0, nt = loc
            if nt.get("edited") and str(nt["edited"]) > str(ts): continue      # edited after the delete: keep
            remove(seed, b0, ch0, v0, nid); del ix[nid]; removed += 1

    if added or updated or removed or unioned:
        tmp = path + ".tmp"
        io.open(tmp, "w", encoding="utf-8").write(head + json.dumps(seed, ensure_ascii=False, separators=(",", ":")) + ";")
        os.replace(tmp, path)
    total = sum(len(a) for chs in seed.values() for vs in chs.values() for a in vs.values())
    print("notes: added=%d updated=%d removed=%d unioned=%d total=%d" % (added, updated, removed, unioned, total))

if __name__ == "__main__":
    main()
