# Schéma de la base de données

La base est celle de l'artefact « The Job Father » (capacité `db`). Un document est un objet JSON.
Les chemins de documents ont un nombre pair de segments (`experiences/exp-01`), les collections un nombre impair.

Règles générales :

- Dates au format `YYYY-MM` (ou `YYYY` si le mois est inconnu). `end: null` et `current: true` pour un poste en cours.
- Ne jamais inventer une valeur. Un champ absent de la source est omis ou mis à `null`.
- Les identifiants de documents sont stables et lisibles : `exp-01`, `edu-01`, `skill-python`, `lang-en`, `cert-01`, `proj-01`. Numéroter dans l'ordre d'apparition dans la source.
- Textes en français ou dans la langue d'origine de la source, sans traduction.

## `profile/me` (document unique)

| Champ | Type | Note |
|---|---|---|
| `fullName` | string | |
| `headline` | string | titre / accroche |
| `location` | string | |
| `email`, `phone`, `website` | string | si présents dans la source |
| `links` | `[{label, url}]` | LinkedIn, GitHub, portfolio... |
| `summary` | string | résumé / à propos |

## `experiences/{id}`

`company`, `title`, `location`, `start`, `end`, `current` (bool), `description` (string), `highlights` (`string[]`, réalisations chiffrées en priorité), `employmentType` (CDI, CDD, freelance, stage... si indiqué).

## `education/{id}`

`school`, `degree`, `field`, `start`, `end`, `description`.

## `skills/{id}`

`name`, `category` (ex. « Langages », « Outils », « Gestion de projet »), `level` (string, uniquement si la source l'indique).

## `languages/{id}`

`name`, `level` (texte de la source : « Natif », « C1 », « Courant »...).

## `certifications/{id}`

`name`, `issuer`, `date`, `url`.

## `projects/{id}`

`name`, `description`, `url`, `start`, `end`, `technologies` (`string[]`).

## `meta/import` (document unique)

| Champ | Type | Note |
|---|---|---|
| `sourceType` | `"pdf"` \| `"linkedin"` | |
| `sourceRef` | string | nom du fichier ou URL du profil |
| `importedAt` | string | date ISO |
| `counts` | objet | nombre de documents par collection |
| `warnings` | `string[]` | passages illisibles, champs ambigus, sections ignorées |

## Règles d'accès

Données personnelles : lecture et écriture réservées au propriétaire de l'artefact.

```json
{ "db": { "rules": [{ "path": "", "read": "owner", "write": "owner" }] } }
```
