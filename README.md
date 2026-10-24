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

Traduit la fiche dans la langue de votre choix et enregistre le résultat comme **nouvelle version** : contenu, titres de rubriques, mois et mots comme « today ». Les noms propres, entreprises, écoles et certifications restent tels quels, et les intitulés de poste usuels en anglais aussi. Rien n'est remplacé.

### Versions

Chaque CV est une version, nommée avec le drapeau de sa langue : « 🇫🇷 v20261025-1 » (date du jour et numéro). `init` (ajout d'une version) et `translate` créent une nouvelle version et gardent toutes les autres. Dès qu'il y a une version, un menu déroulant à côté de « Customize » permet de :

- lire une version : cliquez dessus, la fiche et l'export PDF suivent ;
- la supprimer (en deux clics, sauf la dernière) ;
- enregistrer une copie de la version affichée.

Les modifications faites dans la page (bouton « Edit ») s'appliquent à la version affichée. L'ordre des rubriques, les couleurs et la police sont communs à toutes les versions.

## Structure

```
.claude-plugin/plugin.json          manifeste du plugin
.claude-plugin/marketplace.json     permet l'installation depuis ce dépôt
skills/thejobfather/SKILL.md        commande /thejobfather et sous-commande init
skills/thejobfather/references/     schéma de la base de données
skills/thejobfather/assets/         page de l'artefact
```
