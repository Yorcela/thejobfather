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

1. Choix de la source : CV au format PDF ou site web (LinkedIn par exemple).
2. Extraction des données (identité, expériences, formations, compétences, langues, certifications, projets).
3. Création de l'artefact « The Job Father » avec sa base de données, accessible à vous seul.
4. Écriture des données en base et affichage de la fiche de profil.

LinkedIn et les sites similaires ne proposent pas d'API publique. Pour un import depuis un site web, le plugin vous demande de passer par [Claude in Chrome](https://claude.com/chrome) : votre session y est déjà ouverte, ce qui facilite la récupération. Si l'extension n'est pas disponible, vous pouvez exporter votre profil en PDF et l'importer comme un CV.

Le lien de l'artefact est conservé dans `~/.thejobfather/config.json` pour les commandes suivantes.

## Structure

```
.claude-plugin/plugin.json          manifeste du plugin
.claude-plugin/marketplace.json     permet l'installation depuis ce dépôt
skills/thejobfather/SKILL.md        commande /thejobfather et sous-commande init
skills/thejobfather/references/     schéma de la base de données
skills/thejobfather/assets/         page de l'artefact
```
