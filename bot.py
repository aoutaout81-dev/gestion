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
        """Setup hook called when the bot is ready"""
        await self.db.initialize()
        
        # Load cogs
        cogs = [
            'cogs.administration',
            'cogs.moderation',
            'cogs.help'
        ]
        
        for cog in cogs:
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
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Argument requis manquant : `{error.param.name}`")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Argument invalide : {error}")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"❌ Commande en cooldown. Réessayez dans {error.retry_after:.2f} secondes.")
            return
        
        # Handle custom converter errors
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(f"❌ {error}")
            return
        
        if isinstance(error, commands.RoleNotFound):
            await ctx.send(f"❌ {error}")
            return
        
        if isinstance(error, commands.UserNotFound):
            await ctx.send(f"❌ {error}")
            return
        
        self.logger.error(f"Unhandled error in command {ctx.command}: {error}")
        await ctx.send("❌ Une erreur inattendue s'est produite lors du traitement de la commande.")
    
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
