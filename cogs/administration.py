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
        """Set permission level to role/user or command to permission level
        Usage: 
        +set perm <niveau> <@role/@user> - Assigner niveau de permission
        +set <commande> <niveau> - Déplacer commande vers niveau
        """
        if perm_type.lower() == "perm":
            # +set perm <level> <@role/@user>
            try:
                level = int(level_or_command)
                if level < 1 or level > 9:
                    await ctx.send("❌ Le niveau de permission doit être entre 1 et 9")
                    return
                
                if not target:
                    await ctx.send("❌ Vous devez mentionner un rôle ou un utilisateur")
                    return
                
                # Parse target (role or user)
                if target.startswith('<@&') and target.endswith('>'):
                    # Role mention
                    role_id = int(target[3:-1])
                    role = ctx.guild.get_role(role_id)
                    if not role:
                        await ctx.send("❌ Rôle introuvable")
                        return
                    
                    await self.bot.db.set_permission_level(ctx.guild.id, level, role_id=role_id)
                    await ctx.send(f"✅ Rôle {role.mention} assigné au niveau de permission {level}")
                    
                elif target.startswith('<@') and target.endswith('>'):
                    # User mention
                    user_id = int(target[2:-1].replace('!', ''))
                    user = ctx.guild.get_member(user_id)
                    if not user:
                        await ctx.send("❌ Utilisateur introuvable")
                        return
                    
                    await self.bot.db.set_permission_level(ctx.guild.id, level, user_id=user_id)
                    await ctx.send(f"✅ Utilisateur {user.mention} assigné au niveau de permission {level}")
                    
                else:
                    await ctx.send("❌ Format invalide. Utilisez @role ou @user")
                    return
                
            except ValueError:
                await ctx.send("❌ Niveau de permission invalide")
                return
                
        else:
            # +set <command> <permission_level>
            command_name = perm_type.lower()
            permission_level = level_or_command.lower()
            
            # Validate permission level
            valid_levels = ['perm1', 'perm2', 'perm3', 'perm4', 'perm5', 'perm6', 'perm7', 'perm8', 'perm9', 'owner', 'buyer', 'public', 'everyone']
            if permission_level not in valid_levels:
                await ctx.send(f"❌ Niveau de permission invalide. Utilisez: {', '.join(valid_levels)}")
                return
            
            await self.bot.db.set_command_permission(ctx.guild.id, command_name, permission_level)
            await ctx.send(f"✅ Commande `{command_name}` déplacée vers `{get_permission_level_name(permission_level)}`")
    
    @commands.command(name="del")
    @admin_only()
    async def delete_permission(self, ctx, perm_type: str, level_or_command: str, target: str = None):
        """Remove permission level from role/user or reset command permission
        Usage:
        +del perm <niveau> <@role/@user> - Retirer niveau de permission
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
                
                # Parse target (role or user)
                if target.startswith('<@&') and target.endswith('>'):
                    # Role mention
                    role_id = int(target[3:-1])
                    role = ctx.guild.get_role(role_id)
                    if not role:
                        await ctx.send("❌ Rôle introuvable")
                        return
                    
                    await self.bot.db.remove_permission_level(ctx.guild.id, level, role_id=role_id)
                    await ctx.send(f"✅ Rôle {role.mention} retiré du niveau de permission {level}")
                    
                elif target.startswith('<@') and target.endswith('>'):
                    # User mention
                    user_id = int(target[2:-1].replace('!', ''))
                    user = ctx.guild.get_member(user_id)
                    if not user:
                        await ctx.send("❌ Utilisateur introuvable")
                        return
                    
                    await self.bot.db.remove_permission_level(ctx.guild.id, level, user_id=user_id)
                    await ctx.send(f"✅ Utilisateur {user.mention} retiré du niveau de permission {level}")
                    
                else:
                    await ctx.send("❌ Format invalide. Utilisez @role ou @user")
                    return
                
            except ValueError:
                await ctx.send("❌ Niveau de permission invalide")
                return
        else:
            await ctx.send("❌ Utilisez: `+del perm <niveau> <@role/@user>`")
    
    @commands.command(name="change")
    @admin_only()
    async def change_command_permission(self, ctx, command_name: str, permission_level: str):
        """Change command permission level
        Usage: +change <commande> <niveau>
        """
        command_name = command_name.lower()
        permission_level = permission_level.lower()
        
        # Validate permission level
        valid_levels = ['perm1', 'perm2', 'perm3', 'perm4', 'perm5', 'perm6', 'perm7', 'perm8', 'perm9', 'owner', 'buyer', 'public', 'everyone']
        if permission_level not in valid_levels:
            await ctx.send(f"❌ Niveau de permission invalide. Utilisez: {', '.join(valid_levels)}")
            return
        
        await self.bot.db.set_command_permission(ctx.guild.id, command_name, permission_level)
        await ctx.send(f"✅ Commande `{command_name}` changée vers `{get_permission_level_name(permission_level)}`")
    
    @commands.command(name="changeall")
    @admin_only()
    async def change_all_permissions(self, ctx, old_level: str, new_level: str):
        """Move all commands from one permission level to another
        Usage: +changeall <ancien_niveau> <nouveau_niveau>
        """
        old_level = old_level.lower()
        new_level = new_level.lower()
        
        # Validate permission levels
        valid_levels = ['perm1', 'perm2', 'perm3', 'perm4', 'perm5', 'perm6', 'perm7', 'perm8', 'perm9', 'owner', 'buyer', 'public', 'everyone']
        if old_level not in valid_levels or new_level not in valid_levels:
            await ctx.send(f"❌ Niveaux de permission invalides. Utilisez: {', '.join(valid_levels)}")
            return
        
        # Get all commands with old permission level
        all_perms = await self.bot.db.get_all_command_permissions(ctx.guild.id)
        commands_to_move = [cmd for cmd, level in all_perms.items() if level == old_level]
        
        if not commands_to_move:
            await ctx.send(f"❌ Aucune commande trouvée avec le niveau `{get_permission_level_name(old_level)}`")
            return
        
        # Move all commands
        for command_name in commands_to_move:
            await self.bot.db.set_command_permission(ctx.guild.id, command_name, new_level)
        
        await ctx.send(f"✅ {len(commands_to_move)} commandes déplacées de `{get_permission_level_name(old_level)}` vers `{get_permission_level_name(new_level)}`")
    
    @commands.command(name="perms")
    @has_permission()
    async def show_permissions(self, ctx):
        """Show all permission levels and command assignments for this server"""
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
            
            embed = discord.Embed(
                title="Permissions Reset",
                description="Toutes les permissions ont été remises par défaut.",
                color=self.bot.config.success_color
            )
            await ctx.send(embed=embed)
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "resetperms", 
                "Remise à zéro de toutes les permissions"
            )
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la remise à zéro des permissions: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
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
                embed = discord.Embed(
                    title="❌ Invalid Cooldown",
                    description="Le délai doit être un nombre positif.",
                    color=self.bot.config.error_color
                )
                await ctx.send(embed=embed)
                return
            
            await self.bot.db.set_command_cooldown(ctx.guild.id, command_name.lower(), seconds)
            
            embed = discord.Embed(
                title="Cooldown Set",
                description=f"Délai de `{command_name}` défini à `{seconds}` secondes",
                color=self.bot.config.success_color
            )
            await ctx.send(embed=embed)
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "setcooldown", 
                f"Défini délai de {command_name} à {seconds} secondes"
            )
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la définition du délai: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
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
                embed = discord.Embed(
                    title="❌ Invalid Prefix",
                    description="Le préfixe doit faire 5 caractères ou moins.",
                    color=self.bot.config.error_color
                )
                await ctx.send(embed=embed)
                return
            
            await self.bot.db.set_guild_prefix(ctx.guild.id, new_prefix)
            
            embed = discord.Embed(
                title="Préfixe Changé",
                description=f"Nouveau préfixe: `{new_prefix}`",
                color=self.bot.config.success_color
            )
            await ctx.send(embed=embed)
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "prefix", 
                f"Préfixe changé vers {new_prefix}"
            )
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors du changement de préfixe: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Administration(bot))