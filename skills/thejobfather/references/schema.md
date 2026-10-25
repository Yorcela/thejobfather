# Database schema

The database is the one of the "The Job Father" artifact (`db` capability). A document is a JSON object. Document paths have an even number of segments (`versions/v20261025-1`), collections an odd number.

Places:

| Path | Role | Written by |
|---|---|---|
| `versions/<id>` | a complete resume (one version) | `init`, `translate`, the page |
| `settings/layout` | display shared by all versions (section order, colors) and the displayed version | the page; commands only write `active` |
| `meta/import` | trace of the last import and warnings | `init`, the page (`dismissed`) |
| `settings/preferences` | the user's job preferences, used by `match` | the page ("Preferences" button); commands only read it |
| `answers/<id>` | answers the user gave to `match` questions, kept for a while | `match`; the page (to forget one) |
| `matches/<id>` | one saved matching (resume version + posting), with the whole analysis | `match`; the page (to delete) |
| `offers/<id>` | one tracked job offer and its application | `match` (creates it), `track`; the page (status, form answers, notes) |

There are no longer top-level `profile`, `experiences`, etc. collections: the whole content of a resume lives in its `versions/<id>` document.

## General rules

- Dates in `YYYY-MM` format (or `YYYY` if the month is unknown). `end: null` and `current: true` for a job in progress.
- Never invent a value. A field absent from the source is omitted or set to `null`.
- Text in the language of the version (`lang`), English by default. Proper nouns, companies, schools, products, technologies and official certification titles are not translated.
- No hard line break in a value. A paragraph or a bullet is a single string, even if the source breaks it over several lines. Only `summary` and `description` can contain several paragraphs, separated by a blank line.
- A version is never overwritten by an import or a translation: a new one is created. Only the page modifies an existing version, when the user edits its content.

## `versions/<id>`

Identifier: `v<YYYYMMDD>-<n>`, the creation date and `n` = 1 + the highest number already taken that day (all languages combined). Example: `v20261025-1`, then `v20261025-2`.

| Field | Type | Note |
|---|---|---|
| `name` | string | language flag, space, identifier: `🇫🇷 v20261025-1` |
| `lang` | string | short code of the content language: `en`, `fr`, `es`... |
| `kind` | `"import"` \| `"translation"` \| `"copy"` \| `"adaptation"` \| `"migration"` | how the version came to be (`adaptation`: tailored to a job posting by `adapt`) |
| `parent` | string \| null | identifier of the version it comes from (translation, copy, adaptation) |
| `target` | object | only for an adaptation: `{url, title, company}` of the job posting it was tailored to |
| `createdAt` | string | ISO date |
| `labels` | object | resume labels in this language, see below. `{}` for `en` and `fr` (values built into the page) |
| `titles` | object | custom section titles `{section: title}`, `{}` by default |
| `profile` | object | see below |
| `experiences`, `projects`, `education`, `certifications`, `skills`, `languages`, `hobbies` | object `{identifier: item}` | items described below |

Collections are **objects indexed by identifier**, not arrays. The page displays them in identifier order. Readable, stable identifiers, numbered in order of appearance in the source:

- `exp-01`, `proj-01`, `edu-01`, `cert-01`, `hobby-01`
- `skill-NN-<slug>`: the number keeps the order of the source's categories and skills. When the page edits a category, it writes `skill-NN.MM-<slug>` (NN = category number, MM = rank within the category), which preserves the order.
- `lang-NN-<slug>`: the number keeps the order of the source.

Flags (country code derived from the language, 🌐 by default): `en` 🇬🇧, `fr` 🇫🇷, `es` 🇪🇸, `de` 🇩🇪, `it` 🇮🇹, `pt` 🇵🇹, `nl` 🇳🇱, `pl` 🇵🇱, `sv` 🇸🇪, `da` 🇩🇰, `nb`/`no` 🇳🇴, `fi` 🇫🇮, `cs` 🇨🇿, `ro` 🇷🇴, `hu` 🇭🇺, `el` 🇬🇷, `tr` 🇹🇷, `ru` 🇷🇺, `uk` 🇺🇦, `ja` 🇯🇵, `zh` 🇨🇳, `ko` 🇰🇷, `ar` 🇸🇦, `he` 🇮🇱, `hi` 🇮🇳.

### `profile`

| Field | Type | Note |
|---|---|---|
| `fullName` | string | |
| `headline` | string | title / tagline |
| `location` | string | |
| `email`, `phone`, `website` | string | if present in the source |
| `age` | number | optional, only if the source states it ("37 years old"). Never computed or inferred. Displayed "37 years old" (label `years_old`) |
| `links` | `[{label, url}]` | LinkedIn, GitHub, portfolio... |
| `summary` | string | summary / about, paragraphs separated by a blank line |
| `photoAssetId` | string \| null | `id` of the photo in the artifact's assets (served under `/_blob/<id>`), `null` without a photo |

### `experiences`

`company`, `companyDescription` (what the company does, if the source says so), `title`, `location`, `start`, `end`, `current` (bool), `description` (string), `employmentType` (permanent, fixed-term, freelance, internship... if stated).

Bullets: `groups` (`[{label, items: string[]}]`) when the source lists them under subheadings (e.g. "Responsibilities", "Activities", "Results"), `highlights` (`string[]`) for bullets without a subheading. Quantified achievements first. Keep the source's labels.

### `education`

`school`, `degree`, `field`, `start`, `end`, `description`.

### `skills`

`name`, `category` (e.g. "Languages", "Tools", "Project management"), `level` (string, only if the source states it).

### `languages`

`name`, `level` (text from the source: "Native", "C1", "Fluent"...).

### `certifications`

`name`, `issuer`, `date`, `url`.

### `projects`

`name`, `role` (e.g. "Founder & CTO"), `description` (what the project is), `highlights` (`string[]`), `url`, `start`, `end`, `current` (bool), `technologies` (`string[]`).

### `hobbies`

`name`, `description` (optional). The source's "Hobbies", "Interests" or "Activities" section. Create nothing if the source has none.

### `labels`

Labels of the resume (not of the editing interface, which stays in English). All of them must be provided for a language other than `en` and `fr`:

| Key | English |
|---|---|
| `sec_profile`, `sec_skills`, `sec_experiences`, `sec_projects`, `sec_education`, `sec_hobbies` | Profile, Skills, Professional Experience, Personal Projects, Education & Certifications, Hobbies |
| `languages` | Languages |
| `today` | today |
| `year`, `years`, `month`, `months` | year, years, month, months |
| `col_year`, `col_degree`, `col_institution` | Year, Degree / Certification, Institution |
| `photo_of` | Photo of |
| `years_old` | years old |

Months are formatted according to `lang` (`en`: "Sept. 2024", other languages: browser format).

## `settings/layout`

Display shared by all versions: `order` (`string[]` of sections: `profile`, `skills`, `experiences`, `projects`, `education`, `hobbies`), `hidden` (`string[]`), `theme` (`{accent, title, ink, paper, bg}` as `#rrggbb`), `font` (`modern` | `classic` | `neutral`).

`active`: identifier of the displayed version. Commands may write this single field (read, change `active`, write back, or `update` if it exists), never the rest.

## `settings/preferences`

The user's job preferences, shared by all versions. Every field is optional; a missing field means "no preference". Commands only read this document.

| Field | Type | Note |
|---|---|---|
| `roles` | `[{title, contracts, salary, dailyRate}]` | the roles the user is looking for, each with its own terms. `contracts`: accepted contract types for this role among `permanent`, `fixed-term`, `freelance`, `internship`, `apprenticeship` (several possible, missing means any). `salary` (optional, for employment): `{min, max, currency, period}`, numbers, `currency` such as `EUR`, `period` is `year` or `month`. `dailyRate` (optional, asked when `freelance` is accepted, the TJM): `{min, max, currency}`, numbers, per day |
| `locations` | `[{place, workModes, onsiteDaysMax}]` | where the user wants to work. `place` is a city, region, country or "Remote"; `workModes` lists the accepted modes among `remote`, `hybrid`, `onsite` (several possible, missing means any); `onsiteDaysMax` (0 to 5) only for hybrid |
| `relocation` | boolean | `true` if open to relocation |
| `sectors` | `{prefer: string[], avoid: string[]}` | whitelist and blacklist of sectors |
| `companies` | `{prefer: string[], avoid: string[]}` | companies to join, companies to avoid |
| `companySizes` | `string[]` | `startup` (under 50), `scale-up` (50 to 500), `midsize` (500 to 5,000), `large` (over 5,000) |
| `languages` | `string[]` | working languages |
| `mustHave`, `niceToHave` | `string[]` | free-text criteria, one per entry |
| `dealBreakers` | `string[]` | free-text conditions that rule a job out |
| `notes` | string | anything else |
| `updatedAt` | string | ISO date |

## `answers/<id>`

One document per topic the user answered about in `match`, so the same question is not asked again while the answer still holds. Identifier: `<kind>-<slug of the topic>` (`sector-gambling`, `skill-kubernetes`, `salary-engineering-manager`). A new answer on the same topic replaces the old one. The rules for reusing them are in [match.md](match.md).

| Field | Type | Note |
|---|---|---|
| `kind` | string | `sector`, `company`, `role`, `location`, `work_mode`, `salary`, `skill`, `experience` or `other` |
| `topic` | string | what the answer is about ("gambling", "Kubernetes", "Engineering Manager") |
| `verdict` | string | `refused`, `accepted`, `lacks`, `partial` or `has` |
| `statement` | string | the answer in a sentence, as shown to the user ("No Kubernetes experience in production") |
| `detail` | object | optional. For a refused salary: `{salary: {max_seen, currency, period, role}}`, the highest pay that was refused |
| `from` | `{url, title, company}` | the posting that raised the question |
| `createdAt` | string | ISO date |
| `expiresAt` | string | ISO date, computed with `scripts/answers.py ttl <verdict>`: 7 days for `refused` and `accepted`, 90 for `lacks` and `partial`, 365 for `has` |

An answer whose `expiresAt` is in the past is ignored by `match` and hidden by the page.

## `matches/<id>` and `offers/<id>`

Written by `scripts/offers.py build`, never by hand. The page "My offers" lists them: the matchings tab shows `matches`, the applications board shows `offers`.

**Identifiers.** The posting's address is normalized (host in lower case without `www.`, path without trailing slash, query string without tracking parameters such as `utm_*`, `gclid`, `ref`, the remaining pairs sorted, fragment dropped) and hashed: `hash` = the first 12 characters of the SHA-1. The offer is `offers/o-<hash>`, and the matching is `matches/<versionId>--<hash>`: **one matching per resume version and posting**. `scripts/offers.py key <url>` prints them; the page computes the same values (`normUrl`, `urlHash`).

### `matches/<versionId>--<hash>`

| Field | Type | Note |
|---|---|---|
| `offerId`, `url`, `urlKey` | string | the offer it belongs to, the address as given, the normalized address |
| `versionId`, `versionName` | string | the resume version that was compared |
| `createdAt` | string | ISO date |
| `posting` | object | `title`, `company`, `location`, `work_mode`, `salary`, `contract`, `sector` as read from the posting |
| `score`, `label`, `mode` | number, string, string | from `match_score.py`: `strong`/`good`/`partial`/`weak`, `requirements+preferences` or `requirements` |
| `groups`, `capped`, `dealBreakers` | object, bool, array | points per group, whether the cap applied, deal-breakers found |
| `summary` | string | why this score, in two or three sentences |
| `items` | array | the whole analysis: every requirement and preference with `group`, `label`, `kind`, `status`, `weight`, `max`, `points`, `lost`, `detail` (the evidence) and `source` (`cv`, `user`, `saved answer`, `posting`) |
| `strengths`, `gaps`, `unclear` | array | the top items, as reported |
| `attention` | `string[]` | points of attention that are not scored |
| `next` | object | `highlights` (what to put forward), `recruiterQuestions` |
| `answersUsed` | `string[]` | the saved answers relied on |

### `offers/o-<hash>`

| Field | Type | Note |
|---|---|---|
| `url`, `urlKey`, `title`, `company` | string | the page lets the user fix `title` and `company` |
| `logoAssetId` | string | optional, `id` of the company logo in the artifact's assets (served under `/_blob/<id>`); the page shows the company's initials without one, and lets the user upload a logo |
| `status` | string | `not_applied` (default), `applied`, `response`, `no_response`, `rejected` (by the company), `declined` (by the user) |
| `statusUpdatedAt`, `createdAt` | string | ISO dates |
| `appliedAt` | string | `YYYY-MM-DD`, set when the status first becomes `applied` |
| `cvVersionId` | string | the resume version sent (defaults to the version of the latest matching); the page can open it |
| `formQA` | `[{q, a}]` | the application form: questions and the answers given, to say the same thing during a call |
| `coverLetter`, `notes` | string | |
| `events` | array | history: `{at, type: "status", from, to, by}` with `by` = `user` or `gmail` |
| `emails` | array | found by `track`: `{date, from, subject, kind, snippet}`, `kind` = `response`, `rejected` or `ack`; snippet at most 200 characters, never a whole message |
| `lastEmailCheck` | string | ISO date of the last `track` |

When `match` runs again on a posting whose offer exists, the offer is kept as it is: status, form answers and history belong to the user.

## `meta/import`

| Field | Type | Note |
|---|---|---|
| `sourceType` | `"pdf"` \| `"linkedin"` | |
| `sourceRef` | string | file name or profile URL |
| `photoSource` | `"site"` \| `"pdf"` \| `"upload"` \| `"kept"` \| `"none"` | origin of the photo chosen by the user |
| `importedAt` | string | ISO date |
| `counts` | object | number of items per category |
| `warnings` | `string[]` | unreadable passages, ambiguous fields, skipped sections. Written in English, displayed as-is in the page |
| `dismissed` | `string[]` | written by the page: warnings the user marked "Seen" (same text as in `warnings`). Never set it at import: a new import resets it |

## Access rules

Personal data: read and write restricted to the artifact's owner.

```json
{ "db": { "rules": [{ "path": "", "read": "owner", "write": "owner" }] }, "assets": {}, "downloads": true }
```
