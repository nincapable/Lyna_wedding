# Synchronisation des parties

L’application utilise Supabase comme stockage partagé. Les secrets restent côté serveur Vercel.

1. Créer un projet sur Supabase.
2. Ouvrir **SQL Editor**, coller le contenu de `supabase.sql`, puis exécuter la requête.
3. Dans Vercel, ouvrir **Settings > Environment Variables** et ajouter `SUPABASE_URL` et `SUPABASE_SERVICE_ROLE_KEY`.
4. Facultatif : ajouter `LOCK_1_CODES` et `LOCK_2_CODES`, sous forme de listes séparées par des virgules.
5. Redéployer le projet Vercel.

Ne jamais utiliser la clé service role dans une variable préfixée par `NEXT_PUBLIC_`.

Le navigateur actualise l’état toutes les deux secondes. L’appareil qui crée la partie conserve localement le jeton MJ ; les appareils qui rejoignent la partie ne le reçoivent jamais.

## Kill switch MJ

Pour une base existante, réexécuter `supabase.sql` dans SQL Editor pour ajouter `accept_any_code` sans supprimer les parties. Seul le MJ peut activer ou désactiver le kill switch. L’activer ne change pas l’étape. Lorsqu’il est actif, toute combinaison de quatre chiffres saisie par les joueurs est valide et fait passer à l’étape suivante, comme une bonne combinaison. Réinitialiser la partie désactive le kill switch.
