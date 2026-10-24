#!/usr/bin/env python3
"""Identifiers and documents for saved matchings and tracked offers (standard library only).

Usage:
    python3 -I offers.py key <url>
        prints the normalized URL, its hash, and the offer identifier
    python3 -I offers.py lookup <dir> <url>
        reads the matchings exported into <dir> (ArtifactData list with out_dir) and prints those of this URL
    python3 -I offers.py build <assessment.json> <report.json> --version-id V --version-name N [--notes notes.json] [--now ISO]
        prints {offerId, matchId, match, offer}: the match document to save, and the offer document to create
        when the offer is not tracked yet

The URL normalization and the hash must stay identical to the ones in assets/profile.html (normUrl, urlHash).
"""
import glob
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import quote, urlsplit

TRACKING = re.compile(r"^(utm_.*|gclid|fbclid|msclkid|mc_[a-z]+|trk|trackingid|refid|ref|referrer|source|src|campaign|li_.*|ga_.*)$", re.I)


def normalize(url):
    u = urlsplit(url.strip())
    host = (u.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    path = re.sub(r"/+$", "", quote(u.path, safe="/%:@!$&'()*+,;=-._~"))
    pairs = sorted(p for p in u.query.split("&") if p and not TRACKING.match(p.split("=")[0]))
    return host + path + ("?" + "&".join(pairs) if pairs else "")


def digest(url):
    return hashlib.sha1(normalize(url).encode("utf8")).hexdigest()[:12]


def now_iso(args):
    if "--now" in args:
        return args[args.index("--now") + 1]
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def opt(args, name, required=True):
    if name in args:
        return args[args.index(name) + 1]
    if required:
        sys.stderr.write("missing %s\n" % name)
        sys.exit(2)
    return None


def main():
    a = sys.argv[1:]
    if not a:
        sys.stderr.write(__doc__)
        sys.exit(2)
    if a[0] == "key" and len(a) >= 2:
        h = digest(a[1])
        print(json.dumps({"urlKey": normalize(a[1]), "hash": h, "offerId": "o-" + h}))
    elif a[0] == "lookup" and len(a) >= 3:
        h = digest(a[2])
        found = []
        for path in sorted(glob.glob(os.path.join(a[1], "**", "*.json"), recursive=True)):
            mid = os.path.splitext(os.path.basename(path))[0]
            if not mid.endswith("--" + h):
                continue
            d = json.load(open(path, encoding="utf8"))
            d = d.get("data", d) if isinstance(d.get("data"), dict) and "score" in d["data"] else d
            found.append({"id": mid, "versionId": d.get("versionId"), "versionName": d.get("versionName"), "score": d.get("score"), "label": d.get("label"), "createdAt": d.get("createdAt")})
        print(json.dumps({"offerId": "o-" + h, "matches": found}, ensure_ascii=False, indent=2))
    elif a[0] == "build" and len(a) >= 3:
        assessment = json.load(open(a[1], encoding="utf8"))
        report = json.load(open(a[2], encoding="utf8"))
        vid, vname = opt(a, "--version-id"), opt(a, "--version-name")
        notes = json.load(open(opt(a, "--notes", False), encoding="utf8")) if opt(a, "--notes", False) else {}
        now = now_iso(a)
        posting = assessment.get("posting") or {}
        url = posting.get("url") or report.get("posting", {}).get("url")
        if not url:
            sys.stderr.write("the posting has no url\n")
            sys.exit(2)
        h = digest(url)
        pick = lambda items, keys: [{k: i.get(k) for k in keys if i.get(k) not in (None, "")} for i in items]
        match = {
            "offerId": "o-" + h, "url": url, "urlKey": normalize(url), "versionId": vid, "versionName": vname, "createdAt": now,
            "posting": {k: posting.get(k) for k in ("title", "company", "location", "work_mode", "salary", "contract", "sector") if posting.get(k)},
            "score": report["score"], "label": report["label"], "mode": report.get("mode"),
            "groups": report.get("groups"), "capped": bool(report.get("capped_by_deal_breaker")),
            "dealBreakers": pick(report.get("deal_breakers") or [], ("type", "text", "detail")),
            "summary": notes.get("summary") or "",
            "items": pick(report.get("items") or [], ("group", "label", "kind", "status", "weight", "max", "points", "lost", "detail", "source")),
            "strengths": pick(report.get("strengths") or [], ("label", "points", "max", "detail")),
            "gaps": pick(report.get("gaps") or [], ("label", "status", "lost", "detail")),
            "unclear": pick(report.get("still_unclear") or [], ("label", "detail")),
            "attention": notes.get("attention") or [],
            "next": {"highlights": notes.get("highlights") or [], "recruiterQuestions": notes.get("recruiterQuestions") or []},
            "answersUsed": notes.get("answersUsed") or [],
        }
        offer = {
            "url": url, "urlKey": normalize(url), "title": posting.get("title", ""), "company": posting.get("company", ""),
            "status": "not_applied", "statusUpdatedAt": now, "createdAt": now, "formQA": [], "events": [], "emails": [],
        }
        print(json.dumps({"offerId": "o-" + h, "matchId": "%s--%s" % (vid, h), "match": match, "offer": offer}, ensure_ascii=False, indent=2))
    else:
        sys.stderr.write(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
