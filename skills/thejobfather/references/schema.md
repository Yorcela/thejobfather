# Schéma de la base de données

La base est celle de l'artefact « The Job Father » (capacité `db`). Un document est un objet JSON. Les chemins de documents ont un nombre pair de segments (`versions/v20261025-1`), les collections un nombre impair.

Trois endroits :

| Chemin | Rôle | Écrit par |
|---|---|---|
| `versions/<id>` | un CV complet (une version) | `init`, `translate`, la page |
| `settings/layout` | affichage commun à toutes les versions (ordre des rubriques, couleurs) et version affichée | la page ; les commandes n'écrivent que `active` |
| `meta/import` | trace du dernier import et avertissements | `init`, la page (`dismissed`) |

Il n'y a plus de collections `profile`, `experiences`, etc. au premier niveau : tout le contenu d'un CV vit dans son document `versions/<id>`.

## Règles générales

- Dates au format `YYYY-MM` (ou `YYYY` si le mois est inconnu). `end: null` et `current: true` pour un poste en cours.
- Ne jamais inventer une valeur. Un champ absent de la source est omis ou mis à `null`.
- Textes dans la langue de la version (`lang`), l'anglais par défaut. Noms propres, entreprises, écoles, produits, technologies et intitulés officiels de certifications ne se traduisent pas.
- Pas de retour à la ligne dur dans une valeur. Un paragraphe ou une puce est une seule chaîne, même si la source la coupe sur plusieurs lignes. Seuls `summary` et `description` peuvent contenir plusieurs paragraphes, séparés par une ligne vide.
- Une version n'est jamais écrasée par un import ou une traduction : on en crée une nouvelle. Seule la page modifie une version existante, quand l'utilisateur édite son contenu.

## `versions/<id>`

Identifiant : `v<YYYYMMDD>-<n>`, la date du jour de création et `n` = 1 + le plus grand numéro déjà pris ce jour-là (toutes langues confondues). Exemple : `v20261025-1`, puis `v20261025-2`.

| Champ | Type | Note |
|---|---|---|
| `name` | string | drapeau de la langue, espace, identifiant : `🇫🇷 v20261025-1` |
| `lang` | string | code court de la langue du contenu : `en`, `fr`, `es`... |
| `kind` | `"import"` \| `"translation"` \| `"copy"` \| `"migration"` | comment la version est née |
| `parent` | string \| null | identifiant de la version dont elle est issue (traduction, copie) |
| `createdAt` | string | date ISO |
| `labels` | objet | libellés de la fiche dans cette langue, voir plus bas. `{}` pour `en` et `fr` (valeurs intégrées à la page) |
| `titles` | objet | titres de rubriques personnalisés `{rubrique: titre}`, `{}` par défaut |
| `profile` | objet | voir plus bas |
| `experiences`, `projects`, `education`, `certifications`, `skills`, `languages`, `hobbies` | objet `{identifiant: élément}` | éléments décrits plus bas |

Les collections sont des **objets indexés par identifiant**, pas des tableaux. La page les affiche dans l'ordre des identifiants. Identifiants lisibles et stables, numérotés dans l'ordre d'apparition dans la source :

- `exp-01`, `proj-01`, `edu-01`, `cert-01`, `hobby-01`
- `skill-NN-<slug>` : le numéro garde l'ordre des catégories et des compétences de la source. Quand la page édite une catégorie, elle écrit `skill-NN.MM-<slug>` (NN = numéro de la catégorie, MM = rang dans la catégorie), ce qui conserve l'ordre.
- `lang-NN-<slug>` : le numéro garde l'ordre de la source.

Drapeaux (code de pays déduit de la langue, par défaut 🌐) : `en` 🇬🇧, `fr` 🇫🇷, `es` 🇪🇸, `de` 🇩🇪, `it` 🇮🇹, `pt` 🇵🇹, `nl` 🇳🇱, `pl` 🇵🇱, `sv` 🇸🇪, `da` 🇩🇰, `nb`/`no` 🇳🇴, `fi` 🇫🇮, `cs` 🇨🇿, `ro` 🇷🇴, `hu` 🇭🇺, `el` 🇬🇷, `tr` 🇹🇷, `ru` 🇷🇺, `uk` 🇺🇦, `ja` 🇯🇵, `zh` 🇨🇳, `ko` 🇰🇷, `ar` 🇸🇦, `he` 🇮🇱, `hi` 🇮🇳.

### `profile`

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

### `experiences`

`company`, `companyDescription` (ce que fait l'entreprise, si la source l'indique), `title`, `location`, `start`, `end`, `current` (bool), `description` (string), `employmentType` (CDI, CDD, freelance, stage... si indiqué).

Puces : `groups` (`[{label, items: string[]}]`) quand la source les range sous des sous-titres (ex. « Responsabilités », « Activités », « Résultats »), `highlights` (`string[]`) pour les puces sans sous-titre. Réalisations chiffrées en priorité. Reprendre les libellés de la source.

### `education`

`school`, `degree`, `field`, `start`, `end`, `description`.

### `skills`

`name`, `category` (ex. « Langages », « Outils », « Gestion de projet »), `level` (string, uniquement si la source l'indique).

### `languages`

`name`, `level` (texte de la source : « Natif », « C1 », « Courant »...).

### `certifications`

`name`, `issuer`, `date`, `url`.

### `projects`

`name`, `role` (ex. « Founder & CTO »), `description` (ce qu'est le projet), `highlights` (`string[]`), `url`, `start`, `end`, `current` (bool), `technologies` (`string[]`).

### `hobbies`

`name`, `description` (optionnel). Rubrique « Hobbies », « Centres d'intérêt » ou « Loisirs » de la source. Ne rien créer si la source n'en a pas.

### `labels`

Libellés de la fiche (pas de l'interface d'édition, qui reste en anglais). À fournir tous pour une langue autre que `en` et `fr` :

| Clé | Anglais |
|---|---|
| `sec_profile`, `sec_skills`, `sec_experiences`, `sec_projects`, `sec_education`, `sec_hobbies` | Profile, Skills, Professional Experience, Personal Projects, Education & Certifications, Hobbies |
| `languages` | Languages |
| `today` | today |
| `year`, `years`, `month`, `months` | year, years, month, months |
| `col_year`, `col_degree`, `col_institution` | Year, Degree / Certification, Institution |
| `photo_of` | Photo of |
| `years_old` | years old |

Les mois sont formatés d'après `lang` (`en` : « Sept. 2024 », autres langues : format du navigateur).

## `settings/layout`

Affichage commun à toutes les versions : `order` (`string[]` des rubriques : `profile`, `skills`, `experiences`, `projects`, `education`, `hobbies`), `hidden` (`string[]`), `theme` (`{accent, title, ink, paper, bg}` en `#rrggbb`), `font` (`modern` | `classic` | `neutral`).

`active` : identifiant de la version affichée. Les commandes peuvent écrire ce seul champ (lire, modifier `active`, réécrire, ou `update` s'il existe), jamais le reste.

## `meta/import`

| Champ | Type | Note |
|---|---|---|
| `sourceType` | `"pdf"` \| `"linkedin"` | |
| `sourceRef` | string | nom du fichier ou URL du profil |
| `photoSource` | `"site"` \| `"pdf"` \| `"upload"` \| `"kept"` \| `"none"` | origine de la photo choisie par l'utilisateur |
| `importedAt` | string | date ISO |
| `counts` | objet | nombre d'éléments par catégorie |
| `warnings` | `string[]` | passages illisibles, champs ambigus, sections ignorées. Écrits en anglais, affichés tels quels dans la page |
| `dismissed` | `string[]` | écrit par la page : avertissements que l'utilisateur a marqués « Seen » (texte identique à celui de `warnings`). Ne jamais le renseigner à l'import : un nouvel import le remet à zéro |

## Règles d'accès

Données personnelles : lecture et écriture réservées au propriétaire de l'artefact.

```json
{ "db": { "rules": [{ "path": "", "read": "owner", "write": "owner" }] }, "assets": {}, "downloads": true }
```
