---
name: thejobfather
description: Assistant de recherche d'emploi. Sous-commandes : `init`, qui importe le profil de l'utilisateur (CV PDF ou site web comme LinkedIn, via Claude in Chrome) dans la base de données d'un artefact, en anglais par défaut ; `translate`, qui traduit ce profil dans la langue de son choix en créant une nouvelle version, sans rien remplacer. À utiliser quand l'utilisateur tape /thejobfather, parle d'initialiser son profil de recherche d'emploi ou de traduire son CV.
argument-hint: init | translate [langue]
---

# The Job Father

Point d'entrée du plugin. Le premier argument est la sous-commande : `$ARGUMENTS`

- `init` : voir ci-dessous.
- `translate` : voir tout en bas. Le reste de l'argument est la langue demandée.
- vide ou inconnue : dire en une phrase que `init` et `translate` existent et proposer de lancer `init`.

Répondre en français.

## `init`

Objectif : lire toutes les données de profil de l'utilisateur dans la source qu'il choisit, et les stocker dans la base de données d'un artefact, sous la forme d'une **nouvelle version** du CV. L'artefact sert ensuite de référence pour tout le reste de la recherche d'emploi, et garde l'historique de ses versions.

Le schéma exact des documents est dans [references/schema.md](references/schema.md). Le lire avant l'étape 3.

### 1. Reprise éventuelle

Lire `~/.thejobfather/config.json` s'il existe (clé `artifactUrl`). S'il existe, demander avec AskUserQuestion : « Ajouter une nouvelle version » (réimporter dans le même artefact : les versions existantes sont conservées) ou « Repartir de zéro » (nouvel artefact). Ne jamais supprimer l'ancien artefact ni une version sans demande explicite.

### 2. Choix de la source

Poser la question avec AskUserQuestion : « D'où voulez-vous importer votre profil ? »

- **CV au format PDF** : demander le chemin du fichier (champ « Other » ou message suivant).
- **Site web (LinkedIn par exemple)** : demander l'URL de la page de profil, puis voir « Source site web » plus bas.

### 3. Extraction

**CV PDF.** Lire le fichier avec l'outil Read (paramètre `pages` par tranches de 20 pages si besoin). Si le PDF est illisible (scan sans texte), le dire et demander un autre fichier.

**Source site web (LinkedIn par exemple).** Ces sites n'ont pas d'API publique et bloquent la lecture automatisée. La récupération passe par **Claude in Chrome** (outils `mcp__claude-in-chrome__*`, à charger via ToolSearch s'ils sont différés), car la session de l'utilisateur y est déjà ouverte. Ne pas utiliser le navigateur intégré ni WebFetch pour cette source.

1. Demander explicitement à l'utilisateur de passer par Claude in Chrome pour faciliter la récupération : lui dire d'ouvrir Chrome avec l'extension Claude in Chrome activée et d'être connecté au site concerné. Attendre sa confirmation (AskUserQuestion : « Claude in Chrome est prêt » ou « Je préfère un export PDF »).
2. Si les outils Claude in Chrome ne sont pas disponibles ou ne se connectent pas, l'indiquer, rappeler comment l'installer (extension Claude in Chrome depuis le Chrome Web Store, puis connexion à Claude Code), et proposer de réessayer ou de passer à l'option 4.
3. Une fois connecté : ouvrir l'URL dans un nouvel onglet, lire la page avec `get_page_text`, et déplier les sections du type « Afficher tout » pour obtenir les expériences, formations et compétences complètes. Ne jamais saisir d'identifiants. Si le site demande une connexion, s'arrêter, demander à l'utilisateur de se connecter lui-même dans Chrome, puis reprendre.
4. En dernier recours, demander à l'utilisateur d'exporter son profil en PDF (sur LinkedIn : bouton « Ressources » ou « Plus » puis « Enregistrer au format PDF ») et traiter ce fichier comme un CV PDF.

Ne pas utiliser de données trouvées ailleurs sur le web.

**Règles d'extraction** (les deux sources) :

- Ne reprendre que ce que la source dit. Ne rien déduire, ne rien embellir, ne pas inventer de dates, de chiffres ni de niveaux.
- Ce qui est ambigu ou illisible va dans `meta/import.warnings`, pas dans une valeur devinée. Les avertissements sont affichés tels quels dans la page : les écrire en anglais.
- L'âge, s'il est écrit dans la source, va dans `profile.age` de la version (nombre). Ne jamais le calculer à partir d'une date de naissance.
- Le CV est en anglais par défaut. Si la source est dans une autre langue, traduire fidèlement en anglais (sans embellir ni condenser), en laissant tels quels les noms propres, entreprises, écoles, produits, technologies et intitulés officiels de certifications. Noter dans `meta/import.warnings` « Translated from <language> to English ». Les dates restent au format `YYYY-MM`, la page se charge de l'affichage.
- Recoller les lignes coupées naturellement. Une source PDF ou web coupe ses phrases à la largeur de la page : ces retours ne sont pas des paragraphes. Un paragraphe ou une puce est une seule chaîne sans retour à la ligne. Ne séparer par une ligne vide que de vrais paragraphes (`summary`, `description`).
- Si le nom complet n'est pas trouvé, arrêter et le dire : la source n'est probablement pas un profil.
- Reprendre la structure de la source. Quand un poste range ses puces sous des sous-titres (ex. « Responsabilités », « Activités », « Résultats »), les garder dans `groups`. Quand l'entreprise est accompagnée d'une description, la mettre dans `companyDescription`. Les entreprises ou projets personnels et entrepreneuriaux vont dans `projects` (avec `role`), pas dans `experiences`.
- Les loisirs, hobbies ou centres d'intérêt vont dans `hobbies`. Ne rien créer si la source n'en a pas.

### 3 bis. Photo de profil

La photo est facultative et toujours le choix de l'utilisateur. Avant de poser la question, repérer ce qui est disponible :

- **Source site web** : la photo de profil du site est disponible. La repérer dans la page déjà ouverte avec Claude in Chrome (`find` ou `read_page`), en prenant l'image principale de l'en-tête du profil et non celles des suggestions ou des contacts.
- **Source CV PDF** : chercher une photo dans le PDF, par exemple avec `pdfimages -png -f 1 -l 1 <cv.pdf> <préfixe>` (ou, à défaut, Python avec PyMuPDF lancé avec `-I`), en écrivant les images dans le dossier scratchpad. Regarder les candidates avec Read et ne retenir qu'un portrait. Si aucune photo n'est trouvée, ne pas proposer cette option.

Poser la question avec AskUserQuestion : « Quelle photo utiliser pour votre profil ? » avec les options qui s'appliquent :

- **Reprendre ma photo du site** (source site web uniquement).
- **Reprendre la photo de mon CV** (source CV PDF avec photo trouvée uniquement).
- **Partager une autre photo** : demander le chemin d'un fichier image (PNG, JPEG ou WebP, 20 Mio maximum) et vérifier avec Read qu'il s'agit bien d'une image.
- **Sans photo**.
- **Garder la photo actuelle** (ajout d'une version à un artefact dont la version affichée a un `profile.photoAssetId` renseigné uniquement).

Obtention du fichier :

- **Photo du site** : lire l'attribut `src` de l'image avec `javascript_tool`, puis la télécharger avec `curl` dans un dossier neuf du scratchpad, en demandant la plus grande taille disponible. Si le téléchargement échoue, le dire et reproposer « Partager une autre photo » ou « Sans photo ».
- **Photo du CV** : l'image extraite ci-dessus.

Garder le fichier en local : il est envoyé à l'étape 4, une fois l'artefact publié. Ne jamais utiliser une photo trouvée ailleurs que dans la source choisie ou fournie par l'utilisateur. Avec « Sans photo », ne rien envoyer et mettre `photoAssetId` à `null`.

### 4. Création de l'artefact

Charger les skills `artifact-capabilities` puis `artifact-design` si ce n'est pas déjà fait.

Publier avec l'outil Artifact le fichier `skills/thejobfather/assets/profile.html` de ce plugin (chemin sous `${CLAUDE_PLUGIN_ROOT}`), sans le modifier :

- `capabilities`: `{"db": {"rules": [{"path": "", "read": "owner", "write": "owner"}]}, "assets": {}, "downloads": true}`. Les données sont personnelles, seul le propriétaire lit et écrit. `assets` stocke la photo de profil, `downloads` permet l'export PDF.
- `icon`: `"profile"`.
- `description`: « Profil professionnel et base de données de la recherche d'emploi. »
- En cas d'ajout d'une version (étape 1), passer l'`url` existante : la page est republiée à jour, les données ne bougent pas.

La page s'abonne à la base et affiche un état vide tant qu'elle ne contient aucune version.

Si une photo a été choisie à l'étape 3 bis, l'envoyer ensuite dans l'espace d'assets de l'artefact : appel Artifact avec l'`url` de l'artefact, `asset: true` et `file_path` du fichier image. Garder l'`id` retourné pour l'étape 5. Ne supprimer une ancienne photo que si l'utilisateur le demande.

### 5. Création de la version

Le contenu d'un CV est un seul document `versions/<id>`, décrit dans `references/schema.md`.

1. Lister la collection `versions` avec `ArtifactData` (le charger via ToolSearch s'il est différé) pour choisir l'identifiant : `v<YYYYMMDD>-<n>`, la date du jour et `n` = 1 + le plus grand numéro déjà pris ce jour-là. `name` = drapeau de la langue + espace + identifiant (`🇬🇧 v20261025-1`).
2. Construire le document complet en un fichier JSON dans le scratchpad : `name`, `lang: "en"`, `kind: "import"`, `parent: null`, `createdAt`, `labels: {}`, `titles: {}`, `profile` (avec `photoAssetId` : l'`id` de l'asset, ou `null` sans photo), et les collections `experiences`, `projects`, `education`, `certifications`, `skills`, `languages`, `hobbies` sous forme d'objets indexés par identifiant (`exp-01`, `skill-01-<slug>`, `lang-01-<slug>`...).
3. Écrire ce fichier avec `ArtifactData` `set` (`collection: "versions"`, `doc_id`, `file_path`).
4. Écrire `meta/import` (`set` : il remplace le précédent, ce qui remet `dismissed` à zéro) avec `sourceType`, `sourceRef`, `photoSource`, `importedAt`, `counts` et `warnings`.
5. Rendre la nouvelle version affichée : lire `settings/layout`. S'il existe, `update` avec `if_version` et `{"active": "<id>"}` seulement. Sinon, `set` avec `{"active": "<id>"}`. Ne jamais toucher aux autres champs : ils appartiennent à la page.

Ne jamais modifier ni supprimer une version existante : un import crée toujours une nouvelle version. Les modifications faites à la main dans l'artefact restent dans leur version.

### 6. Vérification et fin

1. Relire le document `versions/<id>` et comparer le nombre d'éléments de chaque collection à `counts`. Corriger tout écart.
2. Enregistrer `{ "artifactUrl": "<url>" }` dans `~/.thejobfather/config.json` (créer le dossier si besoin).
3. Répondre à l'utilisateur : le lien de l'artefact, le nom de la version créée, le nombre d'éléments importés par catégorie, et la liste des avertissements à vérifier. Une courte phrase, sans récapituler la fiche. Rappeler que le CV est en anglais et que `/thejobfather:thejobfather translate` crée une version dans une autre langue.

## `translate`

Objectif : traduire une version du CV dans la langue choisie, en **créant une nouvelle version**. Rien n'est remplacé : la version d'origine et toutes les autres restent intactes, et l'utilisateur les retrouve dans le menu « Version » de l'artefact (lire, supprimer, copier).

1. Lire `~/.thejobfather/config.json`. Sans `artifactUrl`, dire de lancer `init` d'abord et s'arrêter.
2. Langue : le reste de `$ARGUMENTS`, sinon AskUserQuestion « Dans quelle langue traduire le CV ? » (français, espagnol, allemand, et « Other » pour toute autre). En déduire un code court (`fr`, `es`, `de`, `pt`, `it`, `nl`...).
3. Lire avec `ArtifactData` (le charger via ToolSearch s'il est différé) `settings/layout` et la collection `versions`. La version source est celle indiquée par `settings/layout.active`, à défaut la plus récente. Si sa langue est déjà la langue demandée, le dire et s'arrêter. Si une autre version existe déjà dans la langue demandée, le signaler et demander avec AskUserQuestion s'il faut quand même en créer une nouvelle.
4. Préparer le nouveau document dans un fichier JSON du scratchpad, à partir d'une copie de la version source :
   - `name` = drapeau + espace + identifiant, `lang` = le code choisi, `kind: "translation"`, `parent` = l'identifiant de la source, `createdAt` = maintenant. Identifiant : `v<YYYYMMDD>-<n>`, voir `references/schema.md`.
   - `labels` = tous les libellés de la table de `references/schema.md` traduits (y compris `today`, les mois au pluriel et au singulier), `titles` = les titres personnalisés traduits s'il y en a, sinon `{}`.
   - **à traduire** : `profile.headline`, `profile.summary`, `experiences` (`title`, `companyDescription`, `employmentType`, `description`, `groups[].label`, `groups[].items`, `highlights`), `projects` (`role`, `description`, `highlights`), `education` (`degree`, `field`, `description`), `skills` (`name`, `category`, `level`), `languages` (`name`, `level`), `hobbies` (`name`, `description`).
   - **à laisser tel quel** : `fullName`, `age`, lieux, entreprises, écoles, organismes, noms de projets, technologies, intitulés de certifications, liens, e-mail, téléphone, dates, `photoAssetId`, identifiants des éléments. Les intitulés de poste usuels en anglais (Scrum Master, Head of Agile, Senior Engineering Manager...) restent en anglais quand les professionnels de la langue cible les gardent tels quels.
   - Traduction fidèle : pas d'ajout, pas de suppression, pas de reformulation flatteuse. Pas de retour à la ligne dur dans une valeur. Si la langue accorde les mots selon le genre, ne pas deviner celui de l'utilisateur : employer des formulations neutres.
5. Écrire le fichier avec `ArtifactData` `set` sur `versions/<id>`. Puis rendre la nouvelle version affichée : `update` de `settings/layout` avec `if_version` et `{"active": "<id>"}` seulement.
6. Relire la nouvelle version et vérifier que le nombre d'éléments de chaque collection est le même que dans la source.
7. Répondre : le lien de l'artefact, le nom de la nouvelle version et la version dont elle est issue, et ce qui a été volontairement laissé tel quel (noms propres, certifications, intitulés de poste). Une courte phrase.
