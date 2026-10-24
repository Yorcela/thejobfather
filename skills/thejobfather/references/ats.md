# ATS score: what is known, what we measure

## What the sources establish

- **There is no universal ATS score.** No ATS vendor publishes a common scoring scale. The "scores out of 100" of tools (Jobscan, ATS Resume AI and others) are estimates specific to each tool, useful as an indication, not as a prediction of the outcome at a given employer. The weights and thresholds those tools publish are the vendor's own choices.
- **Parsing comes first.** The ATS extracts fields from the file (name, e-mail, phone, latest job title and employer, years of experience, education, skills). A badly read field stays empty, and a recruiter who filters on it will not see the candidate. Multi-column layouts, tables, text boxes, headers and footers, text as images and original section titles are the most cited causes of failure.
- **Recruiters search by keywords** (skills, titles), often literally according to third-party guides: "GA4" and "Google Analytics" can be two different terms, and an unexpanded acronym can be missed. Terms placed in the experience and the title weigh more than a simple skills list. Keyword stuffing is spotted by recruiters as well as by tools.
- **A score does not reject automatically.** Greenhouse states that its Talent Matching neither rejects nor advances any candidate, that it ranks according to criteria the team calibrates (required skills, experience, titles) and maps related terms to the same skill. Automatic rejections come from rules set by the recruiter, such as a "no" answer to a work-authorization question. The idea of a secret threshold ("75% rejected") is disputed: most of the time the resume is stored but does not show up in the recruiter's searches.
- **Jobscan compares the resume to a job posting.** The "match rate" (0 to 100%) compares hard skills, education level (if the posting requires one), job title, soft skills and other keywords, in that order of priority. Word count and measurable results do not count in this rate. The recommended target is at least 75%, without aiming for 100% (artificial text).
- **File format: no consensus.** Some guides prefer DOCX, others a text-based PDF. The common ground: the text must be selectable (not an image), the layout single-column, and it is best to follow the posting's instructions.
- **Other practices backed by several guides**: dates in a single format and in reverse chronological order, contact details in the body of the document, standard section titles, Experience section first after the profile.

Limits of these sources: most are blogs from resume-tool vendors, not ATS documentation. The scale below is therefore **our** scale, built on this consensus. It measures the readability and quality of the resume, and the coverage of a job posting's keywords. It does not predict the outcome at a given employer.

## Scoring scale (100 points)

Without a job posting, the score is **generic**: readability (30) and content (30), scaled to 100. With a job posting, it is **targeted**: readability (30), content (30) and keywords (40), which reflects the weight of keywords in searches and in the match rate. When the PDF is not provided, its 3 points are removed from the total, not counted as lost.

### Readability by a parser (30)

| Check | Pts | Rule |
|---|---|---|
| Contact details | 6 | name (2), valid e-mail (2), phone with at least 8 digits (1), location (1) |
| Standard section titles | 4 | each displayed title is in the list of recognized headings (Profile, Experience, Education, Skills... and French equivalents); an unknown title is worth half |
| Complete experiences | 6 | title, company, start, end or "current" for each job |
| Dates | 5 | readable format, no date without a month (−1 per job, max −3), no end before start (−3); a gap of more than 6 months is flagged, without penalty |
| Clean text | 3 | no hard line break in a bullet, no exotic character or emoji |
| Section order | 3 | expected order: Profile, Experience, Projects, Education, Skills, Hobbies; removes points in proportion to the inversions |
| PDF extraction (optional) | 3 | contact details at the top of the extracted text (1), sections found in order (1), no corrupted characters or lone bullet (1). A PDF without extractable text is flagged as serious |

### Content quality (30)

| Check | Pts | Rule |
|---|---|---|
| Summary | 4 | 30 to 150 words (half the points for 15 to 29 or 151 to 220) |
| Bullets per job | 6 | 3 to 12 bullets for each job (a job older than 10 years may have fewer); above 12, half points |
| Readable bullets | 4 | share of bullets of 8 to 40 words; bullets over 45 words are cited |
| Quantified results | 8 | share of bullets containing a number, full points from 40% |
| Skills | 4 | at least 8 skills listed |
| Education | 2 | a degree (2) or only certifications (1) |
| Length | 2 | 350 to 1,000 words in total (1 point for 250 to 349 or 1,001 to 1,400) |

### Job posting keywords (40, with a job posting only)

Terms are extracted from the posting (see `SKILL.md`), then searched in the resume ignoring case and accents, with simple plurals and the declared variants.

- **Weight by type**, following Jobscan's priority order: hard skills 3, job title 3, education level 2, soft skills 1, others 1. A "required" term counts one and a half times.
- **Where it is found**: in the title, summary or experience, it counts 1; only in the skills list or elsewhere, 0.7.
- **Coverage** = weighted sum of the terms found over the sum of the weights. Points = 40 × coverage. Recommended target: 75% or more.
- **Stuffing**: a term mentioned more than 15 times is flagged.

### Reading the score

85 and above: excellent. 70 to 84: good. 55 to 69: needs work. Below 55: weak. A generic score of 90 says nothing about a specific posting: the targeted score is the one that matters when applying.

## Sources

- Greenhouse, [Talent Matching FAQ](https://support.greenhouse.io/hc/en-us/articles/41131886674075-Talent-Matching-FAQ): no automatic rejection or advancement, match categories, related terms mapped to the same skill.
- Greenhouse, [Search resumes for keywords](https://support.greenhouse.io/hc/en-us/articles/115004600186-Search-resumes-for-keywords): full-text search across applications (the page does not detail the matching mode).
- Jobscan, [Jobscan Tutorial](https://www.jobscan.co/jobscan-tutorial): what the match rate compares, keyword priority order, 75% target, word count and measurable results excluded from the rate.
- ATS Verification, [How ATS scoring works](https://atsverification.com/blog/how-ats-scoring-works/): extracted fields, recruiters filtering by fields and keywords, formats that break parsing, absence of a universal score (article by a tool vendor).
- ATS Resume AI, [Resume ATS scoring criteria](https://www.atsresumeai.com/blog/resume-ats-score): example of a weighted grid (the vendor's own scale, which itself acknowledges the absence of a standard).
- Formatting guides: [University at Buffalo](https://management.buffalo.edu/career-resource-center/students/preparation/tools/correspondence/resume/electronic.html), [Adobe Express](https://www.adobe.com/express/discover/tips/ats-resume-tips), [Scale.jobs](https://scale.jobs/blog/ats-resume-format-works-2026): single column, no tables or text boxes, standard titles, consistent dates, contact details in the body of the document.
