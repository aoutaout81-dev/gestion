import discord
from discord.ext import commands
from typing import Union

class MemberConverter(commands.MemberConverter):
    """Custom member converter that accepts names, mentions, and IDs"""
    
    async def convert(self, ctx, argument: str) -> discord.Member:
        # Try the default converter first (mentions and IDs)
        try:
            return await super().convert(ctx, argument)
        except commands.MemberNotFound:
            pass
        
        # Search by username or display name
        argument = argument.lower()
        for member in ctx.guild.members:
            if (member.name.lower() == argument or 
                member.display_name.lower() == argument or
                argument in member.name.lower() or
                argument in member.display_name.lower()):
                return member
        
        raise commands.MemberNotFound(f"Membre '{argument}' introuvable.")

class RoleConverter(commands.RoleConverter):
    """Custom role converter that accepts names, mentions, and IDs"""
    
    async def convert(self, ctx, argument: str) -> discord.Role:
        # Try the default converter first (mentions and IDs)
        try:
            return await super().convert(ctx, argument)
        except commands.RoleNotFound:
            pass
        
        # Search by role name
        argument = argument.lower()
        for role in ctx.guild.roles:
            if (role.name.lower() == argument or
                argument in role.name.lower()):
                return role
        
        raise commands.RoleNotFound(f"Rôle '{argument}' introuvable.")

class UserConverter(commands.UserConverter):
    """Custom user converter for unban command"""
    
    async def convert(self, ctx, argument: str) -> discord.User:
        # Try to convert as user ID first
        try:
            user_id = int(argument)
            user = await ctx.bot.fetch_user(user_id)
            return user
        except (ValueError, discord.NotFound):
            pass
        
        # Try the default converter
        try:
            return await super().convert(ctx, argument)
        except commands.UserNotFound:
            pass
        
        raise commands.UserNotFound(f"Utilisateur '{argument}' introuvable.")