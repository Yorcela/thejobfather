---
name: thejobfather
description: Job search assistant. Subcommands: `init`, which imports the user's profile (PDF resume or a website such as LinkedIn, via Claude in Chrome) into an artifact database, in English by default; `translate`, which translates that profile into the language of their choice by creating a new version, replacing nothing; `ats_score`, which computes an ATS score for the resume (generic or targeted at a job posting) and suggests improvements. Use when the user types /thejobfather, talks about setting up their job search profile, translating their resume, or checking their ATS compatibility.
argument-hint: init | translate [language] | ats_score [job posting]
---

# The Job Father

Entry point of the plugin. Arguments received: `$ARGUMENTS`. The first word is the subcommand, the rest is its complement.

- `init`: see below.
- `translate`: see the bottom of this file. The rest of the arguments is the requested language.
- `ats_score`: see the bottom of this file. The rest of the arguments is the job posting (URL, file path or text) and possibly the path of a PDF.
- empty or unknown: say in one sentence that `init`, `translate` and `ats_score` exist and offer to run `init`.

Reply in the user's language. The questions and button labels written in quotes below are given in English: say them in the user's language.

## `init`

Goal: read all of the user's profile data from the source they choose, and store it in an artifact database as a **new version** of the resume. The artifact then serves as the reference for the rest of the job search, and keeps the history of its versions.

The exact document schema is in [references/schema.md](references/schema.md). Read it before step 3.

### 1. Resuming

Read `~/.thejobfather/config.json` if it exists (key `artifactUrl`). If it does, ask with AskUserQuestion: "Add a new version" (re-import into the same artifact: existing versions are kept) or "Start from scratch" (new artifact). Never delete the old artifact or a version without an explicit request.

### 2. Choosing the source

Ask with AskUserQuestion: "Where do you want to import your profile from?"

- **PDF resume**: ask for the file path ("Other" field or next message).
- **Website (LinkedIn for example)**: ask for the URL of the profile page, then see "Website source" below.

### 3. Extraction

**PDF resume.** Read the file with the Read tool (`pages` parameter in chunks of 20 pages if needed). If the PDF is unreadable (scan without text), say so and ask for another file.

**Website source (LinkedIn for example).** These sites have no public API and block automated reading. Retrieval goes through **Claude in Chrome** (`mcp__claude-in-chrome__*` tools, to be loaded with ToolSearch if deferred), because the user's session is already open there. Do not use the built-in browser or WebFetch for this source.

1. Explicitly ask the user to go through Claude in Chrome to make retrieval easier: tell them to open Chrome with the Claude in Chrome extension enabled and to be signed in to the site. Wait for their confirmation (AskUserQuestion: "Claude in Chrome is ready" or "I prefer a PDF export").
2. If the Claude in Chrome tools are not available or fail to connect, say so, remind them how to install it (the Claude in Chrome extension from the Chrome Web Store, then connect it to Claude Code), and offer to retry or to move on to option 4.
3. Once connected: open the URL in a new tab, read the page with `get_page_text`, and expand sections such as "Show all" (or the equivalent in the site's language) to get the complete experiences, education and skills. Never type credentials. If the site asks for a sign-in, stop, ask the user to sign in themselves in Chrome, then resume.
4. As a last resort, ask the user to export their profile as a PDF (on LinkedIn: "Resources" or "More" button, then "Save to PDF") and treat that file as a PDF resume.

Do not use data found elsewhere on the web.

**Extraction rules** (both sources):

- Only take what the source says. Do not infer, do not embellish, do not invent dates, figures or levels.
- Anything ambiguous or unreadable goes into `meta/import.warnings`, not into a guessed value. Warnings are shown as-is in the page: write them in English.
- The age, if the source states it, goes into the version's `profile.age` (number). Never compute it from a birth date.
- The resume is in English by default. If the source is in another language, translate it faithfully into English (without embellishing or condensing), leaving proper nouns, companies, schools, products, technologies and official certification titles as they are. Add "Translated from <language> to English" to `meta/import.warnings`. Dates stay in `YYYY-MM` format, the page takes care of the display.
- Re-join lines that wrapped naturally. A PDF or web source breaks its sentences at the page width: these breaks are not paragraphs. A paragraph or a bullet is a single string with no line break. Only separate real paragraphs (`summary`, `description`) with a blank line.
- If the full name is not found, stop and say so: the source is probably not a profile.
- Keep the structure of the source. When a job lists its bullets under subheadings (e.g. "Responsibilities", "Activities", "Results"), keep them in `groups`. When the company comes with a description, put it in `companyDescription`. Personal and entrepreneurial companies or projects go in `projects` (with `role`), not in `experiences`.
- Hobbies and interests go in `hobbies`. Create nothing if the source has none.

### 3 bis. Profile photo

The photo is optional and always the user's choice. Before asking, find out what is available:

- **Website source**: the site's profile photo is available. Locate it in the page already open with Claude in Chrome (`find` or `read_page`), taking the main image of the profile header, not the ones for suggestions or contacts.
- **PDF resume source**: look for a photo in the PDF, for example with `pdfimages -png -f 1 -l 1 <resume.pdf> <prefix>` (or, failing that, Python with PyMuPDF run with `-I`), writing the images to the scratchpad folder. Look at the candidates with Read and keep only a portrait. If no photo is found, do not offer that option.

Ask with AskUserQuestion: "Which photo should be used for your profile?" with the options that apply:

- **Use my photo from the website** (website source only).
- **Use the photo from my resume** (PDF source with a photo found only).
- **Share another photo**: ask for the path of an image file (PNG, JPEG or WebP, 20 MiB maximum) and check with Read that it really is an image.
- **No photo**.
- **Keep the current photo** (adding a version to an artifact whose displayed version has a `profile.photoAssetId` set only).

Getting the file:

- **Website photo**: read the image's `src` attribute with `javascript_tool`, then download it with `curl` into a new scratchpad folder, asking for the largest available size. If the download fails, say so and offer "Share another photo" or "No photo" again.
- **Resume photo**: the image extracted above.

Keep the file locally: it is uploaded in step 4, once the artifact is published. Never use a photo found anywhere other than the chosen source or provided by the user. With "No photo", upload nothing and set `photoAssetId` to `null`.

### 4. Creating the artifact

Load the `artifact-capabilities` then `artifact-design` skills if not already done.

Publish with the Artifact tool the file `skills/thejobfather/assets/profile.html` of this plugin (path under `${CLAUDE_PLUGIN_ROOT}`), without modifying it:

- `capabilities`: `{"db": {"rules": [{"path": "", "read": "owner", "write": "owner"}]}, "assets": {}, "downloads": true}`. The data is personal, only the owner reads and writes. `assets` stores the profile photo, `downloads` enables the PDF export.
- `icon`: `"profile"`.
- `description`: "Professional profile and job search database."
- When adding a version (step 1), pass the existing `url`: the page is republished up to date, the data does not move.

The page subscribes to the database and shows an empty state as long as it contains no version.

If a photo was chosen in step 3 bis, then upload it to the artifact's asset store: Artifact call with the artifact's `url`, `asset: true` and the image's `file_path`. Keep the returned `id` for step 5. Only delete an old photo if the user asks.

### 5. Creating the version

The content of a resume is a single document `versions/<id>`, described in `references/schema.md`.

1. List the `versions` collection with `ArtifactData` (load it with ToolSearch if deferred) to choose the identifier: `v<YYYYMMDD>-<n>`, today's date and `n` = 1 + the highest number already taken that day. `name` = language flag + space + identifier (`🇬🇧 v20261025-1`).
2. Build the complete document as a JSON file in the scratchpad: `name`, `lang: "en"`, `kind: "import"`, `parent: null`, `createdAt`, `labels: {}`, `titles: {}`, `profile` (with `photoAssetId`: the asset's `id`, or `null` without a photo), and the collections `experiences`, `projects`, `education`, `certifications`, `skills`, `languages`, `hobbies` as objects indexed by identifier (`exp-01`, `skill-01-<slug>`, `lang-01-<slug>`...).
3. Write this file with `ArtifactData` `set` (`collection: "versions"`, `doc_id`, `file_path`).
4. Write `meta/import` (`set`: it replaces the previous one, which resets `dismissed`) with `sourceType`, `sourceRef`, `photoSource`, `importedAt`, `counts` and `warnings`.
5. Make the new version the displayed one: read `settings/layout`. If it exists, `update` with `if_version` and only `{"active": "<id>"}`. Otherwise `set` with `{"active": "<id>"}`. Never touch the other fields: they belong to the page.

Never modify or delete an existing version: an import always creates a new version. Edits made by hand in the artifact stay in their version.

### 6. Verification and wrap-up

1. Re-read the `versions/<id>` document and compare the number of items in each collection with `counts`. Fix any discrepancy.
2. Save `{ "artifactUrl": "<url>" }` to `~/.thejobfather/config.json` (create the folder if needed).
3. Reply to the user: the artifact link, the name of the version created, the number of items imported per category, and the list of warnings to check. One short sentence, without recapping the resume. Remind them that the resume is in English and that `/thejobfather:thejobfather translate` creates a version in another language.

## `translate`

Goal: translate a version of the resume into the chosen language, by **creating a new version**. Nothing is replaced: the original version and all the others stay intact, and the user finds them in the artifact's "Version" menu (read, delete, copy).

1. Read `~/.thejobfather/config.json`. Without `artifactUrl`, tell the user to run `init` first and stop.
2. Language: the arguments after `translate`, otherwise AskUserQuestion "Which language should the resume be translated into?" (French, Spanish, German, and "Other" for any other). Derive a short code from it (`fr`, `es`, `de`, `pt`, `it`, `nl`...).
3. Read with `ArtifactData` (load it with ToolSearch if deferred) `settings/layout` and the `versions` collection. The source version is the one given by `settings/layout.active`, otherwise the most recent. If its language is already the requested language, say so and stop. If another version already exists in the requested language, point it out and ask with AskUserQuestion whether to create a new one anyway.
4. Prepare the new document in a scratchpad JSON file, from a copy of the source version:
   - `name` = flag + space + identifier, `lang` = the chosen code, `kind: "translation"`, `parent` = the source's identifier, `createdAt` = now. Identifier: `v<YYYYMMDD>-<n>`, see `references/schema.md`.
   - `labels` = all the labels of the table in `references/schema.md`, translated (including `today`, and the plural and singular of months), `titles` = the custom titles, translated if there are any, otherwise `{}`.
   - **to translate**: `profile.headline`, `profile.summary`, `experiences` (`title`, `companyDescription`, `employmentType`, `description`, `groups[].label`, `groups[].items`, `highlights`), `projects` (`role`, `description`, `highlights`), `education` (`degree`, `field`, `description`), `skills` (`name`, `category`, `level`), `languages` (`name`, `level`), `hobbies` (`name`, `description`).
   - **to leave as is**: `fullName`, `age`, places, companies, schools, organizations, project names, technologies, certification titles, links, e-mail, phone, dates, `photoAssetId`, item identifiers. Common English job titles (Scrum Master, Head of Agile, Senior Engineering Manager...) stay in English when professionals in the target language keep them as they are.
   - Faithful translation: no additions, no removals, no flattering rewording. No hard line breaks in a value. If the language inflects words by gender, do not guess the user's: use neutral wording.
5. Write the file with `ArtifactData` `set` on `versions/<id>`. Then make the new version the displayed one: `update` of `settings/layout` with `if_version` and only `{"active": "<id>"}`.
6. Re-read the new version and check that the number of items in each collection is the same as in the source.
7. Reply: the artifact link, the name of the new version and the version it comes from, and what was deliberately left as is (proper nouns, certifications, job titles). One short sentence.

## `ats_score`

Goal: estimate the ATS compatibility of a version of the resume with a score out of 100, and suggest concrete improvements. There is no universal ATS score: the scoring scale is ours, and it is described with its sources in [references/ats.md](references/ats.md). Read it before explaining a result.

Two modes:

- **generic** (no job posting): readability by a parser and content quality;
- **targeted** (with a job posting): in addition, coverage of the posting's keywords, which weigh 40 points. This is the score that matters for a specific application.

1. Read `~/.thejobfather/config.json`. Without `artifactUrl`, tell the user to run `init` first and stop.
2. Job posting: the arguments after `ats_score` (URL, file path or pasted text). If empty, ask with AskUserQuestion: "Which score should be computed?" with "Generic (no job posting)" and "Targeted at a job posting" (the URL, path or text comes through "Other"). For a URL, use WebFetch; if the page is protected or empty (LinkedIn for example), go through Claude in Chrome as for `init`, or ask the user to paste the text. If the arguments contain a path ending in `.pdf`, it is the PDF export of the resume to check (step 5), not the job posting.
3. Read with `ArtifactData` (load it with ToolSearch if deferred), with `out_dir` in the scratchpad: `settings/layout` (displayed version in `active`, order and hiding of sections), then the displayed version in `versions/<active>`, otherwise the most recent. Say which version is evaluated (its `name`).
4. With a job posting, write a `keywords.json` file in the scratchpad: a list of 15 to 40 objects `{"term", "kind", "required", "variants"}`.
   - `kind`: `hard` (tools, technologies, methods, professional skills), `title` (targeted job title), `education` (required degree or certification), `soft` (soft skills), `other`.
   - `required`: `true` when the posting says required, essential, must, or when the term is in the list of prerequisites.
   - `variants`: only real synonyms that the posting or the profession uses (acronym and expanded form, irregular singular and plural, equivalent in the posting's other language). Nothing else.
   - Only include terms present in the posting. No generic verbs or empty phrases ("dynamic", "passionate").
5. If the user has a PDF export of the resume, add `--pdf <path>`: it checks what a parser really extracts from the file (the artifact's "Export PDF" button produces it). Otherwise, do not insist: mention it in the report as a check not done.
6. Run: `python3 -I ${CLAUDE_PLUGIN_ROOT}/skills/thejobfather/scripts/ats_score.py <version.json> --settings <layout.json> [--keywords <keywords.json>] [--pdf <resume.pdf>]`. The script writes a JSON report (score, `groups`, `checks` with their `findings`, `top_gaps`, `keywords`). Never recompute the score by hand: report it as is.
7. Reply concisely, in the user's language:
   - the score, its label, the mode (generic or targeted) and the evaluated version;
   - a table by category (readability, content, keywords if targeted) with the points;
   - **5 to 7 improvements at most**, ranked by recoverable points (`top_gaps`), each with what is wrong, where, and a concrete proposal: a rewritten sentence, a title to rename, an order to change. Write the proposals in the language of the resume;
   - in targeted mode: the coverage rate, the keywords found (and where) and missing. For each missing one, say whether the resume shows an experience that justifies it (then propose where to write it, using the posting's words) or whether it is a real gap (say so, invent nothing, suggest adding it only if it is true);
   - a one-line caveat: it is an estimate, no ATS publishes a universal score, and recruiters also read the resume.
8. Then offer to apply the improvements that only touch the text and the order of sections. With AskUserQuestion (multiple choice), let the user tick the ones to apply. For those chosen, create a **new version** (`kind: "copy"`, `parent` = the evaluated version, same language, identifier and name as in [references/schema.md](references/schema.md), as for `translate`) and make it the displayed one via `settings/layout.active`. Never modify the evaluated version. The order of sections is a setting shared by all versions (`settings/layout.order`): only change it with the user's explicit agreement, and say so. Add no fact absent from the resume: an improvement that needs information only the user knows (a figure, a tool) is put to them as a question.
9. After applying, run the script again on the new version and show the score before and after. If nothing is applied, end on the report.
