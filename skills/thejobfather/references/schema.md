# Schéma de la base de données

La base est celle de l'artefact « The Job Father » (capacité `db`). Un document est un objet JSON.
Les chemins de documents ont un nombre pair de segments (`experiences/exp-01`), les collections un nombre impair.

Règles générales :

- Dates au format `YYYY-MM` (ou `YYYY` si le mois est inconnu). `end: null` et `current: true` pour un poste en cours.
- Ne jamais inventer une valeur. Un champ absent de la source est omis ou mis à `null`.
- Les identifiants de documents sont stables et lisibles : `exp-01`, `edu-01`, `skill-01-python`, `lang-en`, `cert-01`, `proj-01`. Numéroter dans l'ordre d'apparition dans la source. Pour les compétences, ce numéro garde l'ordre des catégories et des compétences de la source, car la page les affiche dans l'ordre des identifiants.
- Textes dans la langue du CV, l'anglais par défaut (`settings/layout.lang`). Noms propres, entreprises, écoles, produits, technologies et intitulés officiels de certifications ne se traduisent pas.
- Pas de retour à la ligne dur dans une valeur. Un paragraphe ou une puce est une seule chaîne, même si la source la coupe sur plusieurs lignes. Seul `summary` et `description` peuvent contenir plusieurs paragraphes, séparés par une ligne vide.

## `profile/me` (document unique)

| Champ | Type | Note |
|---|---|---|
| `fullName` | string | |
| `headline` | string | titre / accroche |
| `location` | string | |
| `email`, `phone`, `website` | string | si présents dans la source |
| `age` | number | optionnel, uniquement si la source l'indique (« 37 years old »). Jamais calculé ni déduit. Affiché « 37 years old » (libellé `years_old`) |
| `links` | `[{label, url}]` | LinkedIn, GitHub, portfolio... |
| `summary` | string | résumé / à propos, paragraphes séparés par une ligne vide |
| `photoAssetId` | string \| null | `id` de la photo dans les assets de l'artefact (servie sous `/_blob/<id>`), `null` sans photo |

## `experiences/{id}`

`company`, `companyDescription` (ce que fait l'entreprise, si la source l'indique), `title`, `location`, `start`, `end`, `current` (bool), `description` (string), `employmentType` (CDI, CDD, freelance, stage... si indiqué).

Puces : `groups` (`[{label, items: string[]}]`) quand la source les range sous des sous-titres (ex. « Responsabilités », « Activités », « Résultats »), `highlights` (`string[]`) pour les puces sans sous-titre. Réalisations chiffrées en priorité. Reprendre les libellés de la source.

## `education/{id}`

`school`, `degree`, `field`, `start`, `end`, `description`.

## `skills/{id}`

`name`, `category` (ex. « Langages », « Outils », « Gestion de projet »), `level` (string, uniquement si la source l'indique).

## `languages/{id}`

`name`, `level` (texte de la source : « Natif », « C1 », « Courant »...).

## `certifications/{id}`

`name`, `issuer`, `date`, `url`.

## `projects/{id}`

`name`, `role` (ex. « Founder & CTO »), `description` (ce qu'est le projet), `highlights` (`string[]`), `url`, `start`, `end`, `current` (bool), `technologies` (`string[]`).

## `hobbies/{id}`

`name`, `description` (optionnel). Rubrique « Hobbies », « Centres d'intérêt » ou « Loisirs » de la source. Ne rien créer si la source n'en a pas.

## `settings/layout` (document unique, écrit par la page)

Personnalisation de l'affichage : `order` (`string[]` des rubriques : `profile`, `skills`, `experiences`, `projects`, `education`, `hobbies`), `hidden` (`string[]`), `titles` (`{rubrique: titre}`, remplace le titre par défaut), `theme` (`{accent, title, ink, paper, bg}` en `#rrggbb`), `font` (`modern` | `classic` | `neutral`).

Langue de la fiche : `lang` (code court, `en` par défaut et si le champ est absent) et `labels` (`{clé: texte}`), seuls champs que `init` et `translate` ont le droit de modifier. Les mois sont formatés d'après `lang` (`en` : « Sept. 2024 », autres langues : format du navigateur). Clés de `labels`, toutes à fournir pour une langue autre que `en` et `fr` :

| Clé | Anglais |
|---|---|
| `sec_profile`, `sec_skills`, `sec_experiences`, `sec_projects`, `sec_education`, `sec_hobbies` | Profile, Skills, Professional Experience, Personal Projects, Education & Certifications, Hobbies |
| `languages` | Languages |
| `today` | today |
| `year`, `years`, `month`, `months` | year, years, month, months |
| `col_year`, `col_degree`, `col_institution` | Year, Degree / Certification, Institution |
| `photo_of` | Photo of |
| `years_old` | years old |

Ne jamais écraser ce document en entier : lire, modifier uniquement ce qui est prévu, réécrire.

## `meta/import` (document unique)

| Champ | Type | Note |
|---|---|---|
| `sourceType` | `"pdf"` \| `"linkedin"` | |
| `sourceRef` | string | nom du fichier ou URL du profil |
| `photoSource` | `"site"` \| `"pdf"` \| `"upload"` \| `"kept"` \| `"none"` | origine de la photo choisie par l'utilisateur |
| `importedAt` | string | date ISO |
| `counts` | objet | nombre de documents par collection |
| `warnings` | `string[]` | passages illisibles, champs ambigus, sections ignorées. Écrits en anglais, affichés tels quels dans la page |
| `dismissed` | `string[]` | écrit par la page : avertissements que l'utilisateur a marqués « Seen » (texte identique à celui de `warnings`). Ne jamais le renseigner à l'import : un nouvel import le remet à zéro |

## Règles d'accès

Données personnelles : lecture et écriture réservées au propriétaire de l'artefact.

```json
{ "db": { "rules": [{ "path": "", "read": "owner", "write": "owner" }] } }
```
