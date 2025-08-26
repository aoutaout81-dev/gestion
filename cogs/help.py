import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    """Système d'aide du bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help", aliases=["aide", "h"])
    async def help_command(self, ctx, *, category: str = None):
        """Affiche la liste des commandes disponibles"""
        
        # Si une catégorie spécifique est demandée
        if category:
            category = category.lower()
            if category in ["admin", "administration"]:
                await self._send_admin_help(ctx)
            elif category in ["mod", "moderation", "modération"]:
                await self._send_moderation_help(ctx)
            elif category in ["role", "roles", "rôle", "rôles"]:
                await self._send_roles_help(ctx)
            else:
                embed = discord.Embed(
                    title="Catégorie introuvable",
                    description="Catégories disponibles : `administration`, `moderation`, `roles`",
                    color=self.bot.config.error_color
                )
                await ctx.send(embed=embed)
            return
        
        # Menu principal
        embed = discord.Embed(
            title="chdfz gestion - Aide",
            description="Choisissez une catégorie pour voir les commandes disponibles.",
            color=self.bot.config.embed_color
        )
        
        embed.add_field(
            name="Administration",
            value="`+help administration` - Gestion des permissions et configuration",
            inline=False
        )
        
        embed.add_field(
            name="Modération", 
            value="`+help moderation` - Commandes de modération des membres",
            inline=False
        )
        
        embed.add_field(
            name="Gestion des Rôles", 
            value="`+help roles` - Commandes de gestion des rôles",
            inline=False
        )
        
        embed.add_field(
            name="Informations",
            value=f"Préfixe actuel : `+`\n"
                  f"Serveurs : {len(self.bot.guilds)}\n"
                  f"Version : 2.0",
            inline=False
        )
        
        embed.set_footer(text="Utilisez +help <catégorie> pour voir les commandes détaillées")
        
        await ctx.send(embed=embed)
    
    async def _send_admin_help(self, ctx):
        """Envoie l'aide pour les commandes d'administration"""
        embed = discord.Embed(
            title="Commandes d'Administration",
            description="Gestion des permissions et configuration du bot",
            color=self.bot.config.embed_color
        )
        
        commands_list = [
            ("setperm", "Attribuer une permission", "`+setperm <commande> <rôle>`"),
            ("unsetperm", "Retirer une permission", "`+unsetperm <commande> <rôle>`"),
            ("perms", "Voir toutes les permissions", "`+perms`"),
            ("resetperms", "Réinitialiser les permissions", "`+resetperms`"),
            ("cooldown", "Définir un délai d'attente", "`+cooldown <commande> <secondes>`"),
            ("settings", "Voir les paramètres du serveur", "`+settings`"),
            ("prefix", "Changer le préfixe", "`+prefix <nouveau_préfixe>`")
        ]
        
        for name, desc, usage in commands_list:
            embed.add_field(
                name=f"`{name}`",
                value=f"{desc}\n{usage}",
                inline=False
            )
        
        embed.set_footer(text="Ces commandes nécessitent les permissions d'administrateur")
        
        await ctx.send(embed=embed)
    
    async def _send_moderation_help(self, ctx):
        """Envoie l'aide pour les commandes de modération"""
        embed = discord.Embed(
            title="🔨 Commandes de Modération",
            description="Gestion et modération des membres",
            color=self.bot.config.embed_color
        )
        
        commands_list = [
            ("ban", "Bannir un membre", "`+ban <membre> [raison]`"),
            ("unban", "Débannir un utilisateur", "`+unban <id_utilisateur>`"),
            ("kick", "Expulser un membre", "`+kick <membre> [raison]`"),
            ("mute", "Rendre muet un membre", "`+mute <membre> [durée] [raison]`"),
            ("unmute", "Enlever le mute", "`+unmute <membre>`"),
            ("warn", "Avertir un membre", "`+warn <membre> [raison]`"),
            ("infractions", "Voir l'historique d'un membre", "`+infractions <membre>`"),
            ("mutelist", "Liste des membres mués", "`+mutelist`"),
            ("clear", "Supprimer des messages", "`+clear <nombre>`"),
            ("lock", "Verrouiller un salon", "`+lock [#salon]`"),
            ("unlock", "Déverrouiller un salon", "`+unlock [#salon]`")
        ]
        
        for name, desc, usage in commands_list:
            embed.add_field(
                name=f"`{name}`",
                value=f"{desc}\n{usage}",
                inline=False
            )
        
        embed.add_field(
            name="📝 Format des durées",
            value="`10s` = 10 secondes\n`5m` = 5 minutes\n`2h` = 2 heures\n`1d` = 1 jour",
            inline=False
        )
        
        embed.set_footer(text="💡 Vous pouvez utiliser les noms d'utilisateurs au lieu de les mentionner")
        
        await ctx.send(embed=embed)
    
    async def _send_roles_help(self, ctx):
        """Envoie l'aide pour les commandes de gestion des rôles"""
        embed = discord.Embed(
            title="👑 Commandes de Gestion des Rôles",
            description="Gestion complète des rôles du serveur",
            color=self.bot.config.embed_color
        )
        
        commands_list = [
            ("addrole", "Ajouter un rôle à un membre", "`+addrole <membre> <rôle>`"),
            ("delrole", "Retirer un rôle d'un membre", "`+delrole <membre> <rôle>`"),
            ("createrole", "Créer un nouveau rôle", "`+createrole <nom> [couleur] [permissions]`"),
            ("deleterole", "Supprimer un rôle", "`+deleterole <rôle>`"),
            ("rolestats", "Statistiques d'un rôle", "`+rolestats <rôle>`")
        ]
        
        for name, desc, usage in commands_list:
            embed.add_field(
                name=f"`{name}`",
                value=f"{desc}\n{usage}",
                inline=False
            )
        
        embed.add_field(
            name="🎨 Couleurs disponibles",
            value="`rouge`, `bleu`, `vert`, `jaune`, `orange`, `violet`, `rose`, `cyan`, `noir`, `blanc` ou `#RRGGBB`",
            inline=False
        )
        
        embed.add_field(
            name="🔐 Permissions spéciales",
            value="`admin` = toutes les permissions\n`mod` = permissions de modération",
            inline=False
        )
        
        embed.set_footer(text="💡 Vous pouvez utiliser les noms de rôles et membres directement")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))