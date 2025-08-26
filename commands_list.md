# Liste Complète des Commandes - chdfz gestion Bot

## Commandes de Modération (Permission 1 - Modération Basique)
- `+clear <nombre>` - Supprimer des messages (1-100)
- `+warn <@utilisateur> [raison]` - Avertir un utilisateur
- `+mute <@utilisateur> [durée] [raison]` - Rendre muet un utilisateur

## Commandes de Modération Avancée (Permission 2 - Modération Complète)
- `+kick <@utilisateur> [raison]` - Expulser un utilisateur
- `+ban <@utilisateur> [raison]` - Bannir un utilisateur
- `+unban <@utilisateur> [raison]` - Débannir un utilisateur
- `+unmute <@utilisateur>` - Retirer le mute d'un utilisateur
- `+delwarn <@utilisateur> <ID_warn>` - Supprimer un avertissement
- `+infractions <@utilisateur>` - Voir les infractions d'un utilisateur
- `+mutelist` - Liste des utilisateurs mutés
- `+lock [#salon]` - Verrouiller un salon
- `+unlock [#salon]` - Déverrouiller un salon

## Commandes d'Administration (Permission 3 - Administration)
- `+set perm <niveau> <@rôle/@utilisateur>` - Assigner niveau de permission (1-9)
- `+set perm <commande> <@rôle/@utilisateur>` - Permission spécifique pour commande
- `+del perm <niveau> <@rôle/@utilisateur>` - Retirer niveau de permission
- `+change <commande> <niveau>` - Changer le niveau d'une commande
- `+change reset` - Remettre permissions par défaut
- `+changeall <ancien> <nouveau>` - Déplacer commandes d'un niveau
- `+clearperms` - Supprimer toutes les permissions (avec confirmation)
- `+addrole <@utilisateur> <@rôle>` - Ajouter un rôle à un utilisateur
- `+delrole <@utilisateur> <@rôle>` - Retirer un rôle à un utilisateur
- `+prefix <nouveau_prefix>` - Changer le préfixe du bot
- `+setcooldown <commande> <secondes>` - Définir cooldown pour commande

## Commandes Ownership (Owners uniquement)
- `+massrole <@rôle>` - Donner un rôle à tous les humains du serveur
- `+say <#salon> <message>` - Faire parler le bot anonymement
- `+dm <@utilisateur> <message>` - Envoyer un MP via le bot
- `+laisse <@utilisateur>` - Mettre un utilisateur "en laisse" (contrôle pseudo + 🐶)
- `+unlaisse <@utilisateur>` - Retirer de la laisse (+ 🦮)
- `+wl <@utilisateur>` - Ajouter à la whitelist (immunité anti-raid)
- `+unwl <@utilisateur>` - Retirer de la whitelist
- `+blrank add <@utilisateur>` - Ajouter à la blacklist-rank
- `+blrank del <@utilisateur>` - Retirer de la blacklist-rank

## Commandes Buyer (Propriétaire Unique)
- `+owner <@utilisateur>` - Promouvoir quelqu'un owner
- `+unowner <@utilisateur>` - Retirer le statut d'owner
- `+buyer <@utilisateur> [code]` - Transférer propriété (avec code récupération)

## Commandes Publiques (Tout le monde)
- `+help` - Afficher l'aide interactive
- `+helpall` - Voir toutes les commandes par niveau de permission
- `+perms` - Afficher la configuration des permissions
- `+ping` - Vérifier la latence du bot

## Commandes de Configuration (Permission 3+)
- `+settings` - Afficher les paramètres du serveur
- `+muterole <@rôle>` - Définir le rôle de mute
- `+logchannel <#salon>` - Définir le salon de logs

## Hiérarchie des Permissions

### Niveaux de Permission (1-9)
1. **Perm 1** - Modération basique (clear, warn, mute)
2. **Perm 2** - Modération complète (kick, ban, unban, unmute, etc.)
3. **Perm 3** - Administration (setperm, change, addrole, etc.)
4. **Perm 4-9** - Niveaux personnalisables

### Niveaux Spéciaux
- **Owner** - Accès aux commandes ownership
- **Buyer** - Propriétaire unique avec transfert
- **Public** - Commandes d'information
- **Everyone** - Accessible à tous

## Fonctionnalités Spéciales

### Système de Laisse 🐶🦮
Le système de "laisse" permet aux owners de contrôler le pseudonyme d'un utilisateur :
- `+laisse` ajoute l'emoji 🐶 au pseudo
- `+unlaisse` remplace 🐶 par 🦮
- Le bot surveille et maintient ces emojis automatiquement

### Système de Permissions Hiérarchique
- Les permissions sont hiérarchiques (perm1 < perm2 < ... < perm9)
- Un utilisateur avec perm2 peut utiliser les commandes perm1 et perm2
- Attribution flexible par rôle ou utilisateur individuel

### Réponses Simplifiées
Certaines commandes ont des réponses simplifiées sans embeds pour une expérience plus directe :
- addrole, delrole, warn, clear, mute, unmute, setperm, unsetperm

### Anti-Raid et Sécurité
- **Whitelist** : Immunité contre les mesures anti-raid
- **Blacklist-rank** : Restriction d'accès aux commandes de gestion de rôles
- **Code de récupération** : Protection du transfert de propriété