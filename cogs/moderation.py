import discord
from discord.ext import commands
import asyncio
import time
from typing import Optional
from utils.permissions import has_permission
from utils.helpers import parse_time, format_time, get_or_fetch_user, get_mute_role
from utils.converters import MemberConverter, UserConverter

class Moderation(commands.Cog):
    """Moderation commands for managing users and maintaining order"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ban")
    @has_permission()
    async def ban_user(self, ctx, member: MemberConverter, *, reason: str = "Aucune raison fournie"):
        """Ban a member from the server"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous ne pouvez pas vous bannir vous-même.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous ne pouvez pas bannir quelqu'un avec un rôle supérieur ou égal.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Send DM to user before banning
            try:
                dm_embed = discord.Embed(
                    title="🔨 Vous avez été banni",
                    description=f"Vous avez été banni de **{ctx.guild.name}**",
                    color=self.bot.config.error_color
                )
                dm_embed.add_field(name="Raison", value=reason, inline=False)
                dm_embed.add_field(name="Modérateur", value=str(ctx.author), inline=False)
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            await member.ban(reason=f"{reason} | Moderator: {ctx.author}")
            
            # Log the infraction
            await self.bot.db.add_infraction(
                ctx.guild.id, member.id, ctx.author.id, "ban", reason
            )
            
            # Log moderation action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, member.id, ctx.author.id, "ban", reason
            )
            
            embed = discord.Embed(
                title="🔨 Utilisateur banni",
                description=f"**{member}** a été banni.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to ban this user.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to ban user: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="unban")
    @has_permission()
    async def unban_user(self, ctx, user: UserConverter):
        """Unban a user by their ID"""
        try:
            await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author}")
            
            # Log moderation action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, user.id, ctx.author.id, "unban"
            )
            
            embed = discord.Embed(
                title="✅ Utilisateur débanni",
                description=f"**{user}** a été débanni.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Utilisateur introuvable ou non banni.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to unban user: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="kick")
    @has_permission()
    async def kick_user(self, ctx, member: MemberConverter, *, reason: str = "Aucune raison fournie"):
        """Kick a member from the server"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot kick yourself.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot kick someone with a higher or equal role.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Send DM to user before kicking
            try:
                dm_embed = discord.Embed(
                    title="👢 You have been kicked",
                    description=f"You have been kicked from **{ctx.guild.name}**",
                    color=self.bot.config.warning_color
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=False)
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            await member.kick(reason=f"{reason} | Moderator: {ctx.author}")
            
            # Log the infraction
            await self.bot.db.add_infraction(
                ctx.guild.id, member.id, ctx.author.id, "kick", reason
            )
            
            # Log moderation action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, member.id, ctx.author.id, "kick", reason
            )
            
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"**{member}** has been kicked.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to kick this user.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to kick user: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="mute")
    @has_permission()
    async def mute_user(self, ctx, member: MemberConverter, duration: Optional[str] = None, *, reason: str = "Aucune raison fournie"):
        """Mute a member (prevent them from sending messages)"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot mute yourself.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot mute someone with a higher or equal role.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        # Parse duration
        duration_seconds = None
        muted_until = None
        if duration:
            duration_seconds = parse_time(duration)
            if duration_seconds:
                muted_until = time.time() + duration_seconds
        
        try:
            # Get or create mute role
            mute_role = await get_mute_role(ctx.guild)
            if not mute_role:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Failed to create mute role. Check bot permissions.",
                    color=self.bot.config.error_color
                )
                await ctx.send(embed=embed)
                return
            
            # Add mute role to member
            await member.add_roles(mute_role, reason=f"Muted by {ctx.author}: {reason}")
            
            # Add to database
            await self.bot.db.add_mute(
                ctx.guild.id, member.id, muted_until, reason, ctx.author.id
            )
            
            # Log the infraction
            await self.bot.db.add_infraction(
                ctx.guild.id, member.id, ctx.author.id, "mute", reason, duration_seconds
            )
            
            # Log moderation action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, member.id, ctx.author.id, "mute", reason,
                f"Duration: {duration if duration else 'Permanent'}"
            )
            
            embed = discord.Embed(
                title="🔇 User Muted",
                description=f"**{member}** has been muted.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(
                name="Duration", 
                value=format_time(duration_seconds) if duration_seconds else "Permanent", 
                inline=False
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
            # Schedule unmute if duration is set
            if duration_seconds:
                await asyncio.sleep(duration_seconds)
                try:
                    if await self.bot.db.is_user_muted(ctx.guild.id, member.id):
                        await member.remove_roles(mute_role, reason="Mute duration expired")
                        await self.bot.db.remove_mute(ctx.guild.id, member.id)
                except:
                    pass  # User might have left the server
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to mute this user.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to mute user: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="unmute")
    @has_permission()
    async def unmute_user(self, ctx, member: MemberConverter):
        """Unmute a member"""
        try:
            # Check if user is actually muted
            is_muted = await self.bot.db.is_user_muted(ctx.guild.id, member.id)
            if not is_muted:
                embed = discord.Embed(
                    title="❌ Error",
                    description="This user is not muted.",
                    color=self.bot.config.error_color
                )
                await ctx.send(embed=embed)
                return
            
            # Get mute role
            mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if mute_role and mute_role in member.roles:
                await member.remove_roles(mute_role, reason=f"Unmuted by {ctx.author}")
            
            # Remove from database
            await self.bot.db.remove_mute(ctx.guild.id, member.id)
            
            # Log moderation action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, member.id, ctx.author.id, "unmute"
            )
            
            embed = discord.Embed(
                title="🔊 User Unmuted",
                description=f"**{member}** has been unmuted.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to unmute user: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="mutelist")
    @has_permission()
    async def mute_list(self, ctx):
        """Show list of currently muted users"""
        try:
            muted_users = await self.bot.db.get_muted_users(ctx.guild.id)
            
            if not muted_users:
                embed = discord.Embed(
                    title="🔇 Muted Users",
                    description="No users are currently muted.",
                    color=self.bot.config.embed_color
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🔇 Muted Users",
                color=self.bot.config.embed_color
            )
            
            for mute_data in muted_users[:10]:  # Limit to 10 users
                user = await get_or_fetch_user(self.bot, mute_data['user_id'])
                user_name = str(user) if user else f"Unknown User ({mute_data['user_id']})"
                
                duration = "Permanent"
                if mute_data['muted_until']:
                    remaining = float(mute_data['muted_until']) - time.time()
                    if remaining > 0:
                        duration = f"Expires in {format_time(int(remaining))}"
                    else:
                        duration = "Expired"
                
                embed.add_field(
                    name=user_name,
                    value=f"**Reason:** {mute_data['reason']}\n**Duration:** {duration}",
                    inline=False
                )
            
            if len(muted_users) > 10:
                embed.set_footer(text=f"Showing 10 of {len(muted_users)} muted users")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to retrieve muted users: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="warn")
    @has_permission()
    async def warn_user(self, ctx, member: MemberConverter, *, reason: str = "Aucune raison fournie"):
        """Give a warning to a member"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot warn yourself.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Add warning to database
            await self.bot.db.add_infraction(
                ctx.guild.id, member.id, ctx.author.id, "warn", reason
            )
            
            # Log moderation action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, member.id, ctx.author.id, "warn", reason
            )
            
            # Send DM to user
            try:
                dm_embed = discord.Embed(
                    title="⚠️ You have received a warning",
                    description=f"You have been warned in **{ctx.guild.name}**",
                    color=self.bot.config.warning_color
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=False)
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            embed = discord.Embed(
                title="⚠️ User Warned",
                description=f"**{member}** has been warned.",
                color=self.bot.config.warning_color
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to warn user: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="infractions")
    @has_permission()
    async def show_infractions(self, ctx, member: MemberConverter):
        """Show infractions for a member"""
        try:
            infractions = await self.bot.db.get_user_infractions(ctx.guild.id, member.id)
            
            if not infractions:
                embed = discord.Embed(
                    title="📋 User Infractions",
                    description=f"**{member}** has no infractions.",
                    color=self.bot.config.embed_color
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📋 User Infractions",
                description=f"Infractions for **{member}**",
                color=self.bot.config.embed_color
            )
            
            for i, infraction in enumerate(infractions[:10], 1):  # Limit to 10 infractions
                moderator = await get_or_fetch_user(self.bot, infraction['moderator_id'])
                moderator_name = str(moderator) if moderator else "Unknown Moderator"
                
                value = f"**Reason:** {infraction['reason'] or 'No reason'}\n"
                value += f"**Moderator:** {moderator_name}\n"
                value += f"**Date:** {infraction['created_at']}"
                
                if infraction['duration']:
                    value += f"\n**Duration:** {format_time(infraction['duration'])}"
                
                embed.add_field(
                    name=f"{i}. {infraction['type'].title()}",
                    value=value,
                    inline=False
                )
            
            if len(infractions) > 10:
                embed.set_footer(text=f"Showing 10 of {len(infractions)} infractions")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to retrieve infractions: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="clear")
    @has_permission()
    async def clear_messages(self, ctx, amount: int):
        """Clear a specified number of messages"""
        if amount <= 0 or amount > 100:
            embed = discord.Embed(
                title="❌ Error",
                description="Amount must be between 1 and 100.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
            
            # Log moderation action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "clear", 
                f"Cleared {len(deleted) - 1} messages in {ctx.channel.name}"
            )
            
            embed = discord.Embed(
                title="🧹 Messages Cleared",
                description=f"Cleared {len(deleted) - 1} messages.",
                color=self.bot.config.success_color
            )
            
            # Send confirmation and delete after 5 seconds
            msg = await ctx.send(embed=embed, delete_after=5)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to delete messages.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to clear messages: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="lock")
    @has_permission()
    async def lock_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Lock a channel (prevent @everyone from sending messages)"""
        channel = channel or ctx.channel
        
        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            
            # Log moderation action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "lock", f"Locked channel {channel.name}"
            )
            
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"{channel.mention} has been locked.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to manage this channel.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to lock channel: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="unlock")
    @has_permission()
    async def unlock_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Unlock a channel (allow @everyone to send messages)"""
        channel = channel or ctx.channel
        
        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = None  # Reset to default
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            
            # Log moderation action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "unlock", f"Unlocked channel {channel.name}"
            )
            
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description=f"{channel.mention} has been unlocked.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to manage this channel.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to unlock channel: {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
