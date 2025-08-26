import discord
from discord.ext import commands
from utils.permissions import has_permission, admin_only
from utils.helpers import parse_time, format_time
from utils.converters import RoleConverter

class Administration(commands.Cog):
    """Administration and configuration commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="setperm")
    @admin_only()
    async def set_permission(self, ctx, command_name: str, role: RoleConverter):
        """Set permission for a command to a role"""
        try:
            await self.bot.db.set_command_permission(ctx.guild.id, command_name.lower(), role.id)
            
            await ctx.send(f"✅ Rôle {role.mention} peut utiliser `{command_name}`.")
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "setperm", 
                f"Granted {role.name} permission for {command_name}"
            )
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to set permission: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="unsetperm")
    @admin_only()
    async def unset_permission(self, ctx, command_name: str, role: RoleConverter):
        """Remove permission for a command from a role"""
        try:
            await self.bot.db.remove_command_permission(ctx.guild.id, command_name.lower(), role.id)
            
            await ctx.send(f"✅ Rôle {role.mention} ne peut plus utiliser `{command_name}`.")
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "unsetperm", 
                f"Removed {role.name} permission for {command_name}"
            )
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to remove permission: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="perms")
    @has_permission()
    async def show_permissions(self, ctx):
        """Show all command permissions for this server"""
        try:
            permissions = await self.bot.db.get_all_permissions(ctx.guild.id)
            
            embed = discord.Embed(
                title="📋 Permissions du Serveur",
                description="Configuration des permissions par commande",
                color=self.bot.config.embed_color
            )
            
            if not permissions:
                embed.add_field(
                    name="ℹ️ Aucune permission personnalisée",
                    value="Toutes les commandes utilisent les permissions par défaut.\n\n" +
                          "**Permissions par défaut :**\n" +
                          "🔰 **Modération :** ban, kick, warn, mute, clear\n" +
                          "⚙️ **Administration :** setperm, resetperms, settings\n" +
                          "👑 **Ownership :** massrole, say, dm, laisse\n" +
                          "💎 **Buyer :** owner, buyer\n" +
                          "📖 **Public :** help, ping",
                    inline=False
                )
            else:
                # Organize commands by category
                moderation_cmds = []
                administration_cmds = []
                ownership_cmds = []
                other_cmds = []
                
                for command_name, role_ids in permissions.items():
                    roles = []
                    for role_id in role_ids:
                        role = ctx.guild.get_role(role_id)
                        if role:
                            roles.append(role.mention)
                    
                    if roles:
                        cmd_info = f"`{command_name}` → {', '.join(roles)}"
                        
                        if command_name in ['ban', 'kick', 'warn', 'mute', 'unmute', 'clear', 'delwarn']:
                            moderation_cmds.append(cmd_info)
                        elif command_name in ['setperm', 'unsetperm', 'resetperms', 'settings', 'cooldown']:
                            administration_cmds.append(cmd_info)
                        elif command_name in ['massrole', 'say', 'dm', 'laisse', 'unlaisse', 'wl', 'unwl', 'blrank']:
                            ownership_cmds.append(cmd_info)
                        else:
                            other_cmds.append(cmd_info)
                
                if moderation_cmds:
                    embed.add_field(
                        name="🔰 Modération",
                        value="\n".join(moderation_cmds),
                        inline=False
                    )
                
                if administration_cmds:
                    embed.add_field(
                        name="⚙️ Administration",
                        value="\n".join(administration_cmds),
                        inline=False
                    )
                
                if ownership_cmds:
                    embed.add_field(
                        name="👑 Ownership",
                        value="\n".join(ownership_cmds),
                        inline=False
                    )
                
                if other_cmds:
                    embed.add_field(
                        name="📝 Autres",
                        value="\n".join(other_cmds),
                        inline=False
                    )
            
            embed.set_footer(text="💡 Utilisez +setperm <commande> <rôle> pour modifier les permissions")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to retrieve permissions: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="resetperms")
    @admin_only()
    async def reset_permissions(self, ctx):
        """Reset all command permissions to default"""
        try:
            await self.bot.db.reset_permissions(ctx.guild.id)
            
            embed = discord.Embed(
                title="✅ Permissions Reset",
                description="All command permissions have been reset to default.",
                color=self.bot.config.success_color
            )
            await ctx.send(embed=embed)
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "resetperms", 
                "Reset all command permissions"
            )
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to reset permissions: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="cooldown")
    @admin_only()
    async def set_cooldown(self, ctx, command_name: str, seconds: int):
        """Set cooldown for a command"""
        if seconds < 0:
            embed = discord.Embed(
                title="❌ Invalid Cooldown",
                description="Cooldown must be a positive number.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await self.bot.db.set_command_cooldown(ctx.guild.id, command_name.lower(), seconds)
            
            embed = discord.Embed(
                title="✅ Cooldown Set",
                description=f"Command `{command_name}` now has a {seconds} second cooldown.",
                color=self.bot.config.success_color
            )
            await ctx.send(embed=embed)
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "cooldown", 
                f"Set {command_name} cooldown to {seconds} seconds"
            )
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to set cooldown: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="settings")
    @has_permission()
    async def show_settings(self, ctx):
        """Show current bot settings for this server"""
        try:
            prefix = await self.bot.db.get_guild_prefix(ctx.guild.id) or self.bot.config.default_prefix
            
            embed = discord.Embed(
                title="⚙️ Server Settings",
                color=self.bot.config.embed_color
            )
            
            embed.add_field(
                name="Prefix",
                value=f"`{prefix}`",
                inline=True
            )
            
            embed.add_field(
                name="Guild ID",
                value=str(ctx.guild.id),
                inline=True
            )
            
            embed.add_field(
                name="Members",
                value=str(ctx.guild.member_count),
                inline=True
            )
            
            # Check if mute role exists
            mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
            embed.add_field(
                name="Mute Role",
                value=mute_role.mention if mute_role else "Not created",
                inline=True
            )
            
            embed.set_footer(text=f"Bot ID: {self.bot.user.id}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to retrieve settings: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="prefix")
    @admin_only()
    async def set_prefix(self, ctx, new_prefix: str):
        """Change the bot prefix for this server"""
        if len(new_prefix) > 5:
            embed = discord.Embed(
                title="❌ Invalid Prefix",
                description="Prefix must be 5 characters or less.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await self.bot.db.set_guild_prefix(ctx.guild.id, new_prefix)
            
            embed = discord.Embed(
                title="✅ Prefix Changed",
                description=f"Bot prefix has been changed to `{new_prefix}`",
                color=self.bot.config.success_color
            )
            await ctx.send(embed=embed)
            
            # Log the action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "prefix", 
                f"Changed prefix to {new_prefix}"
            )
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to change prefix: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Administration(bot))
