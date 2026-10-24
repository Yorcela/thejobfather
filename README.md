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

### `/thejobfather:thejobfather init`

Importe votre profil dans la base de données d'un artefact Claude.

1. Choix de la source : CV au format PDF ou site web (LinkedIn par exemple).
2. Extraction des données (identité, expériences, formations, compétences, langues, certifications, projets).
3. Choix de la photo de profil : reprendre celle du site (LinkedIn), celle du CV PDF s'il en contient une, en partager une autre, ou ne pas en avoir.
4. Création de l'artefact « The Job Father » avec sa base de données, accessible à vous seul.
5. Écriture des données en base et affichage de la fiche de profil.

La fiche s'affiche comme un CV, dans cet ordre par défaut : profil, compétences, expérience professionnelle, projets personnels (si vous en avez), éducation & certifications, hobbies. Les rubriques vides ne sont pas affichées.

Le bouton « Personnaliser » de l'artefact ouvre un tiroir pour :

- **Rubriques** : changer l'ordre, renommer, masquer.
- **Apparence** : palettes, couleurs (accent, nom, texte, fond de la fiche et de la page) et police.
- **Contenu** : modifier l'identité et le profil (photo comprise), modifier ou supprimer chaque élément, en ajouter de nouveaux.

Ces réglages sont enregistrés dans la base de l'artefact et survivent à une mise à jour de l'import.

Le bouton « Export PDF » télécharge la fiche en PDF (A4) avec du vrai texte, lisible par les logiciels de recrutement. Les rubriques suivent l'ordre que vous avez choisi, aucune ligne n'est coupée, un titre reste toujours avec son contenu, et une puce ou un paragraphe n'est jamais séparé entre deux pages. La police du PDF est Helvetica : les caractères hors alphabet latin (cyrillique, grec, caractères asiatiques...) ne sont pas pris en charge et sont remplacés par « ? ».

Chaque ligne de « To check after import » se masque avec « Seen ». Le bouton « Show dismissed import warnings » de l'onglet Content les ré-affiche.

Pensé pour passer les logiciels de recrutement (ATS) : le CV est en anglais par défaut, les dates ont toujours le même format (« Sept. 2024 - today », avec une balise `time` lisible par machine) et les phrases coupées par la largeur d'une page à l'import sont recollées.

### `/thejobfather:thejobfather translate [langue]`

Traduit la fiche dans la langue de votre choix : contenu, titres de rubriques, mois et mots comme « today ». Les noms propres, entreprises, écoles et certifications restent tels quels. La traduction remplace le contenu actuel de l'artefact : pour revenir à la langue d'origine, relancez `init`.

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
