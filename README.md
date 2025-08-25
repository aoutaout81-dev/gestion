# 🎯 CrowBot Gestion V2

**CrowBot Gestion V2** est un bot Discord de modération et d'administration complet, développé en Python avec discord.py. Il offre un système de gestion avancé pour les serveurs Discord avec des fonctionnalités de modération, d'administration et de gestion des rôles.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Structure du projet](#-structure-du-projet)
- [Commandes disponibles](#-commandes-disponibles)
- [Permissions et sécurité](#-permissions-et-sécurité)
- [Architecture du code](#-architecture-du-code)
- [Guide de développement](#-guide-de-développement)
- [Troubleshooting](#-troubleshooting)
- [Contribuer](#-contribuer)

## 🚀 Fonctionnalités

### 🎛️ **Administration**
- Gestion des permissions par rôle
- Configuration des cooldowns
- Gestion du préfixe personnalisé
- Réinitialisation des paramètres
- Affichage des configurations

### 🔨 **Modération**
- Bannissement et débannissement
- Expulsion des membres
- Système de mute temporaire ou permanent
- Système d'avertissements
- Historique des infractions
- Nettoyage de messages
- Verrouillage/déverrouillage de salons

### 👑 **Gestion des rôles**
- Ajout et suppression de rôles
- Création de rôles avec couleurs personnalisées
- Suppression de rôles existants
- Statistiques détaillées des rôles
- Support des noms, mentions et IDs

### 🛡️ **Sécurité**
- Système de permissions hiérarchique
- Vérification des rôles et positions
- Logs détaillés de toutes les actions
- Protection contre l'auto-modération
- Messages d'erreur en français

## 💻 Installation

### Prérequis
- Python 3.7 ou supérieur
- discord.py 2.6+
- SQLite3 (inclus avec Python)

### Installation rapide

1. **Clonez le projet**
```bash
git clone <url-du-repo>
cd crowbot-gestion-v2
```

2. **Installez les dépendances**
```bash
pip install discord.py
```

3. **Configurez le bot**
   - Créez une application Discord sur [Discord Developer Portal](https://discord.com/developers/applications)
   - Récupérez le token du bot
   - Configurez les variables d'environnement

4. **Lancez le bot**
```bash
python main.py
```

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` ou définissez les variables suivantes :

```env
DISCORD_TOKEN=votre_token_discord_ici
```

### Permissions Discord requises

Le bot nécessite les permissions suivantes :
- `Gérer les rôles`
- `Expulser des membres`
- `Bannir des membres` 
- `Gérer les messages`
- `Gérer les salons`
- `Lire l'historique des messages`
- `Mentionner tout le monde`

### Intents requis

```python
intents.message_content = True
intents.members = True
intents.guilds = True
```

## 📁 Structure du projet

```
crowbot-gestion-v2/
├── main.py                 # Point d'entrée principal
├── bot.py                  # Classe principale du bot
├── config.py               # Configuration et constantes
├── database.py             # Gestion de la base de données SQLite
├── cogs/                   # Modules de commandes
│   ├── administration.py   # Commandes d'administration
│   ├── moderation.py      # Commandes de modération
│   ├── roles.py           # Gestion des rôles
│   └── help.py            # Système d'aide
├── utils/                  # Utilitaires
│   ├── permissions.py     # Système de permissions
│   ├── helpers.py         # Fonctions d'aide
│   └── converters.py      # Convertisseurs personnalisés
├── crowbot.db             # Base de données SQLite (auto-créée)
├── crowbot.log            # Fichier de logs
└── README.md              # Ce fichier
```

## 📚 Commandes disponibles

### 🎛️ Administration

| Commande | Description | Usage |
|----------|-------------|--------|
| `setperm` | Attribuer une permission | `+setperm <commande> <rôle>` |
| `unsetperm` | Retirer une permission | `+unsetperm <commande> <rôle>` |
| `perms` | Voir toutes les permissions | `+perms` |
| `resetperms` | Réinitialiser les permissions | `+resetperms` |
| `cooldown` | Définir un délai d'attente | `+cooldown <commande> <secondes>` |
| `settings` | Voir les paramètres du serveur | `+settings` |
| `prefix` | Changer le préfixe | `+prefix <nouveau_préfixe>` |

### 🔨 Modération

| Commande | Description | Usage |
|----------|-------------|--------|
| `ban` | Bannir un membre | `+ban <membre> [raison]` |
| `unban` | Débannir un utilisateur | `+unban <id_utilisateur>` |
| `kick` | Expulser un membre | `+kick <membre> [raison]` |
| `mute` | Rendre muet un membre | `+mute <membre> [durée] [raison]` |
| `unmute` | Enlever le mute | `+unmute <membre>` |
| `warn` | Avertir un membre | `+warn <membre> [raison]` |
| `infractions` | Voir l'historique d'un membre | `+infractions <membre>` |
| `mutelist` | Liste des membres mués | `+mutelist` |
| `clear` | Supprimer des messages | `+clear <nombre>` |
| `lock` | Verrouiller un salon | `+lock [#salon]` |
| `unlock` | Déverrouiller un salon | `+unlock [#salon]` |

### 👑 Gestion des rôles

| Commande | Description | Usage |
|----------|-------------|--------|
| `addrole` | Ajouter un rôle à un membre | `+addrole <membre> <rôle>` |
| `delrole` | Retirer un rôle d'un membre | `+delrole <membre> <rôle>` |
| `createrole` | Créer un nouveau rôle | `+createrole <nom> [couleur] [permissions]` |
| `deleterole` | Supprimer un rôle | `+deleterole <rôle>` |
| `rolestats` | Statistiques d'un rôle | `+rolestats <rôle>` |

### 📚 Aide

| Commande | Description | Usage |
|----------|-------------|--------|
| `help` | Menu d'aide principal | `+help [catégorie]` |
| `help administration` | Aide administration | `+help administration` |
| `help moderation` | Aide modération | `+help moderation` |
| `help roles` | Aide gestion des rôles | `+help roles` |

## 🔒 Permissions et sécurité

### Système de permissions hiérarchique

1. **Propriétaire du bot** : Accès total
2. **Propriétaire du serveur** : Accès total sur son serveur  
3. **Administrateurs** : Commandes d'administration et modération
4. **Rôles personnalisés** : Selon configuration avec `setperm`

### Protections intégrées

- ✅ Vérification de la hiérarchie des rôles
- ✅ Impossibilité d'auto-modération
- ✅ Protection des rôles système
- ✅ Validation des permissions Discord
- ✅ Logs complets de toutes les actions

### Format des durées

Pour les commandes temporaires (mute) :
- `10s` = 10 secondes
- `5m` = 5 minutes  
- `2h` = 2 heures
- `1d` = 1 jour
- `1w` = 1 semaine

### Couleurs disponibles pour les rôles

**Noms prédéfinis :**
`rouge`, `bleu`, `vert`, `jaune`, `orange`, `violet`, `rose`, `cyan`, `noir`, `blanc`

**Format hexadécimal :**
`#FF0000`, `#00FF00`, `#0000FF`, etc.

## 🏗️ Architecture du code

### Composants principaux

#### `main.py`
Point d'entrée du bot qui :
- Configure les logs
- Récupère le token
- Lance le bot avec gestion des erreurs

#### `bot.py` - Classe CrowBot
Classe principale héritant de `commands.Bot` :
- Configuration des intents
- Gestion des préfixes dynamiques
- Chargement des cogs
- Gestion globale des erreurs
- Système de permissions personnalisé

#### `database.py` - Gestion des données
Classe Database avec SQLite :
- Tables : guilds, permissions, cooldowns, infractions, mutes, logs
- Opérations asynchrones avec verrous
- Méthodes CRUD complètes

#### `config.py` - Configuration
Centralise toutes les configurations :
- Couleurs des embeds
- Listes de commandes par catégorie
- Unités de temps
- Préfixe par défaut

### Structure des Cogs

Chaque cog représente une catégorie de fonctionnalités :

```python
class MonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @has_permission()  # Décorateur de permissions
    async def ma_commande(self, ctx, arg: CustomConverter):
        # Logique de la commande
        pass
```

### Système de permissions

#### Décorateurs disponibles

```python
@has_permission()    # Vérifie permissions + cooldown
@admin_only()        # Administrateurs uniquement
```

#### Convertisseurs personnalisés

```python
MemberConverter     # Membre par nom/mention/ID
RoleConverter       # Rôle par nom/mention/ID  
UserConverter       # Utilisateur par nom/ID
```

## 🛠️ Guide de développement

### Ajouter une nouvelle commande

1. **Choisir le cog approprié** ou créer un nouveau
2. **Définir la commande avec décorateurs**
3. **Implémenter la logique métier**
4. **Ajouter les vérifications de sécurité**
5. **Logger l'action si nécessaire**
6. **Mettre à jour l'aide**

#### Exemple complet

```python
@commands.command(name="macommande")
@has_permission()
async def ma_commande(self, ctx, membre: MemberConverter, *, raison: str = "Aucune raison"):
    """Description de ma commande"""
    
    # Vérifications de sécurité
    if membre == ctx.author:
        embed = discord.Embed(
            title="❌ Erreur",
            description="Vous ne pouvez pas vous cibler vous-même.",
            color=self.bot.config.error_color
        )
        await ctx.send(embed=embed)
        return
    
    try:
        # Logique principale
        # ... votre code ici ...
        
        # Log de l'action
        await self.bot.db.log_moderation_action(
            ctx.guild.id, membre.id, ctx.author.id, "macommande", raison
        )
        
        # Confirmation
        embed = discord.Embed(
            title="✅ Succès",
            description=f"Action réalisée sur **{membre}**.",
            color=self.bot.config.success_color
        )
        embed.add_field(name="Raison", value=raison, inline=False)
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Échec de l'opération : {str(e)}",
            color=self.bot.config.error_color
        )
        await ctx.send(embed=embed)
```

### Ajouter un nouveau cog

1. **Créer le fichier** `cogs/mon_cog.py`
2. **Implémenter la classe** héritant de `commands.Cog`
3. **Ajouter la fonction setup**
4. **Charger dans bot.py**
5. **Mettre à jour l'aide**

#### Template de cog

```python
import discord
from discord.ext import commands
from utils.permissions import has_permission
from utils.converters import MemberConverter

class MonCog(commands.Cog):
    """Description de mon cog"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="test")
    @has_permission()
    async def test_command(self, ctx):
        """Commande de test"""
        await ctx.send("Commande test fonctionnelle !")

async def setup(bot):
    await bot.add_cog(MonCog(bot))
```

### Étendre la base de données

Pour ajouter une nouvelle table :

```python
# Dans database.py, méthode initialize()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ma_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        user_id INTEGER,
        data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
```

Ajouter les méthodes CRUD correspondantes.

### Tests et debugging

#### Logs disponibles

```python
self.bot.logger.info("Message d'information")
self.bot.logger.warning("Avertissement")
self.bot.logger.error("Erreur")
```

Les logs sont écrits dans `crowbot.log` et la console.

#### Variables d'environnement de debug

```env
DISCORD_TOKEN=votre_token
DEBUG=1  # Active le mode debug (optionnel)
```

## 🔧 Troubleshooting

### Problèmes courants

#### Le bot ne se connecte pas
- Vérifiez le token Discord
- Vérifiez les intents dans le Developer Portal
- Vérifiez que le bot a été invité sur le serveur

#### Commandes ne fonctionnent pas
- Vérifiez le préfixe configuré (`+settings`)
- Vérifiez les permissions Discord du bot
- Vérifiez les permissions personnalisées (`+perms`)

#### Erreurs de base de données
- Vérifiez les permissions d'écriture du dossier
- Supprimez `crowbot.db` pour réinitialiser (⚠️ perte de données)

#### Erreurs de permissions
- Vérifiez la position du rôle du bot
- Vérifiez que le bot a les permissions Discord nécessaires
- Vérifiez la hiérarchie des rôles

### Messages d'erreur fréquents

#### "Membre introuvable"
L'utilisateur saisi n'existe pas sur le serveur ou le nom est incorrect.

#### "Rôle introuvable"  
Le rôle saisi n'existe pas ou le nom est incorrect.

#### "Permission insuffisante"
Le bot n'a pas les permissions Discord nécessaires pour cette action.

#### "Argument requis manquant"
Une commande a été utilisée sans tous ses arguments obligatoires.

### Commandes de diagnostic

```bash
# Vérifier les permissions
+settings

# Voir les permissions personnalisées
+perms

# Tester une commande simple
+help
```

## 📝 Changelog

### Version 2.0
- ✅ Système de gestion des rôles complet
- ✅ Convertisseurs personnalisés pour noms/mentions/IDs
- ✅ Messages d'erreur en français
- ✅ Commande help avec menu par catégories
- ✅ Amélioration du système de permissions
- ✅ Logs détaillés de toutes les actions

### Version 1.0
- ✅ Système de modération complet
- ✅ Gestion des permissions par rôle
- ✅ Base de données SQLite
- ✅ Système d'infractions et mutes
- ✅ Configuration par serveur

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🤝 Contribuer

Les contributions sont les bienvenues ! 

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** vos changements (`git commit -m 'Add AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

### Guidelines de contribution

- Respecter le style de code existant
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation
- S'assurer que tous les tests passent

## 📞 Support

Pour obtenir de l'aide :

1. Consulter ce README
2. Vérifier les [Issues GitHub](lien-vers-issues)
3. Utiliser la commande `+help` dans Discord
4. Consulter les logs dans `crowbot.log`

---

**Développé avec ❤️ en Python | Powered by discord.py**