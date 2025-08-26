import discord
from discord.ext import commands
from utils.permissions import has_permission, admin_only, owner_only, buyer_only, get_permission_level_name, get_permission_description
from utils.helpers import parse_time, format_time
from utils.converters import RoleConverter

class Administration(commands.Cog):
    """Administration and configuration commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="set")
    @admin_only()
    async def set_permission(self, ctx, perm_type: str, level_or_command: str, target: str = None):
        """Système de permissions CrowBots compatible
        
        Usage:
        +set perm <niveau> <@role/@user> - Assigner niveau de permission
        +set perm <commande> <@role/@user> - Permission spécifique pour commande  
        """
        if perm_type.lower() == "perm":
            # Deux cas: +set perm <niveau> <@role> OU +set perm <commande> <@role>
            
            # Essayer d'abord niveau numérique
            try:
                level = int(level_or_command)
                if level < 1 or level > 9:
                    await ctx.send("❌ Le niveau de permission doit être entre 1 et 9")
                    return
                
                if not target:
                    await ctx.send("❌ Vous devez mentionner un rôle ou un membre\n💡 Usage: `+set perm <niveau> <@rôle/@membre>`")
                    return
                
                # Parser le target
                role_id, user_id = await self._parse_target(ctx, target)
                if not role_id and not user_id:
                    return
                
                await self.bot.db.set_permission_level(ctx.guild.id, level, role_id=role_id, user_id=user_id)
                
                if role_id:
                    role = ctx.guild.get_role(role_id)
                    await ctx.send(f"✅ Rôle {role.mention} assigné au **niveau de permission {level}**")
                else:
                    user = ctx.guild.get_member(user_id)
                    await ctx.send(f"✅ Membre {user.mention} assigné au **niveau de permission {level}**")
                
            except ValueError:
                # Cas: +set perm <commande> <@role>
                command_name = level_or_command.lower()
                if not target:
                    await ctx.send("❌ Vous devez mentionner un rôle ou un membre\n💡 Usage: `+set perm <commande> <@rôle/@membre>`")
                    return
                
                role_id, user_id = await self._parse_target(ctx, target)
                if not role_id and not user_id:
                    return
                
                await self.bot.db.set_command_specific_permission(ctx.guild.id, command_name, role_id=role_id, user_id=user_id)
                
                if role_id:
                    role = ctx.guild.get_role(role_id)
                    await ctx.send(f"✅ Rôle {role.mention} a maintenant accès à la commande **{command_name}**")
                else:
                    user = ctx.guild.get_member(user_id)
                    await ctx.send(f"✅ Membre {user.mention} a maintenant accès à la commande **{command_name}**")
        
        else:
            await ctx.send("❌ Usage incorrect. Utilisez: `+set perm <niveau> <@rôle>` ou `+set perm <commande> <@rôle>`")
    
    @commands.command(name="del")
    @admin_only()
    async def delete_permission(self, ctx, perm_type: str, level_or_command: str, target: str = None):
        """Supprimer des permissions CrowBots
        
        Usage:
        +del perm <niveau> <@rôle/@membre> - Retirer niveau de permission
        """
        if perm_type.lower() == "perm":
            try:
                level = int(level_or_command)
                if level < 1 or level > 9:
                    await ctx.send("❌ Le niveau de permission doit être entre 1 et 9")
                    return
                
                if not target:
                    await ctx.send("❌ Vous devez mentionner un rôle ou un utilisateur")
                    return
                
                role_id, user_id = await self._parse_target(ctx, target)
                if not role_id and not user_id:
                    return
                
                await self.bot.db.remove_permission_level(ctx.guild.id, level, role_id=role_id, user_id=user_id)
                
                if role_id:
                    role = ctx.guild.get_role(role_id)
                    await ctx.send(f"✅ Rôle {role.mention} retiré du **niveau de permission {level}**")
                else:
                    user = ctx.guild.get_member(user_id)
                    await ctx.send(f"✅ Membre {user.mention} retiré du **niveau de permission {level}**")
                
            except ValueError:
                await ctx.send("❌ Niveau de permission invalide")
                return
        else:
            await ctx.send("❌ Usage: `+del perm <niveau> <@rôle/@membre>`")
    
    @commands.command(name="change")
    @admin_only()
    async def change_command_permission(self, ctx, command_name: str = None, permission_level: str = None):
        """Changer le niveau de permission d'une commande CrowBots
        
        Usage:
        +change <commande> <niveau> - Déplacer commande vers niveau
        +change reset - Remettre toutes les permissions par défaut
        """
        if command_name and command_name.lower() == "reset":
            # Reset toutes les permissions
            await self.bot.db.reset_permissions(ctx.guild.id)
            await self.bot.db.initialize_default_permissions(ctx.guild.id)
            await ctx.send("✅ **Toutes les permissions ont été remises à leurs valeurs par défaut**")
            return
        
        if not command_name or not permission_level:
            await ctx.send("❌ Usage: `+change <commande> <niveau>` ou `+change reset`")
            return
        
        # Valider le niveau de permission
        valid_levels = ['perm1', 'perm2', 'perm3', 'perm4', 'perm5', 'perm6', 'perm7', 'perm8', 'perm9', 'owner', 'buyer', 'public', 'everyone']
        if permission_level.lower() not in valid_levels:
            await ctx.send(f"❌ Niveau de permission invalide.\n💡 Niveaux disponibles: {', '.join(valid_levels)}")
            return
        
        await self.bot.db.set_command_permission(ctx.guild.id, command_name.lower(), permission_level.lower())
        await ctx.send(f"✅ Commande **{command_name}** déplacée vers **{permission_level}**")
    
    @commands.command(name="changeall")
    @admin_only()
    async def change_all_permissions(self, ctx, old_level: str = None, new_level: str = None):
        """Déplacer toutes les commandes d'un niveau vers un autre CrowBots
        
        Usage: +changeall <ancien_niveau> <nouveau_niveau>
        Exemple: +changeall perm3 perm4
        """
        if not old_level or not new_level:
            await ctx.send("❌ Usage: `+changeall <ancien_niveau> <nouveau_niveau>`\n💡 Exemple: `+changeall perm3 perm4`")
            return
            
        # Valider les niveaux de permission
        valid_levels = ['perm1', 'perm2', 'perm3', 'perm4', 'perm5', 'perm6', 'perm7', 'perm8', 'perm9', 'owner', 'buyer', 'public', 'everyone']
        
        if old_level.lower() not in valid_levels or new_level.lower() not in valid_levels:
            await ctx.send(f"❌ Niveaux invalides.\n💡 Niveaux disponibles: {', '.join(valid_levels)}")
            return
        
        # Obtenir toutes les commandes du niveau ancien
        all_perms = await self.bot.db.get_all_command_permissions(ctx.guild.id)
        commands_to_move = [cmd for cmd, level in all_perms.items() if level == old_level.lower()]
        
        if not commands_to_move:
            await ctx.send(f"❌ Aucune commande trouvée au niveau **{old_level}**")
            return
        
        # Déplacer toutes les commandes
        for command_name in commands_to_move:
            await self.bot.db.set_command_permission(ctx.guild.id, command_name, new_level.lower())
        
        await ctx.send(f"✅ **{len(commands_to_move)} commandes** déplacées de **{old_level}** vers **{new_level}**\n"
                      f"Commandes déplacées: {', '.join(commands_to_move)}")
    
    @commands.command(name="perms")
    async def show_permissions(self, ctx):
        """Affiche les permissions et rôles associés CrowBots"""
        try:
            # Get permission levels
            permission_levels = await self.bot.db.get_permission_levels(ctx.guild.id)
            command_permissions = await self.bot.db.get_all_command_permissions(ctx.guild.id)
            
            embed = discord.Embed(
                title="Système de Permissions",
                description="Configuration hiérarchique des permissions (niveaux 1-9)",
                color=self.bot.config.embed_color
            )
            
            # Show permission levels
            if permission_levels:
                for level in sorted(permission_levels.keys()):
                    data = permission_levels[level]
                    roles_text = ""
                    users_text = ""
                    
                    if data['roles']:
                        roles = [ctx.guild.get_role(r_id) for r_id in data['roles']]
                        roles_text = ", ".join([r.mention for r in roles if r])
                    
                    if data['users']:
                        users = [ctx.guild.get_member(u_id) for u_id in data['users']]
                        users_text = ", ".join([u.mention for u in users if u])
                    
                    field_value = ""
                    if roles_text:
                        field_value += f"**Rôles:** {roles_text}\n"
                    if users_text:
                        field_value += f"**Utilisateurs:** {users_text}\n"
                    
                    if not field_value:
                        field_value = "*Aucun rôle/utilisateur assigné*"
                    
                    embed.add_field(
                        name=f"Permission Niveau {level}",
                        value=field_value,
                        inline=False
                    )
            else:
                embed.add_field(
                    name="Niveaux de Permission",
                    value="*Aucun niveau configuré*\nUtilisez `+set perm <niveau> <@role/@user>` pour configurer",
                    inline=False
                )
            
            # Group commands by permission level
            commands_by_level = {}
            for command, level in command_permissions.items():
                if level not in commands_by_level:
                    commands_by_level[level] = []
                commands_by_level[level].append(command)
            
            # Show commands for each level
            level_order = ['perm1', 'perm2', 'perm3', 'perm4', 'perm5', 'perm6', 'perm7', 'perm8', 'perm9', 'owner', 'buyer', 'public', 'everyone']
            for level in level_order:
                if level in commands_by_level:
                    commands = commands_by_level[level]
                    embed.add_field(
                        name=f"{get_permission_level_name(level)} - Commandes",
                        value=f"`{', '.join(sorted(commands))}`",
                        inline=False
                    )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération des permissions: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="helpall")
    @has_permission()
    async def help_all_permissions(self, ctx):
        """Show all commands organized by permission levels"""
        try:
            command_permissions = await self.bot.db.get_all_command_permissions(ctx.guild.id)
            
            # If no permissions set, initialize defaults
            if not command_permissions:
                await self.bot.db.initialize_default_permissions(ctx.guild.id)
                command_permissions = await self.bot.db.get_all_command_permissions(ctx.guild.id)
            
            embed = discord.Embed(
                title="Toutes les Commandes par Niveau",
                description="Organisation hiérarchique des commandes",
                color=self.bot.config.embed_color
            )
            
            # Group commands by permission level
            commands_by_level = {}
            for command, level in command_permissions.items():
                if level not in commands_by_level:
                    commands_by_level[level] = []
                commands_by_level[level].append(command)
            
            # Show commands for each level with descriptions
            level_order = ['buyer', 'owner', 'perm9', 'perm8', 'perm7', 'perm6', 'perm5', 'perm4', 'perm3', 'perm2', 'perm1', 'public', 'everyone']
            for level in level_order:
                if level in commands_by_level:
                    commands = sorted(commands_by_level[level])
                    description = get_permission_description(level)
                    
                    embed.add_field(
                        name=f"{get_permission_level_name(level)}",
                        value=f"*{description}*\n`{', '.join(commands)}`",
                        inline=False
                    )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération des commandes: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="resetperms")
    @admin_only()
    async def reset_permissions(self, ctx):
        """Reset all permissions to default"""
        try:
            await self.bot.db.reset_permissions(ctx.guild.id)
            await self.bot.db.initialize_default_permissions(ctx.guild.id)
            
            await ctx.send("✅ Permissions remises par défaut.")
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "resetperms", 
                "Remise à zéro de toutes les permissions"
            )
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la remise à zéro : {str(e)}")
    
    @commands.command(name="clearperm")
    @admin_only()
    async def clear_permissions(self, ctx):
        """Clear all permission level assignments (alias for resetperms)"""
        await self.reset_permissions(ctx)
    
    @commands.command(name="setcooldown")
    @admin_only()
    async def set_cooldown(self, ctx, command_name: str, seconds: int):
        """Set cooldown for a command"""
        try:
            if seconds < 0:
                await ctx.send("❌ Le délai doit être un nombre positif.")
                return
            
            await self.bot.db.set_command_cooldown(ctx.guild.id, command_name.lower(), seconds)
            
            await ctx.send(f"✅ Délai de `{command_name}` défini à `{seconds}` secondes")
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "setcooldown", 
                f"Défini délai de {command_name} à {seconds} secondes"
            )
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la définition du délai: {str(e)}")
    
    @commands.command(name="settings")
    @has_permission()
    async def show_settings(self, ctx):
        """Show server settings"""
        try:
            prefix = await self.bot.db.get_guild_prefix(ctx.guild.id) or "+"
            
            embed = discord.Embed(
                title=f"Paramètres du Serveur - {ctx.guild.name}",
                color=self.bot.config.embed_color
            )
            
            embed.add_field(name="Préfixe", value=f"`{prefix}`", inline=True)
            
            # Get mute role
            mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if mute_role:
                embed.add_field(
                    name="Rôle Muet",
                    value=mute_role.mention,
                    inline=True
                )
            else:
                embed.add_field(
                    name="Rôle Muet",
                    value="Non configuré",
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération des paramètres: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="prefix")
    @admin_only()
    async def change_prefix(self, ctx, new_prefix: str):
        """Change the bot prefix for this server"""
        try:
            if len(new_prefix) > 5:
                await ctx.send("❌ Le préfixe doit faire 5 caractères ou moins.")
                return
            
            await self.bot.db.set_guild_prefix(ctx.guild.id, new_prefix)
            
            await ctx.send(f"✅ Nouveau préfixe: `{new_prefix}`")
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "prefix", 
                f"Préfixe changé vers {new_prefix}"
            )
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du changement de préfixe: {str(e)}")

async def setup(bot):
    await bot.add_cog(Administration(bot))