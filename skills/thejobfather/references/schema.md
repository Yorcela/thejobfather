# Database schema

The database is the one of the "The Job Father" artifact (`db` capability). A document is a JSON object. Document paths have an even number of segments (`versions/v20261025-1`), collections an odd number.

Three places:

| Path | Role | Written by |
|---|---|---|
| `versions/<id>` | a complete resume (one version) | `init`, `translate`, the page |
| `settings/layout` | display shared by all versions (section order, colors) and the displayed version | the page; commands only write `active` |
| `meta/import` | trace of the last import and warnings | `init`, the page (`dismissed`) |

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
| `kind` | `"import"` \| `"translation"` \| `"copy"` \| `"migration"` | how the version came to be |
| `parent` | string \| null | identifier of the version it comes from (translation, copy) |
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
