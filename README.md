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

Le bouton « Customize » de l'artefact active le mode édition :

- **Édition sur place** : cliquez sur n'importe quel texte du CV (nom, coordonnées, résumé, postes, dates, puces, compétences, formations, hobbies, titres de rubrique) pour le modifier directement. Entrée ou un clic ailleurs enregistre, Échap annule. Vider une puce, une compétence, une langue ou un lien la supprime. Des liens « + bullet », « + skill », « + experience »... ajoutent des éléments, et un « × » (à confirmer par un second clic) supprime un poste, un projet, une formation ou une catégorie. La photo se change d'un clic.
- **Rubriques** : une fois en mode édition, chaque titre de rubrique a des flèches pour la déplacer et un bouton pour la masquer ou la réafficher. Cliquer sur le titre le renomme.
- **Apparence** : le panneau à droite règle les palettes, les couleurs (accent, nom, texte, fond de la fiche et de la page) et la police.

Ces réglages sont enregistrés dans la base de l'artefact et survivent à une mise à jour de l'import.

Le bouton « Export PDF » télécharge la fiche en PDF (A4) avec du vrai texte, lisible par les logiciels de recrutement. Les rubriques suivent l'ordre que vous avez choisi, aucune ligne n'est coupée, un titre reste toujours avec son contenu, et une puce ou un paragraphe n'est jamais séparé entre deux pages. Le PDF utilise les mêmes polices que la page, embarquées dans le fichier : Instrument Sans pour le texte, et Bricolage Grotesque (thème Modern) ou Source Serif 4 (thème Classic) pour le nom et les titres de poste ; le thème Neutral utilise Helvetica. Ces polices sont réduites à l'alphabet latin : les caractères hors de cet alphabet (cyrillique, grec, caractères asiatiques...) ne sont pas pris en charge et sont remplacés par « ? ». Les trois polices sont sous licence SIL Open Font License 1.1.

Chaque ligne de « To check after import » se masque avec « Seen ». Le bouton « Show dismissed import warnings » du panneau Customize les ré-affiche.

Pensé pour passer les logiciels de recrutement (ATS) : le CV est en anglais par défaut, les dates ont toujours le même format (« Sept. 2024 - today », avec une balise `time` lisible par machine) et les phrases coupées par la largeur d'une page à l'import sont recollées.

### `/thejobfather:thejobfather translate [langue]`

Traduit la fiche dans la langue de votre choix et enregistre le résultat comme **nouvelle version** : contenu, titres de rubriques, mois et mots comme « today ». Les noms propres, entreprises, écoles et certifications restent tels quels, et les intitulés de poste usuels en anglais aussi. Rien n'est remplacé.

### `/thejobfather:thejobfather ats_score [offre]`

Estime la compatibilité ATS de la version affichée du CV avec un score sur 100 et propose des améliorations concrètes. Sans offre, le score est **générique** : lisibilité par un parseur (coordonnées, titres de rubrique standard, dates, ordre des rubriques) et qualité du contenu (résumé, puces, résultats chiffrés, compétences, longueur). Avec une offre d'emploi (URL, fichier ou texte), le score est **ciblé** : il ajoute la couverture des mots-clés de l'offre, qui pèsent 40 points, et indique ceux qui manquent. Avec le chemin d'un export PDF, il vérifie aussi ce qu'un parseur extrait du fichier.

Aucun éditeur d'ATS ne publie de score universel : le barème est le nôtre, construit sur ce que disent les sources, et donne une estimation, pas une prédiction. Le détail du barème et les sources sont dans `skills/thejobfather/references/ats.md`. Le calcul est fait par un script (`skills/thejobfather/scripts/ats_score.py`), donc reproductible. Les améliorations acceptées sont enregistrées dans une nouvelle version, jamais dans celle qui a été évaluée.

### `/thejobfather:thejobfather match <url>`

Compare une annonce d'emploi avec votre CV et vos préférences, puis calcule un **score de matching** expliqué. La commande lit l'annonce (par Claude in Chrome si la page est protégée, comme LinkedIn), repère les écarts et les points d'attention, vous pose des questions sur ses doutes (une expérience absente du CV, un salaire ou un nombre de jours sur site flou, une condition éliminatoire), puis donne le score avec les éléments qui ont rapporté ou coûté le plus de points. Elle termine sur ce qu'il faut mettre en avant et la question à poser au recruteur.

Le score a deux parties : les exigences de l'annonce face à votre CV (60 points) et ses conditions face à vos préférences (40 points). Un critère éliminatoire (secteur ou entreprise blacklistés, condition éliminatoire, préférence impérative non respectée) plafonne le score à 25. Sans préférences enregistrées, seul le CV est comparé. Vos réponses aux questions sont mémorisées pour ne pas vous reposer la même question sur l'annonce suivante : un secteur, une entreprise ou un niveau de salaire refusé reste refusé 7 jours, une compétence que vous n'avez pas reste manquante 90 jours, une expérience que vous confirmez reste valable un an (et la commande vous suggère de l'ajouter au CV). Les réponses valides sont visibles, avec leur date d'expiration, et se suppriment une par une dans la page « Preferences » de l'artefact (« Answers I am remembering »). Un refus qui doit durer plus longtemps va dans la liste noire des préférences, qui n'expire pas.

Comme pour `ats_score`, le calcul est fait par un script (`skills/thejobfather/scripts/match_score.py`) à partir de l'analyse de la commande, et le barème est dans `skills/thejobfather/references/match.md`. C'est une estimation, pas une prédiction d'embauche.

### Préférences d'emploi

Le bouton « Preferences » de l'artefact affiche, à la place du CV, un formulaire pour saisir ce que vous cherchez (« Back to resume » pour revenir au CV). Tout est facultatif, et les préférences sont communes à toutes les versions du CV :

- **Rôles, contrats et rémunération :** chaque rôle visé a ses propres types de contrat acceptés (CDI, CDD, freelance, stage, alternance, plusieurs possibles) et sa rémunération souhaitée : une fourchette de salaire (minimum et maximum, par an ou par mois) pour un contrat salarié, et, si le freelance est coché, une fourchette de TJM (taux journalier).
- **Lieux et mode de travail :** pour chaque lieu (ville, région, pays ou « Remote »), les modes acceptés (remote, hybride, sur site, plusieurs possibles) et, si l'hybride est coché, le nombre maximum de jours sur site par semaine. Une case indique l'ouverture à la mobilité.
- **Secteurs et entreprises :** secteurs souhaités (liste blanche) et à éviter (liste noire), entreprises à rejoindre ou à éviter, tailles d'entreprise.
- **Autres :** langues de travail, critères indispensables, souhaitables et éliminatoires, notes.

Ces préférences servent à la commande `match`, qui compare l'annonce au rôle et au lieu les plus proches.

### Versions

Chaque CV est une version, nommée avec le drapeau de sa langue : « 🇫🇷 v20261025-1 » (date du jour et numéro). `init` (ajout d'une version) et `translate` créent une nouvelle version et gardent toutes les autres. Dès qu'il y a une version, un menu déroulant à côté de « Customize » permet de :

- lire une version : cliquez dessus, la fiche et l'export PDF suivent ;
- la supprimer (en deux clics, sauf la dernière) ;
- enregistrer une copie de la version affichée.

Les modifications faites dans la page (édition sur place) s'appliquent à la version affichée. L'ordre des rubriques, les couleurs et la police sont communs à toutes les versions.

## Structure

```
.claude-plugin/plugin.json          manifeste du plugin
.claude-plugin/marketplace.json     permet l'installation depuis ce dépôt
skills/thejobfather/SKILL.md        commande /thejobfather et sous-commandes init, translate, ats_score, match
skills/thejobfather/references/     schéma de la base de données, barèmes des scores ATS et de matching
skills/thejobfather/scripts/        calcul des scores ATS et de matching
skills/thejobfather/assets/         page de l'artefact
```
