# La Bague hors du Temps — prototype V2

Jeu de 45 à 60 minutes pour deux équipes. Les illustrations sont volontairement laissées de côté ; ce dossier contient les règles, statistiques, solutions et textes à mettre en page.

## Vérité de l’affaire — MJ uniquement

**Victor Delmas**, cousin du marié et illusionniste amateur, a prémédité le vol pour empêcher le mariage. Une clause familiale lui retire son atelier dès la célébration et rend ses dettes exigibles. Il a extrait l’alliance de l’écrin avec une aiguille aimantée reliée à un fil de scène, puis l’a enfermée dans sa boîte truquée.

La bague est un ancrage temporel : son vol pendant la répétition du serment efface le mariage. Les maladresses d’Élias et le mensonge de Salomé sont des fausses pistes, pas les causes du phénomène.

## Déroulé

| Temps | Épreuve | Gain |
|---:|---|---|
| 0–5 | Prologue | Dossier initial |
| 5–15 | E1 : combo de dégâts | Code 748 + P1/P2 |
| 15–25 | E2 : combo de pioche | Cartes brouillées + P3/P4 |
| 25–35 | E3 : superposition | AIGUILLE + P5 |
| 35–45 | E4 : visions | A-L-I-E + P6 |
| 45–55 | E5 : charade | ALLIANCE puis 2543 |
| 55–60 | Accusation | Voleur, mobile, méthode |

# Énigme 1 — Le Gardien du point fixe

## But

Le Gardien commence à **21 stabilité**. Il faut atteindre exactement 0, posséder exactement trois Échos, puis jouer la Lame. Passer sous 0 remet le Gardien à 21 et retire les Échos. Une carte ne se joue qu’une fois ; on finit de résoudre tous ses déclenchements avant la suivante.

## Statistiques des cartes

| ID | Nom | Type | Effet | Sceau |
|---|---|---|---|---:|
| E1-01 | Cloche des promesses | Relique | Reste en jeu. Lorsqu’une carte redéclenche un effet déjà résolu, inflige 1 après ce redéclenchement. Une sonnerie maximum par carte jouée. | 2 |
| E1-02 | Étincelle du présent | Sort | Inflige 2. | 5 |
| E1-03 | Ruban sans fin | Sort—Écho | Redéclenche l’effet imprimé du dernier Sort joué, puis gagnez 1 Écho. | 7 |
| E1-04 | Sablier miroir | Relique—Écho | Le prochain Sort de dégâts se redéclenche avec +2 à ses dégâts imprimés. Après résolution, gagnez 1 Écho. | 4 |
| E1-05 | Anneau foudroyant | Sort | Inflige 4. | 1 |
| E1-06 | Onde rémanente | Sort—Écho | Redéclenche les dégâts imprimés du dernier Sort de dégâts, sans ses bonus, puis gagnez 1 Écho. | 8 |
| E1-07 | Lame du serment | Rituel | Jouable à 0 avec exactement 3 Échos. Le code est formé par les sceaux des cartes ayant créé les Échos. | 3 |
| E1-L1 | Bouquet spectral | Leurre | Rendez 3 stabilité, puis infligez 5. | 6 |
| E1-L2 | Voile protecteur | Leurre | Annulez la prochaine occurrence de dégâts. | 9 |
| E1-L3 | Montre brisée | Leurre | Redéclenchez la dernière Relique résolue. | 0 |

## Combo détaillé

1. **Cloche** : elle surveille les répétitions. Total 0.
2. **Étincelle** : 2 dégâts. Stabilité 19.
3. **Ruban** : répète l’Étincelle pour 2 ; la Cloche ajoute 1. Stabilité 16, Échos 1.
4. **Sablier** : prépare le prochain Sort de dégâts.
5. **Anneau** : 4, puis répétition à 4 + 2, puis Cloche à 1. L’étape inflige 11. Stabilité 5, Échos 2.
6. **Onde** : reprend la valeur imprimée de l’Anneau, donc 4 et non 6 ; la Cloche ajoute 1. Stabilité 0, Échos 3.
7. **Lame** : victoire. Les créateurs d’Écho sont Ruban 7, Sablier 4, Onde 8 : **code 748**.

Calcul : `2 + (2+1) + (4+6+1) + (4+1) = 21`.

Indices : « installez d’abord ce qui réagit aux répétitions » ; puis « le petit Sort va avec le Ruban, le grand avec le Sablier » ; enfin donner l’ordre des titres.

# Énigme 2 — Reconstituer l’équipement

## But et préparation

Finir avec exactement six équipements stables en main et aucun instable. Les six Actions doivent être utilisées une fois.

Pioche, de haut en bas : **Voile instable, Bague factice, Aiguille d’argent, Clef de la loge, Gants blancs, Loupe, Ruban bordeaux, Montre arrêtée**.

## Cartes Action

| ID | Nom | Type | Effet |
|---|---|---|---|
| E2-A1 | Intendant prévoyant | Relique | Quand un effet fait piocher exactement 2, piochez-en une troisième, puis placez l’une des trois sous la pioche. |
| E2-A2 | Serment du tri | Relique | La première fois qu’une carte est placée sous la pioche, piochez immédiatement 1. |
| E2-A3 | Miroir de vestiaire | Relique | Le prochain effet « piochez 1 » est résolu deux fois. |
| E2-A4 | Fouille des poches | Action | Piochez 1. |
| E2-A5 | Souvenir récupéré | Action | Défaussez un équipement ; prenez la carte sous la pioche, puis piochez 1. Si la défausse était un Vêtement, gardez les deux ; sinon défaussez la seconde. |
| E2-A6 | Sacoche renversée | Action | Piochez exactement 2. |

## Équipements

| Nom | Famille | Stable | Symbole |
|---|---|---:|---|
| Voile instable | Vêtement | Non | comète |
| Bague factice | Bijou | Oui | lune |
| Aiguille d’argent | Outil | Oui | étoile |
| Clef de la loge | Outil | Oui | clef |
| Gants blancs | Vêtement | Oui | mains |
| Loupe | Outil | Oui | œil |
| Ruban bordeaux | Accessoire | Oui | boucle |
| Montre arrêtée | Mécanisme | Non | cadran fendu |

## Combo détaillé

1. Poser **Intendant**, puis **Serment du tri**.
2. Jouer **Sacoche** : piocher Voile + Bague ; l’Intendant ajoute Aiguille. Mettre la **Bague** sous la pioche, garder Voile + Aiguille.
3. Le **Serment** se déclenche : piocher la **Clef**. Main : Voile, Aiguille, Clef.
4. Poser le **Miroir**.
5. Jouer **Fouille** : son effet se résout deux fois, piochant **Gants**, puis **Loupe**.
6. Jouer **Souvenir récupéré** : défausser le **Voile**. Prendre la **Bague** sous la pioche puis piocher le **Ruban**. Le Voile est un Vêtement, donc garder les deux.
7. Main finale : **Aiguille, Clef, Gants, Loupe, Bague, Ruban**. La Montre instable reste dans la pioche.

Séquence de validation : `étoile – clef – mains – œil – lune – boucle`.

Erreurs contrôlées : mettre le Voile sous la pioche empêche la dernière double récupération ; poser le Miroir trop tôt double la mauvaise pioche ; jouer Souvenir avant Fouille récupère les mauvaises cartes.

# Énigme 3 — Superposition réelle

Imprimer les quatre Bases du fichier `puzzle_visuel/superposition-aiguille.svg` sur papier blanc et les quatre Calques sur transparent. Découper et mélanger.

Les joueurs doivent apparier chaque Base et chaque Calque en faisant coïncider le cercle doré et le trait noir. Chaque bonne superposition complète deux lettres : **AI**, **GU**, **IL**, **LE**. Les groupes sont rangés grâce aux 1, 2, 3 et 4 étoiles des Bases. Solution visible : **AIGUILLE**.

Cette réponse révèle la méthode du vol et débloque P5. Le prototype est volontairement sans filtre coloré : l’information n’existe complètement qu’après superposition physique.

# Énigme 4 — Les visions du sorcier

Les joueurs associent quatre cartes Vision aux cartes Réalité dans l’ordre **QUI ? OÙ ? AVEC QUOI ? QUAND ?**

| Vision utile | Réalité |
|---|---|
| Rideau rouge, scène vide, masque souriant | Victor |
| Miroir à ampoules, veste suspendue, porte entrouverte | Loge |
| Boussole attirée par une épingle plutôt que le nord | Aiguille aimantée |
| Horloge dont les aiguilles sont remplacées par 27 pétales | 18 h 27 |

Fausses visions : bouquet sous la pluie/Jardin ; œil dans un objectif/Mina ou appareil ; mains poudrées/Élias ; serrure dans une larme/Clef ; 32 oiseaux/18 h 32 ; deux sœurs/Salomé ; foule sous un lustre/Salle ; ruban autour d’une rose/fausse piste.

Solution : **Victor — Loge — Aiguille — 18 h 27**. Au dos des quatre bonnes Réalités figurent les lettres **A, L, I, E**, qui donnent l’ordre de conversion final. P2, P4 et P5 confirment les associations et évitent une résolution purement subjective.

# Énigme 5 — L’Alliance

Utiliser une charade graphique plutôt qu’une charade phonétique fragile :

- une lettre **A** ;
- un **lit** dont le T est barré : LI ;
- une **anse** dont le S est barré : ANE ;
- une lettre **C** qui vient s’insérer dans ANE : ANCE ;
- un miroir entre A et LI indique que le L de LI doit être doublé.

Assemblage : `A + L + LI + ANCE` = **ALLIANCE**.

L’énigme 4 a fourni l’ordre A-L-I-E. Sur le clavier téléphonique imprimé près de la boîte : A=2, L=5, I=4, E=3. **Code final : 2543**.

# Accusation

- Voleur : Victor Delmas.
- Mobile : empêcher le mariage pour conserver son atelier et retarder ses dettes.
- Méthode : aiguille aimantée et fil de scène glissés sous l’écrin.
- Preuve : clause notariale + badge de 18 h 26 + photo corrigée à 18 h 27 + poudre de scène.

Les documents distribuables sont dans `documents_enquete/`.
