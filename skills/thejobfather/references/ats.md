# Score ATS : ce qu'on sait, ce qu'on mesure

## Ce que les sources établissent

- **Il n'existe pas de score ATS universel.** Aucun éditeur d'ATS ne publie de barème commun. Les « scores sur 100 » des outils (Jobscan, ATS Resume AI et autres) sont des estimations propres à chaque outil, utiles comme indication, pas comme prédiction du résultat chez un employeur. Les poids et seuils publiés par ces outils sont des choix de l'éditeur.
- **Le parsing passe avant tout.** L'ATS extrait du fichier des champs (nom, e-mail, téléphone, dernier poste et employeur, années d'expérience, formation, compétences). Un champ mal lu reste vide, et un recruteur qui filtre dessus ne verra pas le candidat. Mises en page à colonnes, tableaux, zones de texte, en-têtes et pieds de page, images de texte et titres de rubrique originaux sont les causes les plus citées d'échec.
- **Les recruteurs cherchent par mots-clés** (compétences, intitulés), souvent de façon littérale d'après les guides tiers : « GA4 » et « Google Analytics » peuvent être deux termes différents, un acronyme non développé peut passer à côté. Les termes placés dans l'expérience et le titre pèsent plus qu'une simple liste de compétences. Le bourrage de mots-clés est repéré par les recruteurs comme par les outils.
- **Un score ne rejette pas automatiquement.** Greenhouse indique que son Talent Matching ne rejette et ne fait avancer aucun candidat, qu'il classe selon des critères que l'équipe calibre (compétences requises, expérience, intitulés) et rapproche des termes voisins d'une même compétence. Les rejets automatiques viennent de règles réglées par le recruteur, comme une réponse « non » à une question d'autorisation de travail. L'idée d'un seuil secret (« 75 % rejetés ») est contestée : le plus souvent le CV est stocké mais n'apparaît pas aux recherches du recruteur.
- **Jobscan compare le CV à une offre.** Le « match rate » (0 à 100 %) compare compétences techniques, niveau d'études (si l'offre en exige un), intitulé de poste, compétences comportementales et autres mots-clés, dans cet ordre de priorité. Le nombre de mots et les résultats chiffrés ne comptent pas dans ce taux. L'objectif conseillé est d'au moins 75 %, sans chercher 100 % (texte artificiel).
- **Format de fichier : pas de consensus.** Certains guides préfèrent le DOCX, d'autres un PDF texte. Le point commun : le texte doit être sélectionnable (pas une image), la mise en page sur une colonne, et le mieux est de suivre la consigne de l'offre.
- **Autres usages validés par plusieurs guides** : dates dans un format unique et en ordre antichronologique, coordonnées dans le corps du document, intitulés de rubrique standard, rubrique Expérience en premier après le profil.

Limites de ces sources : la plupart sont des blogs d'éditeurs d'outils de CV, pas des documentations d'ATS. Le barème ci-dessous est donc **notre** barème, construit sur ce consensus. Il mesure la lisibilité et la qualité du CV, et la couverture des mots-clés d'une offre. Il ne prédit pas le résultat chez un employeur donné.

## Barème (100 points)

Sans offre, le score est **générique** : lisibilité (30) et contenu (30), ramenés sur 100. Avec une offre, il est **ciblé** : lisibilité (30), contenu (30) et mots-clés (40), ce qui reflète le poids des mots-clés dans les recherches et dans le match rate. Quand le PDF n'est pas fourni, ses 3 points sont retirés du total, pas comptés comme perdus.

### Lisibilité par un parseur (30)

| Contrôle | Pts | Règle |
|---|---|---|
| Coordonnées | 6 | nom (2), e-mail valide (2), téléphone d'au moins 8 chiffres (1), lieu (1) |
| Titres de rubrique standard | 4 | chaque titre affiché est dans la liste des intitulés reconnus (Profile, Experience, Education, Skills... et équivalents français) ; un titre inconnu vaut la moitié |
| Expériences complètes | 6 | intitulé, entreprise, début, fin ou « en cours » pour chaque poste |
| Dates | 5 | format lisible, pas de date sans mois (−1 par poste, max −3), pas de fin avant le début (−3) ; un trou de plus de 6 mois est signalé, sans pénalité |
| Texte propre | 3 | pas de retour à la ligne dur dans une puce, pas de caractère exotique ou d'emoji |
| Ordre des rubriques | 3 | ordre attendu : Profil, Expérience, Projets, Éducation, Compétences, Hobbies ; retire des points au prorata des inversions |
| Extraction du PDF (optionnel) | 3 | coordonnées en haut du texte extrait (1), rubriques retrouvées dans l'ordre (1), pas de caractères corrompus ni de puce isolée (1). Un PDF sans texte extractible est signalé comme grave |

### Qualité du contenu (30)

| Contrôle | Pts | Règle |
|---|---|---|
| Résumé | 4 | de 30 à 150 mots (moitié des points de 15 à 29 ou de 151 à 220) |
| Puces par poste | 6 | de 3 à 12 puces pour chaque poste (un ancien poste de plus de 10 ans peut en avoir moins) ; au-delà de 12, demi-points |
| Puces lisibles | 4 | part des puces de 8 à 40 mots ; les puces de plus de 45 mots sont citées |
| Résultats chiffrés | 8 | part des puces contenant un chiffre, points pleins à partir de 40 % |
| Compétences | 4 | au moins 8 compétences listées |
| Formation | 2 | une formation (2) ou seulement des certifications (1) |
| Longueur | 2 | de 350 à 1 000 mots au total (1 point de 250 à 349 ou de 1 001 à 1 400) |

### Mots-clés de l'offre (40, avec offre uniquement)

Les termes sont extraits de l'offre (voir `SKILL.md`), puis cherchés dans le CV sans tenir compte de la casse ni des accents, avec le pluriel simple et les variantes déclarées.

- **Poids par type**, d'après l'ordre de priorité de Jobscan : compétences techniques 3, intitulé de poste 3, niveau d'études 2, compétences comportementales 1, autres 1. Un terme « requis » compte une fois et demie.
- **Où il est trouvé** : dans l'intitulé, le résumé ou l'expérience, il compte 1 ; seulement dans la liste de compétences ou ailleurs, 0,7.
- **Couverture** = somme pondérée des termes trouvés sur la somme des poids. Points = 40 × couverture. Objectif conseillé : 75 % ou plus.
- **Bourrage** : un terme cité plus de 15 fois est signalé.

### Lecture du score

85 et plus : excellent. 70 à 84 : bon. 55 à 69 : à travailler. Moins de 55 : faible. Un score générique de 90 ne dit rien sur une offre précise : c'est le score ciblé qui compte pour postuler.

## Sources

- Greenhouse, [Talent Matching FAQ](https://support.greenhouse.io/hc/en-us/articles/41131886674075-Talent-Matching-FAQ) : pas de rejet ni d'avancement automatique, catégories de correspondance, termes voisins rattachés à une même compétence.
- Greenhouse, [Search resumes for keywords](https://support.greenhouse.io/hc/en-us/articles/115004600186-Search-resumes-for-keywords) : recherche en texte intégral dans les candidatures (la page ne détaille pas le mode de correspondance).
- Jobscan, [Jobscan Tutorial](https://www.jobscan.co/jobscan-tutorial) : ce que compare le match rate, ordre de priorité des mots-clés, objectif de 75 %, nombre de mots et résultats chiffrés exclus du taux.
- ATS Verification, [How ATS scoring works](https://atsverification.com/blog/how-ats-scoring-works/) : champs extraits, filtrage des recruteurs par champs et mots-clés, formats qui cassent le parsing, absence de score universel (article d'un éditeur d'outil).
- ATS Resume AI, [Resume ATS scoring criteria](https://www.atsresumeai.com/blog/resume-ats-score) : exemple de grille pondérée (barème propre à l'éditeur, qui reconnaît lui-même l'absence de standard).
- Guides de mise en forme : [University at Buffalo](https://management.buffalo.edu/career-resource-center/students/preparation/tools/correspondence/resume/electronic.html), [Adobe Express](https://www.adobe.com/express/discover/tips/ats-resume-tips), [Scale.jobs](https://scale.jobs/blog/ats-resume-format-works-2026) : une colonne, pas de tableaux ni de zones de texte, titres standard, dates cohérentes, coordonnées dans le corps du document.
