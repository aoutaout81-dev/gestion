import discord
from discord.ext import commands
import asyncio
import logging
from database import Database
from config import Config

class CrowBot(commands.Bot):
    def __init__(self):
        # Initialize with default prefix, will be updated from database
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None
        )
        
        self.db = Database()
        self.config = Config()
        self.logger = logging.getLogger('CrowBot')
        
    async def get_prefix(self, message):
        """Get the prefix for a guild"""
        if message.guild is None:
            return self.config.default_prefix
        
        prefix = await self.db.get_guild_prefix(message.guild.id)
        return prefix or self.config.default_prefix
    
    async def setup_hook(self):
        await self.db.initialize()
        cogs = [
            'cogs.administration',
            'cogs.moderation',
            'cogs.roles',
            'cogs.help_interactive',
            'cogs.triggers',
            'cogs.ownership'
        ]

        for cog in cogs:
            if cog not in self.extensions:  # ← empêche le rechargement
                try:
                    await self.load_extension(cog)
                    self.logger.info(f"Loaded cog: {cog}")
                except Exception as e:
                    self.logger.error(f"Failed to load cog {cog}: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        self.logger.info(f'{self.user.name if self.user else "Bot"} has connected to Discord!')
        self.logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for infractions | +help"
            )
        )
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild"""
        self.logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        await self.db.setup_guild(guild.id)
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.CheckFailure):
            # Don't send error message for check failures, already handled by custom checks
            return
        
        if isinstance(error, commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions)
            await ctx.send(f"❌ **Permissions manquantes :** `{perms}`\n💡 Vous devez avoir ces permissions pour utiliser cette commande.")
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ **Argument manquant :** `{error.param.name}`\n💡 Utilisez `+help` pour voir la syntaxe correcte.")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ **Argument invalide :** {error}\n💡 Vérifiez la syntaxe de votre commande.")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"❌ **Commande en cooldown**\n⏰ Réessayez dans {error.retry_after:.1f} secondes.")
            return
        
        # Handle custom converter errors
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(f"❌ **Membre introuvable :** {error}")
            return
        
        if isinstance(error, commands.RoleNotFound):
            await ctx.send(f"❌ **Rôle introuvable :** {error}")
            return
        
        if isinstance(error, commands.UserNotFound):
            await ctx.send(f"❌ **Utilisateur introuvable :** {error}")
            return
        
        # Enhanced error logging with more details
        self.logger.error(f"Unhandled error in command '{ctx.command}' by {ctx.author} ({ctx.author.id}) in {ctx.guild.name if ctx.guild else 'DM'}: {error}")
        await ctx.send(f"❌ **Erreur inattendue**\n🔧 Détails : `{str(error)[:100]}...`\n💡 Contactez l'administrateur si le problème persiste.")
    
    async def check_permissions(self, ctx, command_name):
        """Check if user has permission to use a command"""
        # Bot owner always has permission
        if await self.is_owner(ctx.author):
            return True
        
        # Server owner always has permission
        if ctx.author == ctx.guild.owner:
            return True
        
        # Check custom permissions
        user_roles = [role.id for role in ctx.author.roles]
        allowed_roles = await self.db.get_command_permissions(ctx.guild.id, command_name)
        
        if allowed_roles:
            return any(role_id in allowed_roles for role_id in user_roles)
        
        # Default: only administrators can use moderation commands
        moderation_commands = [
            'ban', 'unban', 'kick', 'mute', 'unmute', 'warn', 'clear', 
            'lock', 'unlock', 'setperm', 'unsetperm', 'resetperms'
        ]
        
        if command_name in moderation_commands:
            return ctx.author.guild_permissions.administrator
        
        return True
    
    async def check_cooldown(self, ctx, command_name):
        """Check if command is on cooldown for user"""
        cooldown_time = await self.db.get_command_cooldown(ctx.guild.id, command_name)
        if not cooldown_time:
            return True
        
        last_used = await self.db.get_last_command_use(ctx.guild.id, ctx.author.id, command_name)
        if not last_used:
            await self.db.update_last_command_use(ctx.guild.id, ctx.author.id, command_name)
            return True
        
        import time
        if time.time() - last_used < cooldown_time:
            return False
        
        await self.db.update_last_command_use(ctx.guild.id, ctx.author.id, command_name)
        return True
