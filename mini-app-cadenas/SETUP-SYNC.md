# Synchronisation des parties

L’application utilise Supabase comme stockage partagé. Les secrets restent côté serveur Vercel.

1. Créer un projet sur Supabase.
2. Ouvrir **SQL Editor**, coller le contenu de `supabase.sql`, puis exécuter la requête.
3. Dans Vercel, ouvrir **Settings > Environment Variables** et ajouter `SUPABASE_URL` et `SUPABASE_SERVICE_ROLE_KEY`.
4. Facultatif : ajouter `LOCK_1_CODES` et `LOCK_2_CODES`, sous forme de listes séparées par des virgules. Le cadenas 2 demande un scan du dragon violet avant la saisie de sa combinaison.
5. Redéployer le projet Vercel.

Ne jamais utiliser la clé service role dans une variable préfixée par `NEXT_PUBLIC_`.

Le navigateur actualise l’état toutes les deux secondes. L’appareil qui crée la partie conserve localement le jeton MJ ; les appareils qui rejoignent la partie ne le reçoivent jamais.

## Kill switch MJ

Pour une base existante, réexécuter `supabase.sql` dans SQL Editor pour ajouter `accept_any_code` et `bypass_dragon` sans supprimer les parties. Seul le MJ peut activer ou désactiver les deux interrupteurs indépendants. Le kill switch des codes rend toute combinaison de quatre chiffres valide mais ne déchiffre pas le dragon. Le kill switch du dragon rend la saisie du cadenas 2 disponible sur tous les appareils, sans ouvrir le cadenas ni accepter les mauvais codes. Aucun interrupteur ne change l’étape à lui seul. Réinitialiser la partie désactive les deux.

## Épreuve du dragon — cadenas 2

Après le cadenas 1, les joueurs peuvent photographier le dessin assemblé ou choisir une photo, puis appuyer sur « Vérifier le dragon ». Le serveur extrait les traits violets ou indigo de la photo et compare uniquement ce masque au motif sur fond blanc de `scan-reference/dragon.png`. Une seconde référence, `dragon-visible.png`, contient seulement les traits du motif visibles après chevauchement, sans images ni textes des cartes. Aucun fond de carte n’est comparé. Les points caractéristiques ORB et plusieurs alignements par homographie permettent de tolérer les décalages et les parties masquées.

Les seuils sont regroupés dans `DRAGON_TOLERANCE` : au moins 60 % des traits du motif doivent être retrouvés et au moins 75 % des traits colorés détectés doivent correspondre au motif, avec un décalage local de 10 pixels sur un dessin normalisé à 512 pixels (environ 2 %). Un contrôle de couverture par région évite de valider une seule carte ou un assemblage dont une zone importante manque. L’extraction accepte la dérive du violet vers l’indigo lors de l’impression et de la prise de vue.

Une reconnaissance valide autorise la saisie du code du cadenas 2 sur l’appareil qui a scanné, sans changer l’étape. Une combinaison valide passe ensuite à l’étape 3, joue l’animation et débloque l’engramme 2 sur tous les appareils. Le champ et le bouton de combinaison sont entièrement masqués tant qu’aucun scan n’a réussi et que le kill switch du dragon est désactivé. Activer le kill switch du dragon fait apparaître la saisie, sans scan. Seul le kill switch des codes rend tout code à quatre chiffres valide. Les essais restent illimités. Les statuts des interrupteurs sont affichés uniquement dans la console MJ.

Le serveur signe une preuve du scan liée à la version de la partie, sans ajouter de colonne Supabase. Une erreur de combinaison renouvelle cette preuve pour permettre un nouvel essai. Un changement de la partie sur un autre appareil, une réinitialisation ou un rechargement de la page peut demander un nouveau scan.

La photo est redimensionnée sur l’appareil avant envoi et n’est pas enregistrée. Aucune API d’IA ni clé supplémentaire n’est nécessaire. Les références sont privées côté serveur et incluses dans le déploiement. Les tests couvrent une vraie photo des cartes imprimées, compression, rotation, luminosité, perspective, occlusion simulée, dessin incomplet, morceaux déplacés et image inversée. Tester plusieurs photos des cartes imprimées avant la partie pour vérifier les conditions réelles d’éclairage et d’empilement.
## Lecture des documents sur smartphone

Les documents des deux engrammes et le rapport de résolution utilisent un lecteur PDF.js intégré, sans iframe ni nouvel onglet. Chaque page est affichée dans l’application avec des boutons précédent/suivant, un zoom et un ajustement à la largeur. Le lecteur utilise les mêmes routes privées : l’accès reste soumis à l’ouverture des cadenas. Les pages sont rendues une à une et la résolution est plafonnée pour limiter la mémoire sur téléphone.

Le moteur PDF, ses polices et ses ressources sont servis depuis l’application, sans CDN. `scripts/copy-pdf-assets.mjs` les copie depuis la version installée de `pdfjs-dist` lors de l’installation et avant `npm run dev` ou `npm run build`. Ces fichiers générés sont exclus de Git et du lint. Aucune modification Supabase supplémentaire n’est nécessaire pour le lecteur.

## Conclusion de l’enquête

Une fois les deux cadenas ouverts, l’onglet Suspects présente les six personnes du dossier. Le joueur sélectionne un suspect puis confirme avec le bouton distinct « Désigner … coupable ». La réponse est vérifiée sur le serveur d’après le dossier : Salomé Kern est la coupable. Le kill switch des cadenas ne modifie pas ce verdict.

Les deux conclusions affichent l’anneau et proposent le rapport de résolution, consultable dans l’application. La conclusion incorrecte précise la restitution à 21 h 16 et l’intervention d’une équipe indépendante du futur. Le rapport privé `resolution-documents/rapport-enquete.pdf` est inaccessible avant l’ouverture des deux cadenas et reste séparé des engrammes. Chaque appareil formule sa propre accusation ; la conclusion est conservée pendant la navigation entre onglets et réinitialisée en quittant ou en réinitialisant la partie.
