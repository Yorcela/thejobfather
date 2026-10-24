#!/usr/bin/env python3
"""Job match score from a structured assessment (standard library only).

Usage:
    python3 -I match_score.py assessment.json

The assistant reads the job posting, compares it with the resume and the user's preferences,
asks the user about its doubts, then writes assessment.json. This script turns that assessment
into a score, so the number is reproducible and every point can be explained.

assessment.json:
{
  "posting": {"url", "title", "company", "location", "work_mode", "salary", "contract", "sector"},
  "version": "name of the evaluated resume version",
  "preferences_set": true,
  "requirements": [{"text", "kind": "must|nice", "category", "status": "met|partial|missing|unknown", "evidence", "source": "cv|user|saved answer"}],
  "preferences": [{"dimension", "status": "ok|partial|conflict|unknown", "detail", "hard": false}],
  "dealbreakers": [{"text", "triggered": true|false, "detail"}],
  "avoided": [{"kind": "sector|company|role|location|work_mode", "value", "detail"}]   (also filled from saved answers)
}
The scoring scale is described in references/match.md.
"""
import json
import sys

GROUP_POINTS = {"requirements": 60.0, "preferences": 40.0}
REQ_WEIGHT = {"must": 3.0, "nice": 1.0}
REQ_VALUE = {"met": 1.0, "partial": 0.5, "unknown": 0.4, "missing": 0.0}
PREF_WEIGHT = {"salary": 3.0, "work_mode": 3.0, "location": 3.0, "title": 2.0, "sector": 2.0, "contract": 1.5, "seniority": 1.5, "company_size": 1.0, "language": 1.0}
PREF_DEFAULT_WEIGHT = 1.0
PREF_VALUE = {"ok": 1.0, "partial": 0.5, "unknown": 0.5, "conflict": 0.0}
DEALBREAKER_CAP = 25.0


def fail(msg):
    sys.stderr.write("match_score.py: %s\n" % msg)
    sys.exit(2)


def main():
    if len(sys.argv) != 2:
        fail("usage: match_score.py assessment.json")
    a = json.load(open(sys.argv[1], encoding="utf8"))
    reqs = a.get("requirements") or []
    prefs = a.get("preferences") or []
    prefs_set = bool(a.get("preferences_set")) and bool(prefs)

    for r in reqs:
        if r.get("kind") not in REQ_WEIGHT:
            fail("requirement kind must be must|nice: %r" % r.get("text"))
        if r.get("status") not in REQ_VALUE:
            fail("requirement status must be met|partial|missing|unknown: %r" % r.get("text"))
    for p in prefs:
        if p.get("status") not in PREF_VALUE:
            fail("preference status must be ok|partial|conflict|unknown: %r" % p.get("dimension"))

    items = []
    groups = {}

    def build(group, rows, weight_of, value_of, label_of, kind_of):
        total_w = sum(weight_of(r) for r in rows)
        if not rows or total_w <= 0:
            return None
        pts = 0.0
        for r in rows:
            w = weight_of(r)
            v = value_of(r)
            share = GROUP_POINTS[group] * w / total_w
            items.append({
                "group": group, "label": label_of(r), "kind": kind_of(r), "status": r.get("status"),
                "weight": w, "max": round(share, 2), "points": round(share * v, 2), "lost": round(share * (1 - v), 2),
                "detail": r.get("evidence") or r.get("detail") or "",
                "source": r.get("source"),
            })
            pts += share * v
        return pts / GROUP_POINTS[group]

    req_pct = build("requirements", reqs, lambda r: REQ_WEIGHT[r["kind"]], lambda r: REQ_VALUE[r["status"]],
                    lambda r: r.get("text", ""), lambda r: r["kind"])
    pref_pct = build("preferences", prefs if prefs_set else [], lambda p: PREF_WEIGHT.get(p.get("dimension"), PREF_DEFAULT_WEIGHT),
                     lambda p: PREF_VALUE[p["status"]], lambda p: p.get("dimension", ""), lambda p: "hard" if p.get("hard") else "preference")

    parts = [(g, pct) for g, pct in (("requirements", req_pct), ("preferences", pref_pct)) if pct is not None]
    if not parts:
        fail("nothing to score: no requirements and no preferences")
    max_total = sum(GROUP_POINTS[g] for g, _ in parts)
    raw = sum(GROUP_POINTS[g] * pct for g, pct in parts)
    score = 100.0 * raw / max_total
    for g, pct in parts:
        groups[g] = {"points": round(GROUP_POINTS[g] * pct, 1), "max": GROUP_POINTS[g], "share": round(pct, 3)}
    # when only one group is scored, its points are rescaled on 100 for display
    scale = 100.0 / max_total

    triggers = []
    for d in a.get("dealbreakers") or []:
        if d.get("triggered"):
            triggers.append({"type": "deal-breaker", "text": d.get("text"), "detail": d.get("detail", "")})
    for v in a.get("avoided") or []:
        triggers.append({"type": "avoided " + str(v.get("kind", "")), "text": v.get("value"), "detail": v.get("detail", "")})
    for p in prefs if prefs_set else []:
        if p.get("hard") and p["status"] == "conflict":
            triggers.append({"type": "hard preference", "text": p.get("dimension"), "detail": p.get("detail", "")})
    capped = False
    if triggers and score > DEALBREAKER_CAP:
        score, capped = DEALBREAKER_CAP, True
    score = round(score)

    label = "strong match" if score >= 80 else "good match" if score >= 65 else "partial match" if score >= 50 else "weak match"
    if triggers:
        label = "deal-breaker"

    for it in items:
        it["max"] = round(it["max"] * scale, 1)
        it["points"] = round(it["points"] * scale, 1)
        it["lost"] = round(it["lost"] * scale, 1)
    strengths = [i for i in items if i["status"] in ("met", "ok") and i["kind"] in ("must", "hard", "preference")]
    strengths.sort(key=lambda i: -i["max"])
    gaps = sorted((i for i in items if i["lost"] >= 0.5), key=lambda i: -i["lost"])
    unclear = [i for i in items if i["status"] == "unknown"]

    report = {
        "score": score, "label": label, "mode": "requirements and preferences" if len(parts) == 2 else ("requirements only" if parts[0][0] == "requirements" else "preferences only"),
        "posting": a.get("posting") or {}, "version": a.get("version"),
        "groups": groups, "capped_by_deal_breaker": capped, "deal_breakers": triggers,
        "strengths": strengths[:6], "gaps": gaps[:8], "still_unclear": unclear,
        "items": items,
        "note": "Estimate based on the posting, the resume and the user's answers: not a hiring prediction. See references/match.md.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
