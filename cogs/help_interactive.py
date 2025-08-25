import discord
from discord.ext import commands

class HelpView(discord.ui.View):
    """Vue interactive pour le système d'aide"""
    
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot
        
    @discord.ui.button(label="🎛️ Administration", style=discord.ButtonStyle.primary)
    async def admin_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Affiche l'aide pour les commandes d'administration"""
        embed = discord.Embed(
            title="🎛️ Commandes d'Administration",
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
        
        embed.set_footer(text="⚠️ Ces commandes nécessitent les permissions d'administrateur")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔨 Modération", style=discord.ButtonStyle.primary)
    async def moderation_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Affiche l'aide pour les commandes de modération"""
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
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="👑 Rôles", style=discord.ButtonStyle.primary)
    async def roles_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Affiche l'aide pour les commandes de gestion des rôles"""
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
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="👨‍💼 Ownership", style=discord.ButtonStyle.success)
    async def ownership_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Affiche l'aide pour les commandes d'ownership"""
        embed = discord.Embed(
            title="👨‍💼 Commandes Ownership",
            description="Gestion avancée du bot et propriété",
            color=self.bot.config.embed_color
        )
        
        embed.add_field(
            name="🏢 Commandes Owners",
            value=(
                "`massrole <rôle>` - Donne le rôle à tous les humains\n"
                "`say <message>` - Fait parler le bot anonymement\n"
                "`dm <membre> <msg>` - Message privé via le bot\n"
                "`laisse <membre>` - Met en laisse (🐶🦮)\n"
                "`unlaisse <membre>` - Retire de la laisse\n"
                "`wl <membre>` - Ajoute à la whitelist anti-raid\n"
                "`unwl <membre>` - Retire de la whitelist\n"
                "`blrank add <membre>` - Ajoute au blacklist-rank\n"
                "`blrank del <membre>` - Retire du blacklist-rank\n"
                "`blrank` - Liste blacklist-rank"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔑 Commandes Buyer (Propriétaire)",
            value=(
                "`owner <membre>` - Ajoute un owner\n"
                "`unowner <membre>` - Retire un owner\n"
                "`buyer <membre> <code>` - Transfert la propriété"
            ),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Hiérarchie",
            value=(
                "**Buyer** : Propriétaire principal avec code de récupération\n"
                "**Owners** : Administrateurs avec privilèges étendus\n"
                "**Whitelist** : Immunité aux protections anti-raid\n"
                "**Blacklist-rank** : Protection contre attribution de rôles"
            ),
            inline=False
        )
        
        embed.set_footer(text="🦮 Le système de laisse surveille automatiquement les pseudos")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.secondary, row=1)
    async def main_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retourne au menu principal"""
        embed = discord.Embed(
            title="📚 CrowBot Gestion V2 - Aide Interactive",
            description="Choisissez une catégorie avec les boutons ci-dessous pour voir les commandes disponibles.",
            color=self.bot.config.embed_color
        )
        
        embed.add_field(
            name="🎛️ Administration",
            value="Gestion des permissions et configuration",
            inline=True
        )
        
        embed.add_field(
            name="🔨 Modération", 
            value="Commandes de modération des membres",
            inline=True
        )
        
        embed.add_field(
            name="👑 Rôles", 
            value="Gestion complète des rôles",
            inline=True
        )
        
        embed.add_field(
            name="👨‍💼 Ownership", 
            value="Commandes avancées propriété",
            inline=True
        )
        
        embed.add_field(
            name="ℹ️ Informations",
            value=f"Préfixe actuel : `+`\nServeurs : {len(self.bot.guilds)}\nVersion : 2.0",
            inline=False
        )
        
        embed.set_footer(text="Sélectionnez une catégorie avec les boutons ci-dessous")
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """Appelé quand la vue expire"""
        # Disable all buttons when timeout
        for item in self.children:
            item.disabled = True

class HelpCommand(commands.Cog):
    """Système d'aide interactif du bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help", aliases=["aide", "h"])
    async def help_command(self, ctx):
        """Affiche le menu d'aide interactif"""
        
        embed = discord.Embed(
            title="📚 CrowBot Gestion V2 - Aide Interactive",
            description="Choisissez une catégorie avec les boutons ci-dessous pour voir les commandes disponibles.",
            color=self.bot.config.embed_color
        )
        
        embed.add_field(
            name="🎛️ Administration",
            value="Gestion des permissions et configuration",
            inline=True
        )
        
        embed.add_field(
            name="🔨 Modération", 
            value="Commandes de modération des membres",
            inline=True
        )
        
        embed.add_field(
            name="👑 Rôles", 
            value="Gestion complète des rôles",
            inline=True
        )
        
        embed.add_field(
            name="👨‍💼 Ownership", 
            value="Commandes avancées propriété",
            inline=True
        )
        
        embed.add_field(
            name="ℹ️ Informations",
            value=f"Préfixe actuel : `+`\nServeurs : {len(self.bot.guilds)}\nVersion : 2.0",
            inline=False
        )
        
        embed.set_footer(text="Sélectionnez une catégorie avec les boutons ci-dessous")
        
        view = HelpView(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))