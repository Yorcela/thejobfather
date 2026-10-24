#!/usr/bin/env python3
"""Score ATS heuristique d'une version du CV (bibliothèque standard uniquement).

Usage :
    python3 -I ats_score.py version.json [--settings layout.json] [--keywords keywords.json] [--pdf cv.pdf]

version.json   document versions/<id> exporté depuis la base (voir references/schema.md)
--settings     document settings/layout (ordre et masquage des rubriques)
--keywords     liste de mots-clés tirés d'une offre : [{"term", "kind", "required", "variants"}]
--pdf          export PDF du CV, pour vérifier l'extraction du texte (nécessite pdftotext)

Sortie : un rapport JSON. Le barème est expliqué dans references/ats.md.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date

EXPECTED_ORDER = ["profile", "experiences", "projects", "education", "skills", "hobbies"]
SECTION_IDS = ["profile", "skills", "experiences", "projects", "education", "hobbies"]

DEFAULT_TITLES = {
    "en": {"profile": "Profile", "skills": "Skills", "experiences": "Professional Experience", "projects": "Personal Projects", "education": "Education & Certifications", "hobbies": "Hobbies"},
    "fr": {"profile": "Profil", "skills": "Compétences", "experiences": "Expérience professionnelle", "projects": "Projets personnels", "education": "Éducation & certifications", "hobbies": "Hobbies"},
}

# intitulés de rubrique que les parseurs reconnaissent (comparés sans accents ni casse)
STANDARD_HEADINGS = {
    "profile": ["profile", "summary", "professional summary", "career summary", "about", "about me", "objective", "profil", "profil professionnel", "resume", "resume professionnel", "a propos", "a propos de moi"],
    "skills": ["skills", "technical skills", "core skills", "key skills", "core competencies", "competencies", "expertise", "competences", "competences cles", "competences techniques"],
    "experiences": ["experience", "work experience", "professional experience", "employment history", "work history", "career history", "experience professionnelle", "experiences professionnelles", "parcours professionnel", "experiences"],
    "projects": ["projects", "personal projects", "selected projects", "side projects", "key projects", "projets", "projets personnels", "projets cles"],
    "education": ["education", "education and certifications", "education and training", "certifications", "training", "academic background", "formation", "formations", "education et certifications", "diplomes", "formation et certifications"],
    "hobbies": ["hobbies", "interests", "hobbies and interests", "activities", "centres d interet", "loisirs", "interets"],
}

KIND_WEIGHT = {"hard": 3.0, "title": 3.0, "education": 2.0, "soft": 1.0, "other": 1.0}
ZONE_WEIGHT = {"title": 1.0, "summary": 1.0, "experience": 1.0, "skills": 0.7, "other": 0.7}
KEYWORD_POINTS = 40.0

# caractères que l'export PDF (police Helvetica, WinAnsi) sait écrire
SAFE_CHARS = re.compile(r"[^\x20-\x7E\xA0-\xFF–—‘’‚“”„•…€™ŒœŠšŸŽž]")


def fold(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode("ascii").lower()
    s = s.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def words(s):
    return len(re.findall(r"\S+", str(s or "")))


def load_doc(path):
    d = json.load(open(path, encoding="utf8"))
    if isinstance(d.get("data"), dict) and "lang" in d["data"]:
        d = d["data"]
    return d


def items(doc, coll):
    m = doc.get(coll)
    if not isinstance(m, dict):
        return []
    return [dict(v, _id=k) for k, v in sorted(m.items()) if isinstance(v, dict)]


def bullets_of(e):
    out = []
    for g in e.get("groups") or []:
        out.extend(x for x in (g.get("items") or []) if isinstance(x, str))
    out.extend(x for x in (e.get("highlights") or []) if isinstance(x, str))
    return out


def ym(s):
    m = re.match(r"^(\d{4})(?:-(\d{2}))?$", str(s or ""))
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)) if m.group(2) else None


def months(y, m):
    return y * 12 + ((m or 1) - 1)


class Report:
    def __init__(self):
        self.checks = []

    def add(self, cid, group, label, maxp, points, findings=None, detail=None):
        self.checks.append({
            "id": cid, "group": group, "label": label, "max": maxp,
            "points": round(max(0.0, min(maxp, points)), 2),
            "findings": findings or [], "detail": detail or {},
        })


def f(severity, message, fix=None, where=None):
    out = {"severity": severity, "message": message}
    if fix:
        out["fix"] = fix
    if where:
        out["where"] = where
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version")
    ap.add_argument("--settings")
    ap.add_argument("--keywords")
    ap.add_argument("--pdf")
    a = ap.parse_args()

    doc = load_doc(a.version)
    settings = json.load(open(a.settings, encoding="utf8")) if a.settings else {}
    if isinstance(settings.get("data"), dict):
        settings = settings["data"]
    lang = (doc.get("lang") or "en")[:2].lower()
    labels = doc.get("labels") or {}
    custom_titles = doc.get("titles") or {}
    profile = doc.get("profile") or {}
    exps, projs = items(doc, "experiences"), items(doc, "projects")
    edus, certs = items(doc, "education"), items(doc, "certifications")
    skills, langs, hobbies = items(doc, "skills"), items(doc, "languages"), items(doc, "hobbies")

    # rubriques affichées, dans l'ordre choisi
    present = {
        "profile": bool(profile.get("summary")), "skills": bool(skills or langs), "experiences": bool(exps),
        "projects": bool(projs), "education": bool(edus or certs), "hobbies": bool(hobbies),
    }
    hidden = set(settings.get("hidden") or [])
    order = [s for s in (settings.get("order") or []) if s in SECTION_IDS] + [s for s in SECTION_IDS if s not in (settings.get("order") or [])]
    visible = [s for s in order if present[s] and s not in hidden]

    def title_of(sid):
        return custom_titles.get(sid) or labels.get("sec_" + sid) or DEFAULT_TITLES.get(lang, DEFAULT_TITLES["en"])[sid]

    R = Report()

    # ---------------- Lisibilité par un parseur (30 points) ----------------
    fnd = []
    pts = 0.0
    if profile.get("fullName"):
        pts += 2
    else:
        fnd.append(f("high", "No full name", "Add the full name: it is the first field a parser extracts.", "profile.fullName"))
    email = str(profile.get("email") or "")
    if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        pts += 2
    else:
        fnd.append(f("high", "No valid e-mail address", "Add an e-mail address in the header: recruiters contact candidates from the parsed field.", "profile.email"))
    if len(re.sub(r"\D", "", str(profile.get("phone") or ""))) >= 8:
        pts += 1
    else:
        fnd.append(f("medium", "No phone number", "Add a phone number with the country code.", "profile.phone"))
    if profile.get("location"):
        pts += 1
    else:
        fnd.append(f("medium", "No location", "Add city and country: many searches filter on location.", "profile.location"))
    R.add("contact", "parsing", "Contact details", 6, pts, fnd)

    fnd, vals = [], []
    for sid in visible:
        t = title_of(sid)
        ok = fold(t) in [fold(x) for x in STANDARD_HEADINGS[sid]]
        vals.append(1.0 if ok else 0.5)
        if not ok:
            fnd.append(f("medium", "Section title \"%s\" is not a standard heading" % t, "Rename it to a standard heading such as \"%s\"." % DEFAULT_TITLES["en"][sid], "titles." + sid))
    R.add("headings", "parsing", "Standard section titles", 4, 4 * (sum(vals) / len(vals)) if vals else 0, fnd)

    fnd, ok_n = [], 0
    for e in exps:
        miss = [k for k, cond in (("title", e.get("title")), ("company", e.get("company")), ("start date", e.get("start")), ("end date or current", e.get("end") or e.get("current"))) if not cond]
        if miss:
            fnd.append(f("high", "Experience \"%s\" lacks: %s" % (e.get("title") or e["_id"], ", ".join(miss)), "Fill these fields: parsers build the employment history from them.", "experiences." + e["_id"]))
        else:
            ok_n += 1
    if not exps:
        fnd.append(f("high", "No professional experience", "Add your experience: it is the core of what parsers and recruiters read.", "experiences"))
    R.add("experience_fields", "parsing", "Complete experience entries", 6, 6 * ok_n / len(exps) if exps else 0, fnd)

    fnd, penalty = [], 0.0
    all_dated = exps + projs + edus + certs
    year_only = 0
    spans = []
    for e in exps:
        s, en = ym(e.get("start")), ym(e.get("end"))
        for k in ("start", "end"):
            v = e.get(k)
            if v and not ym(v):
                penalty += 2
                fnd.append(f("high", "Unreadable date \"%s\"" % v, "Use YYYY-MM.", "experiences.%s.%s" % (e["_id"], k)))
        if s and not s[1] or (en and not en[1]):
            year_only += 1
        if s and en and months(*en) < months(*s):
            penalty += 3
            fnd.append(f("high", "End date before start date in \"%s\"" % (e.get("title") or e["_id"]), "Fix the dates.", "experiences." + e["_id"]))
        if s:
            end_m = months(*en) if en else (date.today().year * 12 + date.today().month - 1 if e.get("current") else None)
            if end_m is not None:
                spans.append((months(*s), end_m, e.get("title") or e["_id"]))
    if year_only:
        penalty += min(3, year_only)
        fnd.append(f("medium", "%d experience(s) with a year-only date" % year_only, "Give month and year (YYYY-MM): a consistent \"Mon YYYY - Mon YYYY\" format is parsed more reliably.", "experiences"))
    spans.sort(key=lambda x: -x[0])
    for newer, older in zip(spans, spans[1:]):
        gap = newer[0] - older[1]
        if gap > 6:
            fnd.append(f("info", "%d-month gap between \"%s\" and \"%s\"" % (gap, older[2], newer[2]), "Recruiters notice gaps: a short line in the profile or a role (freelance, training, project) explains it.", "experiences"))
    R.add("dates", "parsing", "Consistent, readable dates", 5, 5 - penalty, fnd)

    fnd, issues = [], 0
    hard_breaks = [b for e in exps + projs for b in bullets_of(e) if "\n" in b]
    if hard_breaks:
        issues += 1
        fnd.append(f("medium", "%d bullet(s) contain a hard line break" % len(hard_breaks), "Join the lines: a bullet is one string, the layout wraps it."))
    blobs = [str(profile.get("headline") or ""), str(profile.get("summary") or "")] + [b for e in exps + projs for b in bullets_of(e)] + [str(e.get("title") or "") for e in exps]
    odd = sorted({c for t in blobs for c in SAFE_CHARS.findall(t.replace("\n", " "))})
    if odd:
        issues += 1
        fnd.append(f("medium", "Characters outside the PDF font or unusual for parsers: %s" % " ".join(odd[:8]), "Replace them with plain characters (emoji and symbols are dropped or garbled by many parsers)."))
    R.add("hygiene", "parsing", "Clean text", 3, 3 - issues * 1.5, fnd)

    fnd = []
    rank = {s: i for i, s in enumerate(EXPECTED_ORDER)}
    inv = []
    for i in range(len(visible)):
        for j in range(i + 1, len(visible)):
            if rank[visible[i]] > rank[visible[j]]:
                inv.append((visible[i], visible[j]))
    max_inv = len(visible) * (len(visible) - 1) / 2
    if inv:
        fnd.append(f("medium", "Unconventional section order: " + "; ".join("%s before %s" % x for x in inv), "ATS and recruiters expect Profile, then Experience, Education, Skills. Reorder in Customize mode, with the arrows next to each section title.", "settings.order"))
    R.add("order", "parsing", "Conventional section order", 3, 3 * (1 - len(inv) / max_inv) if max_inv else 3, fnd, {"visible_order": visible})

    pdf_report = None
    if a.pdf:
        fnd, pts = [], 0.0
        if not shutil.which("pdftotext"):
            fnd.append(f("info", "pdftotext is not installed: the PDF check was skipped"))
        else:
            txt = subprocess.run(["pdftotext", a.pdf, "-"], capture_output=True, text=True).stdout
            pages = txt.count("\f")
            lines = [l.strip() for l in txt.splitlines() if l.strip()]
            if len(txt.strip()) < 200:
                fnd.append(f("high", "The PDF has (almost) no extractable text", "Export a text-based PDF, not a scan or an image."))
                pdf_report = {"pages": pages, "chars": len(txt)}
            else:
                head = "\n".join(lines[:25])
                has_mail = bool(re.search(r"[^@\s]+@[^@\s]+\.[^@\s]+", head))
                has_phone = len(re.sub(r"\D", "", head)) >= 8
                pts += 0.5 * has_mail + 0.5 * has_phone
                if not (has_mail and has_phone):
                    fnd.append(f("high", "E-mail or phone not found at the top of the extracted text", "Keep the contact details in the body of the first page, not in a header or an image."))
                idx = {}
                for sid in visible:
                    names = {fold(x) for x in STANDARD_HEADINGS[sid]} | {fold(title_of(sid))}
                    for n, l in enumerate(lines):
                        if fold(l) in names:
                            idx[sid] = n
                            break
                found_all = len(idx) == len(visible)
                ordered = found_all and [idx[s] for s in visible] == sorted(idx[s] for s in visible)
                pts += 1.0 if ordered else (0.5 if found_all else 0.5 * len(idx) / max(1, len(visible)))
                if not found_all:
                    fnd.append(f("high", "Section heading(s) not found in the extracted text: %s" % ", ".join(s for s in visible if s not in idx), "Use plain headings on their own line."))
                elif not ordered:
                    fnd.append(f("medium", "Sections come out in a different order in the extracted text", "Check for columns, text boxes or floating elements."))
                bad = txt.count("�") + txt.count("□")
                lone = sum(1 for l in lines if l in ("•", "-", "*", "▪"))
                if bad == 0 and lone == 0:
                    pts += 1
                else:
                    fnd.append(f("medium", "Garbled characters (%d) or bullets alone on a line (%d) in the extracted text" % (bad, lone), "Use a standard font and text bullets."))
                if pages > 2:
                    fnd.append(f("low", "The PDF has %d pages" % pages, "One or two pages is the norm: tighten older roles."))
                pdf_report = {"pages": pages, "chars": len(txt), "sections_found": list(idx)}
        R.add("pdf", "parsing", "Text extracted from the PDF", 3, pts, fnd, pdf_report or {})

    # ---------------- Qualité du contenu (30 points) ----------------
    fnd = []
    sw = words(profile.get("summary"))
    pts = 4 if 30 <= sw <= 150 else (2 if 15 <= sw < 30 or 150 < sw <= 220 else 0)
    if sw == 0:
        fnd.append(f("high", "No professional summary", "Add 3 to 5 lines: role, years of experience, strongest skills, a measurable result.", "profile.summary"))
    elif pts < 4:
        fnd.append(f("medium", "Summary has %d words" % sw, "Aim for 30 to 150 words.", "profile.summary"))
    R.add("summary", "content", "Professional summary", 4, pts, fnd, {"words": sw})

    fnd, ok_n = [], 0
    today = date.today()
    for e in exps:
        b = len(bullets_of(e))
        old = ym(e.get("end")) and today.year - ym(e["end"])[0] > 10
        if 3 <= b <= 12 or (old and b >= 1):
            ok_n += 1
        elif b > 12:
            ok_n += 0.5
            fnd.append(f("low", "\"%s\" has %d bullets" % (e.get("title") or e["_id"], b), "Keep the 8 to 12 strongest bullets: recruiters skim.", "experiences." + e["_id"]))
        else:
            fnd.append(f("medium" if b else "high", "\"%s\" has %d bullet(s)" % (e.get("title") or e["_id"], b), "Give each recent role 3 to 8 bullets (scope, actions, results).", "experiences." + e["_id"]))
    R.add("experience_depth", "content", "Bullets per role", 6, 6 * ok_n / len(exps) if exps else 0, fnd)

    all_bul = [(e.get("title") or e.get("name") or e["_id"], b) for e in exps + projs for b in bullets_of(e)]
    fnd = []
    if all_bul:
        good = [x for x in all_bul if 8 <= words(x[1]) <= 40]
        long_ = sorted((x for x in all_bul if words(x[1]) > 45), key=lambda x: -words(x[1]))
        for t, b in long_[:3]:
            fnd.append(f("medium", "Bullet of %d words in \"%s\": \"%s…\"" % (words(b), t, b[:60]), "Split it into two bullets of 15 to 30 words.", "experiences"))
        R.add("bullet_length", "content", "Readable bullets (8 to 40 words)", 4, 4 * len(good) / len(all_bul), fnd, {"bullets": len(all_bul), "in_range": len(good)})
        quant = [x for x in all_bul if re.search(r"\d", x[1])]
        frac = len(quant) / len(all_bul)
        fnd = []
        if frac < 0.4:
            fnd.append(f("high" if frac < 0.2 else "medium", "Only %d%% of bullets carry a number" % round(frac * 100), "Add figures to the bullets without one: team size, %, time saved, volume, budget. Only use numbers you can back up."))
        R.add("quantified", "content", "Quantified impact", 8, 8 * min(1.0, frac / 0.4), fnd, {"share": round(frac, 2)})
    else:
        R.add("bullet_length", "content", "Readable bullets (8 to 40 words)", 4, 0, [f("high", "No bullets in experiences or projects", "Describe each role with short bullets.")])
        R.add("quantified", "content", "Quantified impact", 8, 0, [])

    fnd = []
    n_sk = len(skills)
    if n_sk < 8:
        fnd.append(f("high" if n_sk < 4 else "medium", "%d skill(s) listed" % n_sk, "List at least 8 skills, tools and methods, written the way job postings write them.", "skills"))
    R.add("skills", "content", "Skills list", 4, 4 * min(1.0, n_sk / 8), fnd, {"count": n_sk})

    fnd = []
    ed = 2 if edus else (1 if certs else 0)
    if ed == 0:
        fnd.append(f("medium", "No education or certification", "Add your highest degree or your certifications.", "education"))
    R.add("education", "content", "Education or certifications", 2, ed, fnd)

    text_parts = [profile.get("headline"), profile.get("summary")]
    for e in exps + projs:
        text_parts += [e.get("title"), e.get("role"), e.get("name"), e.get("company"), e.get("companyDescription"), e.get("description")] + bullets_of(e) + list(e.get("technologies") or [])
    for e in edus:
        text_parts += [e.get("degree"), e.get("field"), e.get("school")]
    for e in certs:
        text_parts += [e.get("name"), e.get("issuer")]
    text_parts += [s.get("name") for s in skills] + [s.get("category") for s in skills] + [x.get("name") for x in langs] + [h.get("name") for h in hobbies]
    total_words = sum(words(t) for t in text_parts if t)
    fnd = []
    pts = 2 if 350 <= total_words <= 1000 else (1 if 250 <= total_words < 350 or 1000 < total_words <= 1400 else 0)
    if total_words < 350:
        fnd.append(f("medium", "%d words in total" % total_words, "The CV is short: develop the recent roles."))
    elif total_words > 1000:
        fnd.append(f("medium", "%d words in total" % total_words, "The CV is long: tighten the oldest roles to stay within two pages."))
    R.add("length", "content", "Length", 2, pts, fnd, {"words": total_words})

    # ---------------- Mots-clés d'une offre (40 points) ----------------
    kw_report = None
    if a.keywords:
        raw = json.load(open(a.keywords, encoding="utf8"))
        kws = raw.get("keywords", raw) if isinstance(raw, dict) else raw
        zones = {
            "title": [profile.get("headline")] + [e.get("title") for e in exps] + [e.get("role") for e in projs],
            "summary": [profile.get("summary")],
            "experience": [t for e in exps + projs for t in ([e.get("description"), e.get("companyDescription"), e.get("company")] + bullets_of(e) + list(e.get("technologies") or []))],
            "skills": [s.get("name") for s in skills] + [s.get("category") for s in skills] + [e.get("name") for e in certs] + [e.get("degree") for e in edus] + [e.get("field") for e in edus],
            "other": [x.get("name") for x in langs] + [h.get("name") for h in hobbies] + [e.get("school") for e in edus],
        }
        folded = {z: " " + " ".join(fold(t) for t in ts if t) + " " for z, ts in zones.items()}
        everything = " ".join(folded.values())

        def pattern(term):
            t = fold(term)
            if not t:
                return None
            body = r"\s+".join(re.escape(p) for p in t.split())
            return re.compile(r"(?<![a-z0-9])" + body + (r"(?:s|es)?" if len(t) > 3 else "") + r"(?![a-z0-9])")

        matched, missing, stuffed = [], [], []
        got, total = 0.0, 0.0
        for k in kws:
            term = k.get("term") if isinstance(k, dict) else str(k)
            kind = (k.get("kind") if isinstance(k, dict) else None) or "other"
            req = bool(k.get("required")) if isinstance(k, dict) else False
            forms = [term] + list((k.get("variants") if isinstance(k, dict) else None) or [])
            w = KIND_WEIGHT.get(kind, 1.0) * (1.5 if req else 1.0)
            total += w
            best, where = 0.0, []
            for z in ("title", "summary", "experience", "skills", "other"):
                if any(p and p.search(folded[z]) for p in map(pattern, forms)):
                    where.append(z)
                    best = max(best, ZONE_WEIGHT[z])
            got += w * best
            count = sum(len(p.findall(everything)) for p in map(pattern, forms) if p)
            if count > 15:
                stuffed.append(term)
            entry = {"term": term, "kind": kind, "required": req}
            if best:
                matched.append(dict(entry, found_in=where, count=count))
            else:
                missing.append(entry)
        coverage = got / total if total else 0.0
        fnd = []
        miss_req = [m for m in missing if m["required"] or m["kind"] in ("hard", "title")]
        if miss_req:
            fnd.append(f("high", "Missing: " + ", ".join(m["term"] for m in miss_req[:12]), "Add each one only where it is true, using the posting's exact wording (and the acronym if the posting uses it), preferably in experience bullets and the headline."))
        only_skills = [m["term"] for m in matched if m["found_in"] and set(m["found_in"]) <= {"skills", "other"}]
        if only_skills:
            fnd.append(f("low", "Only in the skills list: " + ", ".join(only_skills[:10]), "Show them in context too: a bullet that proves the skill."))
        if stuffed:
            fnd.append(f("low", "Possible keyword stuffing: " + ", ".join(stuffed), "Mentioned more than 15 times: keep it natural."))
        R.add("keywords", "keywords", "Keywords of the job posting", KEYWORD_POINTS, KEYWORD_POINTS * coverage, fnd, {"coverage": round(coverage, 3)})
        kw_report = {"coverage": round(coverage, 3), "matched": matched, "missing": missing, "target": 0.75}

    # ---------------- Total ----------------
    groups = {}
    for c in R.checks:
        g = groups.setdefault(c["group"], {"points": 0.0, "max": 0.0})
        g["points"] += c["points"]
        g["max"] += c["max"]
    for g in groups.values():
        g["points"], g["max"] = round(g["points"], 1), round(g["max"], 1)
    use = ["parsing", "content"] + (["keywords"] if kw_report else [])
    pts = sum(groups[g]["points"] for g in use)
    mx = sum(groups[g]["max"] for g in use)
    score = round(100 * pts / mx) if mx else 0
    label = "excellent" if score >= 85 else "good" if score >= 70 else "needs work" if score >= 55 else "weak"
    gaps = sorted(({"id": c["id"], "label": c["label"], "lost": round(c["max"] - c["points"], 1)} for c in R.checks if c["max"] - c["points"] >= 0.5), key=lambda x: -x["lost"])
    report = {
        "score": score, "label": label, "mode": "targeted" if kw_report else "generic",
        "language": lang, "version": doc.get("name"), "groups": groups, "top_gaps": gaps[:8],
        "checks": R.checks, "keywords": kw_report,
        "stats": {"experiences": len(exps), "bullets": len(all_bul), "skills": len(skills), "words": total_words, "visible_sections": visible},
        "note": "Heuristic estimate: no ATS publishes a universal score. See references/ats.md.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
