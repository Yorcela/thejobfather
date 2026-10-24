---
name: thejobfather
description: Assistant de recherche d'emploi. Sous-commande disponible : `init`, qui importe le profil de l'utilisateur (CV PDF ou site web comme LinkedIn, via Claude in Chrome) dans la base de données d'un artefact. À utiliser quand l'utilisateur tape /thejobfather ou parle d'initialiser son profil de recherche d'emploi.
argument-hint: init
---

# The Job Father

Point d'entrée du plugin. Le premier argument est la sous-commande : `$ARGUMENTS`

- `init` : voir ci-dessous.
- vide ou inconnue : dire en une phrase que seule `init` existe pour l'instant et proposer de la lancer.

Répondre en français.

## `init`

Objectif : lire toutes les données de profil de l'utilisateur dans la source qu'il choisit, et les stocker dans la base de données d'un artefact, qui sert ensuite de référence pour tout le reste de la recherche d'emploi.

Le schéma exact des documents est dans [references/schema.md](references/schema.md). Le lire avant l'étape 3.

### 1. Reprise éventuelle

Lire `~/.thejobfather/config.json` s'il existe (clé `artifactUrl`). S'il existe, demander avec AskUserQuestion : « Mettre à jour le profil existant » (réimporter dans le même artefact) ou « Repartir de zéro » (nouvel artefact). Ne jamais supprimer l'ancien artefact sans demande explicite.

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
- Ce qui est ambigu ou illisible va dans `meta/import.warnings`, pas dans une valeur devinée.
- Garder les textes dans leur langue d'origine.
- Si le nom complet n'est pas trouvé, arrêter et le dire : la source n'est probablement pas un profil.

### 4. Création de l'artefact

Charger les skills `artifact-capabilities` puis `artifact-design` si ce n'est pas déjà fait.

Publier avec l'outil Artifact le fichier `skills/thejobfather/assets/profile.html` de ce plugin (chemin sous `${CLAUDE_PLUGIN_ROOT}`), sans le modifier :

- `capabilities`: `{"db": {"rules": [{"path": "", "read": "owner", "write": "owner"}]}}`. Les données sont personnelles, seul le propriétaire lit et écrit.
- `icon`: `"profile"`.
- `description`: « Profil professionnel et base de données de la recherche d'emploi. »
- En cas de mise à jour (étape 1), passer l'`url` existante.

La page s'abonne à la base et affiche un état vide tant qu'elle ne contient rien.

### 5. Remplissage de la base

Écrire les documents avec l'outil `ArtifactData` (le charger via ToolSearch s'il est différé), en une seule action `batch` quand c'est possible. Respecter exactement les chemins et champs de `references/schema.md` :

- `profile/me`
- `experiences/exp-NN`, `education/edu-NN`, `skills/skill-<slug>`, `languages/lang-<slug>`, `certifications/cert-NN`, `projects/proj-NN`
- `meta/import` en dernier, avec `sourceType`, `sourceRef`, `importedAt`, `counts` et `warnings`.

En cas de mise à jour, utiliser `set` sur les mêmes identifiants et supprimer les documents de l'ancien import qui n'existent plus dans la nouvelle source.

### 6. Vérification et fin

1. Faire un `list` de chaque collection écrite et comparer les nombres à `counts`. Corriger tout écart.
2. Enregistrer `{ "artifactUrl": "<url>" }` dans `~/.thejobfather/config.json` (créer le dossier si besoin).
3. Répondre à l'utilisateur : le lien de l'artefact, le nombre d'éléments importés par catégorie, et la liste des avertissements à vérifier. Une courte phrase, sans récapituler la fiche.
