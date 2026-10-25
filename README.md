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

Une barre de navigation reste affichée en haut de l'artefact, alignée à gauche, avec trois liens : « Resume », « My offers » et « Preferences » (le lien actif est souligné), et rien d'autre. Le menu des versions et « Export PDF » ne s'affichent que sur la page du CV, au-dessus de la fiche. Le mode d'édition est toujours actif sur cette page, et le panneau « Customize » est collé à droite de la feuille A4 (210 mm). Toutes les pages ont la même largeur, celle de la feuille et du panneau ensemble, qui se réduit quand l'écran est plus étroit : le panneau passe alors sous la feuille.

Sur la page du CV, le mode édition est actif en permanence :

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

### `/thejobfather:thejobfather adapt <url>`

Adapte le CV à une offre d'emploi. La commande lit l'annonce, repère ce que le CV ne montre pas ou dit trop vaguement (une expérience sans chiffre, un outil sans contexte, un terme de l'annonce qui a un vrai équivalent dans votre CV), puis vous pose des questions ciblées (8 au plus, jamais sur un sujet déjà couvert par vos réponses mémorisées). Elle réutilise le matching déjà enregistré pour cette annonce s'il existe.

Elle montre ensuite ce qui va changer (langue, titre et résumé, puces déplacées ou reformulées, faits ajoutés d'après vos réponses, exigences qui restent non couvertes) et crée, après votre accord, une **nouvelle version** du CV, sans toucher à la version d'origine. Le CV est rédigé par défaut dans la langue de l'annonce (traduit si besoin, comme `translate`). Règle de fond : on réordonne, reformule et met en avant ce que le CV montre déjà, et on n'ajoute un fait que si vous l'avez confirmé. Rien n'est inventé ni supprimé. Si l'offre est suivie dans « My offers », la version adaptée y est associée, et le score ATS ciblé avant et après est donné.

### Sans adresse d'offre

Quand `match`, `adapt` ou `apply` est lancée sans URL, la commande demande de quelle offre il s'agit parmi celles déjà enregistrées (les plus récentes d'abord, une adresse ou un nom d'entreprise se saisissent via « Autre »). Pour `match`, les analyses demandées depuis le tableau passent en premier. Pour `apply`, seules les offres auxquelles vous n'avez pas encore postulé sont proposées.

Quand un matching donne moins de 70 sur 100, `match` demande si vous gardez l'annonce ou si elle passe directement en « Declined by me » dans le tableau des candidatures.

### Mes offres et suivi des candidatures

Le bouton « My offers » de l'artefact affiche deux onglets :

- **Matchings** : chaque `match` est enregistré avec son score et **toute l'analyse** (chaque exigence et chaque préférence avec sa preuve, points d'attention, ce qu'il faut mettre en avant, questions au recruteur). Il y a un matching par version du CV et par annonce, identifiée par son adresse (les paramètres de suivi comme `utm_*` et la barre finale sont ignorés). Si vous relancez `match` sur une annonce déjà comparée, la commande propose de revoir le matching précédent, ou d'en refaire un (par exemple avec une version plus récente du CV).
- **Applications** : un tableau des candidatures (statuts : pas postulé, postulé, réponse reçue, sans réponse, offre reçue, refusé par l'entreprise, refusé par moi), trié par date de candidature, de la plus récente à la plus ancienne. Les statuts terminés (offre reçue, refusé par l'entreprise, refusé par moi) sont masqués par défaut : le bouton « Show finished » les affiche. Le statut se change directement dans la ligne. Une ligne en bas du tableau demande seulement l'adresse d'une annonce : Entrée ou le bouton à icône d'avion ajoute l'offre (marquée « Analysis pending »), copie la commande à lancer et, dans Claude Code, `/thejobfather:thejobfather match` sans argument reprend les analyses demandées (la page ne peut pas lancer l'analyse elle-même). Chaque candidature s'ouvre sur une fiche à sommaire latéral (aperçu, score de matching, exigences, préférences, questions, formulaire, notes, historique), dont les champs se modifient directement en place ; sans matching, un bouton « Run the matching » marque l'offre pour analyse et copie la commande à lancer dans Claude Code. La fiche contient : statut et date, **version du CV envoyée** (avec un lien pour l'ouvrir), analyse de matching, **formulaire de candidature** (questions et réponses données, pour dire la même chose lors d'un call), lettre de motivation, notes et historique.

Le tableau des applications liste l'entreprise (avec son logo), l'intitulé, le statut, le meilleur score de matching, le CV envoyé, la date de candidature et la date d'ajout. Elle n'affiche par défaut que les offres ajoutées il y a un mois ou moins : le filtre de la colonne « Added », pré-rempli, permet de remonter plus loin. Le statut se filtre, Company, Status, Score, Applied et Added se trient, et toute la ligne d'une candidature est cliquable pour ouvrir sa fiche. 20 offres par page.

### `/thejobfather:thejobfather apply <url>`

Remplit le formulaire de candidature d'une offre, dans votre navigateur (Claude in Chrome), avec le bon CV. Les questions simples dont elle connaît la réponse (identité, ville, langues, diplômes...) sont remplies directement et récapitulées à la fin. Pour les questions plus profondes (motivation, projet à décrire, salaire, préavis, consentement...), vous validez chaque réponse avant que la commande passe à la suivante : elle propose une réponse tirée de ce qu'elle sait de vous (réponses mémorisées, candidatures précédentes, CV, préférences, matching) et, quand elle ne sait pas, elle pose la question telle quelle, sans rien inventer.

Règles de fond : **elle ne soumet jamais le formulaire**, c'est vous qui cliquez. Elle ne crée pas de compte, ne tape aucun mot de passe ni code et ne résout pas de captcha. Elle demande avant de cocher un consentement, et ne propose jamais de réponse aux données sensibles (identité, santé, diversité...). Le CV envoyé est la version associée à l'offre (par `adapt`) ou celle que vous choisissez : vous exportez son PDF depuis l'artefact et la commande le téléverse. Les textes libres (lettre, « pourquoi nous ») sont écrits comme vous parleriez : phrases courtes, mots simples, sans tirets longs ni formules d'IA, avec de temps en temps une toute petite faute de frappe dans un long texte, que vous pouvez faire nettoyer.

La commande garde l'onglet ouvert et enregistre en continu ce que contient le formulaire : si vous modifiez des réponses avant de soumettre, c'est la version finale qui est sauvegardée. Quand vous validez le formulaire, elle demande si vous l'avez soumis, puis enregistre dans « My offers », sur la candidature : toutes les questions et réponses (« Application form »), la lettre, la version du CV, un événement dans l'historique et, si vous avez soumis, le statut « Applied ». Les réponses qui valent au-delà de ce formulaire rejoignent vos réponses mémorisées.

### `/thejobfather:thejobfather mail_synch`

Garde le tableau des candidatures en phase avec votre boîte mail (connecteur Gmail, en lecture seule, avec votre accord). Elle cherche sur les 30 derniers jours les confirmations de candidature déjà envoyées (Greenhouse, Lever, Ashby, Welcome to the Jungle, LinkedIn...), vous montre celles qui manquent dans le tableau et ajoute celles que vous cochez, avec le statut « Applied » et la date de la confirmation. Ensuite elle va chercher les réponses (comme `track`) et propose les changements de statut. Pour chaque confirmation ou réponse, l'expéditeur, l'objet, la date, un court extrait, le texte du mail tel que reçu (retours à la ligne gardés, 20 000 caractères au plus) et son lien Gmail sont gardés : l'historique de la candidature affiche le mail en entier, avec ses liens cliquables, et un bouton l'ouvre dans Gmail. Les pièces jointes et les newsletters ne sont jamais gardées.

**Routine automatique.** `/thejobfather:thejobfather mail_synch schedule` demande votre accord une fois, puis crée une tâche planifiée qui lance `mail_synch auto` tous les jours à 9h et à 14h. Elle cherche les nouvelles réponses toute seule, sans poser de question, et ne change jamais un statut : elle marque l'offre « New reply » (avec le statut suggéré), ce qui affiche un compteur sur « My offers » et une étiquette dans le tableau, et envoie une notification s'il y a au moins une réponse. Sur la fiche, un bandeau permet d'appliquer le statut suggéré ou de marquer la réponse comme vue. La tâche tourne tant que l'application Claude est ouverte (sinon au prochain lancement) ; un test avec « Run now » dans les tâches planifiées permet de valider les accès Gmail. `mail_synch unschedule` l'arrête.

### `/thejobfather:thejobfather track`

Suivi des réponses : la commande cherche dans votre Gmail (connecteur Gmail de Claude, en lecture seule, avec votre accord avant toute lecture) les messages reçus après chaque candidature, les classe (réponse, refus, simple accusé de réception), et vous propose de mettre à jour le statut. Rien n'est modifié sans votre validation, seules les métadonnées utiles (date, expéditeur, objet, un court extrait) sont gardées, et elle propose « sans réponse » après environ 21 jours de silence.

### Préférences d'emploi

Le lien « Preferences » de l'artefact affiche, à la place du CV, une page pour saisir ce que vous cherchez : un sommaire à gauche (rôles et salaire, lieux, secteurs et entreprises, préférences, réponses mémorisées) et une carte par thème, avec des pastilles à cocher pour les contrats et les modes de travail, et un bouton « Save changes ». Tout est facultatif, et les préférences sont communes à toutes les versions du CV :

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

Le menu n'affiche que les 5 dernières versions. Son bouton « View more » ouvre la page « CV versions » : un tableau paginé (20 versions par page) de toutes les versions, avec les colonnes Version, Language, Type, Employer, Date et Actions. Les colonnes Language, Type, Employer et Date se filtrent par l'icône d'entonnoir de leur en-tête (la date par une période), Version et Date se trient, et « Reset filters » efface les filtres. Un clic sur le nom d'une version la lit, et chacune peut être supprimée.

Les modifications faites dans la page (édition sur place) s'appliquent à la version affichée. L'ordre des rubriques, les couleurs et la police sont communs à toutes les versions.

## Structure

```
.claude-plugin/plugin.json          manifeste du plugin
.claude-plugin/marketplace.json     permet l'installation depuis ce dépôt
skills/thejobfather/SKILL.md        commande /thejobfather et sous-commandes init, translate, ats_score, match, adapt, apply, mail_synch, track
skills/thejobfather/references/     schéma de la base de données, barèmes des scores ATS et de matching
skills/thejobfather/scripts/        calcul des scores ATS et de matching, identifiants des offres
skills/thejobfather/assets/         page de l'artefact
```
