# The Job Father

Plugin Claude Code pour gérer sa recherche d'emploi.

## Installation

```bash
claude plugin marketplace add Yorcela/thejobfather
claude plugin install thejobfather@thejobfather
```

Pour développer en local, depuis le dossier du dépôt :

```bash
claude --plugin-dir .
```

## Commandes

### `/thejobfather init`

Importe votre profil dans la base de données d'un artefact Claude.

1. Choix de la source : CV au format PDF ou profil LinkedIn.
2. Extraction des données (identité, expériences, formations, compétences, langues, certifications, projets).
3. Création de l'artefact « The Job Father » avec sa base de données, accessible à vous seul.
4. Écriture des données en base et affichage de la fiche de profil.

LinkedIn ne propose pas d'API publique. Le plugin lit votre profil dans votre navigateur si une session est ouverte, sinon il vous demande d'exporter votre profil en PDF depuis LinkedIn.

Le lien de l'artefact est conservé dans `~/.thejobfather/config.json` pour les commandes suivantes.

## Structure

```
.claude-plugin/plugin.json          manifeste du plugin
.claude-plugin/marketplace.json     permet l'installation depuis ce dépôt
skills/thejobfather/SKILL.md        commande /thejobfather et sous-commande init
skills/thejobfather/references/     schéma de la base de données
skills/thejobfather/assets/         page de l'artefact
```
