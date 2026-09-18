# Synchronisation des parties

L’application utilise Supabase comme stockage partagé. Les secrets restent côté serveur Vercel.

1. Créer un projet sur Supabase.
2. Ouvrir **SQL Editor**, coller le contenu de `supabase.sql`, puis exécuter la requête.
3. Dans Vercel, ouvrir **Settings > Environment Variables** et ajouter `SUPABASE_URL` et `SUPABASE_SERVICE_ROLE_KEY`.
4. Facultatif : ajouter `LOCK_1_CODES`, sous forme de liste séparée par des virgules. Le cadenas 2 utilise le scan du dragon violet.
5. Redéployer le projet Vercel.

Ne jamais utiliser la clé service role dans une variable préfixée par `NEXT_PUBLIC_`.

Le navigateur actualise l’état toutes les deux secondes. L’appareil qui crée la partie conserve localement le jeton MJ ; les appareils qui rejoignent la partie ne le reçoivent jamais.

## Kill switch MJ

Pour une base existante, réexécuter `supabase.sql` dans SQL Editor pour ajouter `accept_any_code` sans supprimer les parties. Seul le MJ peut activer ou désactiver le kill switch. L’activer ne change pas l’étape. Lorsqu’il est actif, toute combinaison de quatre chiffres saisie par les joueurs est valide et fait passer à l’étape suivante, comme une bonne combinaison. Réinitialiser la partie désactive le kill switch.

## Épreuve du dragon — cadenas 2

Après le cadenas 1, les joueurs peuvent photographier le dessin assemblé ou choisir une photo, puis appuyer sur « Vérifier le dragon ». Le serveur compare uniquement les traits violets à `scan-reference/dragon.png` : points caractéristiques ORB, alignement par homographie et contrôle de couverture dans les différentes régions du dragon. Les fonds et textes des cartes sont ignorés ; les traits partiellement masqués par les chevauchements sont tolérés. Les positions et orientations des cartes doivent former le dessin.

Une reconnaissance valide passe à l’étape 3, joue l’animation sur l’appareil du joueur et débloque l’engramme 2 sur tous les appareils. Une photo refusée laisse le cadenas verrouillé. Les essais restent illimités. L’ancien code numérique du cadenas 2 est désactivé ; si le kill switch est actif, le scan est accepté sans comparaison et une saisie numérique de secours apparaît.

La photo est redimensionnée sur l’appareil avant envoi et n’est pas enregistrée. Aucune API d’IA ni clé supplémentaire n’est nécessaire. La référence est privée côté serveur et incluse dans le déploiement. Les tests couvrent compression, rotation, luminosité, perspective, occlusion simulée, dessin incomplet et morceaux déplacés. Tester des photos des cartes imprimées avant la partie pour vérifier les conditions réelles d’éclairage et d’empilement.
## Conclusion de l’enquête

Une fois les deux cadenas ouverts, l’onglet Suspects présente les six personnes du dossier. Le joueur sélectionne un suspect puis confirme avec le bouton distinct « Désigner … coupable ». La réponse est vérifiée sur le serveur d’après le dossier : Salomé Kern est la coupable. Le kill switch des cadenas ne modifie pas ce verdict.

Les deux conclusions affichent l’anneau et proposent le rapport de résolution, consultable dans l’application. La conclusion incorrecte précise la restitution à 21 h 16 et l’intervention d’une équipe indépendante du futur. Le rapport privé `resolution-documents/rapport-enquete.pdf` est inaccessible avant l’ouverture des deux cadenas et reste séparé des engrammes. Chaque appareil formule sa propre accusation ; la conclusion est conservée pendant la navigation entre onglets et réinitialisée en quittant ou en réinitialisant la partie.
