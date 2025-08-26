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
            raise PermissionError("Vous n'avez pas la permission d'utiliser cette commande.")
        
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
        
        raise PermissionError("Vous devez avoir les permissions d'administrateur pour utiliser cette commande.")
    
    return commands.check(predicate)

def owner_only():
    """Decorator for owner-only commands"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        
        # Check if user is owner
        is_owner = await ctx.bot.is_owner_user(ctx.author.id)
        if not is_owner:
            raise PermissionError("Seuls les owners peuvent utiliser cette commande.")
        
        return True
    
    return commands.check(predicate)

def buyer_only():
    """Decorator for buyer-only commands"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        
        # Check if user is buyer
        is_buyer = await ctx.bot.is_buyer_user(ctx.author.id)
        if not is_buyer:
            raise PermissionError("Seul le buyer peut utiliser cette commande.")
        
        return True
    
    return commands.check(predicate)

def public_only():
    """Decorator for public commands (everyone can use)"""
    async def predicate(ctx):
        return True
    
    return commands.check(predicate)

def get_permission_level_name(level):
    """Get human readable permission level name"""
    level_names = {
        'perm1': 'Permission 1',
        'perm2': 'Permission 2', 
        'perm3': 'Permission 3',
        'perm4': 'Permission 4',
        'perm5': 'Permission 5',
        'perm6': 'Permission 6',
        'perm7': 'Permission 7',
        'perm8': 'Permission 8',
        'perm9': 'Permission 9',
        'owner': 'Owner',
        'buyer': 'Buyer',
        'public': 'Public',
        'everyone': 'Tout le monde'
    }
    return level_names.get(level, level)

def get_permission_description(level):
    """Get description for permission level"""
    descriptions = {
        'perm1': 'Modération basique (clear, warn, mute)',
        'perm2': 'Modération complète (kick, ban, etc.)',
        'perm3': 'Administration et gestion',
        'perm4': 'Permission niveau 4',
        'perm5': 'Permission niveau 5',
        'perm6': 'Permission niveau 6',
        'perm7': 'Permission niveau 7',
        'perm8': 'Permission niveau 8',
        'perm9': 'Permission niveau 9',
        'owner': 'Commandes avancées (owners)',
        'buyer': 'Gestion du bot (buyer)',
        'public': 'Accessible à tous',
        'everyone': 'Accessible partout'
    }
    return descriptions.get(level, 'Permission personnalisée')