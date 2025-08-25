# CrowBot Gestion V2 - Discord Bot

## Overview
CrowBot est un bot Discord de modération avancée avec système de gestion hiérarchique et fonctionnalités anti-raid. Le bot utilise Python avec discord.py et une base de données SQLite pour la persistance.

## Recent Changes (25 août 2025)
- ✅ Migration vers Replit complétée
- ✅ Nouvelles commandes ownership/administration avancées ajoutées
- ✅ Système de buyers/owners implémenté
- ✅ Système de whitelist/blacklist ajouté
- ✅ Système de "laisse" pour contrôler les pseudos
- ✅ Commandes de communication anonyme (say, dm)
- ✅ Réponses simplifiées pour commandes principales
- ✅ Commande massrole pour attribution de rôles en masse

## Project Architecture

### Core Files
- `main.py` - Point d'entrée principal
- `bot.py` - Classe principale du bot
- `database.py` - Gestion de la base de données SQLite
- `config.py` - Configuration du bot

### Cogs (Modules)
- `cogs/administration.py` - Commandes d'administration
- `cogs/moderation.py` - Commandes de modération
- `cogs/roles.py` - Gestion des rôles
- `cogs/help.py` - Système d'aide
- `cogs/triggers.py` - Système de triggers/réponses automatiques
- `cogs/ownership.py` - **NOUVEAU** Commandes avancées ownership

### Utilities
- `utils/permissions.py` - Système de permissions
- `utils/helpers.py` - Fonctions utilitaires
- `utils/converters.py` - Convertisseurs Discord

## User Preferences
- Réponses simplifiées préférées pour les commandes de base
- Interface en français
- Messages d'erreur clairs et concis

## Database Schema
- Tables existantes : guild_settings, command_permissions, command_cooldowns, command_usage, infractions, muted_users, moderation_logs
- **Nouvelles tables** : bot_ownership, owners, whitelist, blacklist_rank, leash_system

## Nouvelles Fonctionnalités Implémentées

### Système Hiérarchique
- **buyer** : Propriétaire principal du bot avec code de récupération
- **owners** : Utilisateurs avec privilèges étendus
- **whitelist** : Utilisateurs immunisés contre l'anti-raid

### Commandes Ownership (Owners uniquement)
- `massrole` - Attribution de rôles en masse aux humains
- `say` - Communication anonyme via le bot
- `dm` - Messages privés via le bot  
- `laisse/unlaisse` - Contrôle des pseudos avec émojis 🐶🦮
- `wl/unwl` - Gestion whitelist
- `blrank add/del` - Gestion blacklist-rank

### Commandes Buyer (Propriétaire uniquement)
- `owner/unowner` - Gestion des owners
- `buyer` - Transfert de propriété avec code de récupération

### Réponses Simplifiées
Les commandes suivantes ont maintenant des réponses simplifiées sans embeds :
- addrole, delrole, warn, clear, mute, unmute, setperm, unsetperm

## Configuration Requise
- Python 3.11+
- discord.py >= 2.6.2
- Variable d'environnement DISCORD_TOKEN requise

## Status
✅ Bot opérationnel et prêt à l'emploi
✅ Migration Replit terminée
✅ Toutes les nouvelles fonctionnalités implémentées