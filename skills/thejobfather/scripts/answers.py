#!/usr/bin/env python3
"""Validity of the answers the user gave to `match` questions (standard library only).

Usage:
    python3 -I answers.py ttl <verdict> [--now ISO]
        prints the createdAt and expiresAt to store for a new answer
    python3 -I answers.py active <dir> [--now ISO]
        reads the answer documents exported into <dir> (ArtifactData list with out_dir) and prints
        {"active": [...], "expired": [ids]}

Verdicts and how long an answer stays valid (also in references/match.md):
    refused   7 days    the user refused a sector, company, role, place, work mode or a salary level
    accepted  7 days    the user explicitly accepted something they would otherwise avoid
    lacks     90 days   the user does not have a skill or experience (it will not change within weeks)
    partial   90 days   the user has some exposure, not enough
    has       365 days  the user has a skill or experience that is not on the resume
"""
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

TTL_DAYS = {"refused": 7, "accepted": 7, "lacks": 90, "partial": 90, "has": 365}


def parse_now(args):
    if "--now" in args:
        i = args.index("--now")
        return datetime.fromisoformat(args[i + 1].replace("Z", "+00:00")).astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] not in ("ttl", "active"):
        sys.stderr.write(__doc__)
        sys.exit(2)
    now = parse_now(args)
    if args[0] == "ttl":
        verdict = args[1]
        if verdict not in TTL_DAYS:
            sys.stderr.write("unknown verdict %r (use %s)\n" % (verdict, ", ".join(sorted(TTL_DAYS))))
            sys.exit(2)
        print(json.dumps({"createdAt": iso(now), "expiresAt": iso(now + timedelta(days=TTL_DAYS[verdict])), "days": TTL_DAYS[verdict]}))
        return
    active, expired = [], []
    for path in sorted(glob.glob(os.path.join(args[1], "**", "*.json"), recursive=True)):
        d = json.load(open(path, encoding="utf8"))
        if isinstance(d.get("data"), dict) and "verdict" in d["data"]:
            d = d["data"]
        aid = os.path.splitext(os.path.basename(path))[0]
        try:
            exp = datetime.fromisoformat(str(d.get("expiresAt", "")).replace("Z", "+00:00"))
        except ValueError:
            exp = None
        if exp is not None and exp > now:
            active.append(dict(d, id=aid))
        else:
            expired.append(aid)
    print(json.dumps({"active": active, "expired": expired}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
