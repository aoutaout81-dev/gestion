import re
import time
from typing import Optional

def parse_time(time_str: str) -> Optional[int]:
    """Parse time string like '1h30m' into seconds"""
    if not time_str:
        return None
    
    time_regex = re.compile(r'(\d+)([smhdw])')
    matches = time_regex.findall(time_str.lower())
    
    if not matches:
        return None
    
    total_seconds = 0
    time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
    
    for amount, unit in matches:
        total_seconds += int(amount) * time_units.get(unit, 0)
    
    return total_seconds

def format_time(seconds: int) -> str:
    """Format seconds into human readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

def format_timestamp(timestamp: float) -> str:
    """Format timestamp into readable date"""
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

async def get_or_fetch_user(bot, user_id: int):
    """Get user from cache or fetch from API"""
    user = bot.get_user(user_id)
    if user:
        return user
    
    try:
        user = await bot.fetch_user(user_id)
        return user
    except:
        return None

async def get_mute_role(guild, create_if_missing=True):
    """Get or create mute role for the guild"""
    import discord
    
    # Look for existing mute role
    mute_role = discord.utils.get(guild.roles, name="Muted")
    
    if mute_role:
        return mute_role
    
    if not create_if_missing:
        return None
    
    # Create mute role
    try:
        mute_role = await guild.create_role(
            name="Muted",
            color=discord.Color.dark_grey(),
            reason="Auto-created mute role"
        )
        
        # Set permissions for mute role in all channels
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                await channel.set_permissions(
                    mute_role,
                    send_messages=False,
                    add_reactions=False,
                    speak=False
                )
            elif isinstance(channel, discord.VoiceChannel):
                await channel.set_permissions(
                    mute_role,
                    speak=False,
                    connect=False
                )
        
        return mute_role
    except discord.Forbidden:
        return None
