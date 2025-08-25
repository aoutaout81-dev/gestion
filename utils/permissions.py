import discord
from discord.ext import commands

class PermissionError(commands.CheckFailure):
    """Custom exception for permission errors"""
    pass

def has_permission():
    """Decorator to check if user has permission to use command"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        
        # Check if user has permission
        has_perm = await ctx.bot.check_permissions(ctx, ctx.command.name)
        if not has_perm:
            raise PermissionError("You don't have permission to use this command.")
        
        # Check cooldown
        on_cooldown = not await ctx.bot.check_cooldown(ctx, ctx.command.name)
        if on_cooldown:
            cooldown_time = await ctx.bot.db.get_command_cooldown(ctx.guild.id, ctx.command.name)
            from discord.ext.commands import Cooldown
            cooldown = Cooldown(1, cooldown_time or 60)
            raise commands.CommandOnCooldown(cooldown, cooldown_time or 60, commands.BucketType.user)
        
        return True
    
    return commands.check(predicate)

def admin_only():
    """Decorator for admin-only commands"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        
        # Bot owner can always use admin commands
        if await ctx.bot.is_owner(ctx.author):
            return True
        
        # Guild owner can always use admin commands
        if ctx.author == ctx.guild.owner:
            return True
        
        # Check if user has administrator permission
        if ctx.author.guild_permissions.administrator:
            return True
        
        raise PermissionError("You need administrator permissions to use this command.")
    
    return commands.check(predicate)
