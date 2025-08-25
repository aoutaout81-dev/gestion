import discord
from discord.ext import commands
from typing import Optional
from utils.converters import MemberConverter, UserConverter

def is_owner_or_buyer():
    """Check if user is owner or buyer"""
    async def predicate(ctx):
        buyer = await ctx.bot.db.get_buyer(ctx.guild.id)
        is_owner = await ctx.bot.db.is_owner(ctx.guild.id, ctx.author.id)
        return ctx.author.id == buyer or is_owner
    
    return commands.check(predicate)

def is_buyer_only():
    """Check if user is buyer only"""
    async def predicate(ctx):
        buyer = await ctx.bot.db.get_buyer(ctx.guild.id)
        return ctx.author.id == buyer
    
    return commands.check(predicate)

class Ownership(commands.Cog):
    """Commandes de gestion de propriété et d'ownership"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Monitor nickname changes for leashed users"""
        if before.nick != after.nick:
            leash_info = await self.bot.db.get_leash_info(after.guild.id, after.id)
            if leash_info:
                # Get owner info
                owner = after.guild.get_member(leash_info['owner_id'])
                if owner:
                    leash_nick = f"🐶🦮 de {owner.display_name}"
                    if after.nick != leash_nick:
                        try:
                            await after.edit(nick=leash_nick, reason="Leash system - nickname protected")
                        except discord.Forbidden:
                            pass
    
    @commands.command(name="massrole")
    @is_owner_or_buyer()
    async def mass_role(self, ctx, role: discord.Role):
        """Donne un rôle à tous les utilisateurs humains"""
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Vous ne pouvez pas gérer un rôle supérieur au vôtre.")
        
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Je ne peux pas gérer ce rôle car il est supérieur au mien.")
        
        humans = [member for member in ctx.guild.members if not member.bot and role not in member.roles]
        
        if not humans:
            return await ctx.send(f"❌ Aucun utilisateur humain à ajouter au rôle {role.mention}.")
        
        success_count = 0
        for member in humans:
            try:
                await member.add_roles(role, reason=f"Massrole par {ctx.author}")
                success_count += 1
            except:
                continue
        
        await ctx.send(f"✅ Rôle {role.mention} ajouté à {success_count}/{len(humans)} utilisateurs.")
    
    @commands.command(name="say")
    @is_owner_or_buyer()
    async def say(self, ctx, *, message: str):
        """Fait parler le bot de manière anonyme"""
        await ctx.message.delete()
        await ctx.send(message)
    
    @commands.command(name="dm")
    @is_owner_or_buyer()
    async def dm_user(self, ctx, user: UserConverter, *, message: str):
        """Envoie un message privé via le bot"""
        try:
            await user.send(message)
            await ctx.send("✅ Message privé envoyé.")
        except discord.Forbidden:
            await ctx.send("❌ Impossible d'envoyer un message privé à cet utilisateur.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {str(e)}")
    
    @commands.command(name="laisse")
    @is_owner_or_buyer()
    async def leash_user(self, ctx, member: MemberConverter):
        """Met un membre en laisse"""
        if member == ctx.author:
            return await ctx.send("❌ Vous ne pouvez pas vous mettre en laisse.")
        
        if member.bot:
            return await ctx.send("❌ Impossible de mettre un bot en laisse.")
        
        # Check if already leashed
        if await self.bot.db.is_leashed(ctx.guild.id, member.id):
            return await ctx.send("❌ Ce membre est déjà en laisse.")
        
        original_nick = member.nick or member.name
        leash_nick = f"🐶🦮 de {ctx.author.display_name}"
        
        try:
            await member.edit(nick=leash_nick, reason=f"Leash par {ctx.author}")
            await self.bot.db.add_leash(ctx.guild.id, member.id, ctx.author.id, original_nick)
            await ctx.send(f"🦮 {member.mention} est maintenant en laisse.")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de modifier ce pseudo.")
    
    @commands.command(name="unlaisse")
    @is_owner_or_buyer()
    async def unleash_user(self, ctx, member: MemberConverter):
        """Retire un membre de la laisse"""
        leash_info = await self.bot.db.get_leash_info(ctx.guild.id, member.id)
        if not leash_info:
            return await ctx.send("❌ Ce membre n'est pas en laisse.")
        
        try:
            await member.edit(nick=leash_info['original_nick'], reason=f"Unleash par {ctx.author}")
            await self.bot.db.remove_leash(ctx.guild.id, member.id)
            await ctx.send(f"❌ {member.mention} n'est plus en laisse.")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de modifier ce pseudo.")
    
    @commands.command(name="owner")
    @is_buyer_only()
    async def add_owner(self, ctx, member: MemberConverter):
        """Ajouter un owner"""
        if member.bot:
            return await ctx.send("❌ Impossible d'ajouter un bot comme owner.")
        
        if await self.bot.db.is_owner(ctx.guild.id, member.id):
            return await ctx.send("❌ Ce membre est déjà owner.")
        
        buyer = await self.bot.db.get_buyer(ctx.guild.id)
        if member.id == buyer:
            return await ctx.send("❌ Ce membre est déjà le buyer.")
        
        await self.bot.db.add_owner(ctx.guild.id, member.id, ctx.author.id)
        await ctx.send(f"✅ {member.mention} a été promu owner.")
    
    @commands.command(name="unowner")
    @is_buyer_only()
    async def remove_owner(self, ctx, member: MemberConverter):
        """Retirer un owner"""
        if not await self.bot.db.is_owner(ctx.guild.id, member.id):
            return await ctx.send("❌ Ce membre n'est pas owner.")
        
        await self.bot.db.remove_owner(ctx.guild.id, member.id)
        await ctx.send(f"❌ {member.mention} n'est plus owner.")
    
    @commands.command(name="buyer")
    @is_buyer_only()
    async def transfer_buyer(self, ctx, member: MemberConverter, code: str):
        """Transférer la propriété du bot"""
        if member.bot:
            return await ctx.send("❌ Impossible de transférer à un bot.")
        
        if not await self.bot.db.verify_recovery_code(ctx.guild.id, code):
            return await ctx.send("❌ Code de récupération invalide.")
        
        # Generate new recovery code
        new_code = await self.bot.db.set_buyer(ctx.guild.id, member.id)
        
        # Remove from owners if they were one
        await self.bot.db.remove_owner(ctx.guild.id, member.id)
        
        await ctx.send(f"✅ Propriété transférée à {member.mention}.")
        
        try:
            await member.send(f"🔑 Vous êtes maintenant le buyer du bot sur **{ctx.guild.name}**.\nNouveau code de récupération : `{new_code}`")
        except:
            pass
    
    @commands.command(name="wl")
    @is_owner_or_buyer()
    async def whitelist_add(self, ctx, member: MemberConverter):
        """Ajouter en whitelist"""
        if await self.bot.db.is_whitelisted(ctx.guild.id, member.id):
            return await ctx.send("❌ Ce membre est déjà en whitelist.")
        
        await self.bot.db.add_whitelist(ctx.guild.id, member.id, ctx.author.id)
        await ctx.send(f"✅ {member.mention} ajouté à la whitelist.")
    
    @commands.command(name="unwl")
    @is_owner_or_buyer()
    async def whitelist_remove(self, ctx, member: MemberConverter):
        """Retirer de la whitelist"""
        if not await self.bot.db.is_whitelisted(ctx.guild.id, member.id):
            return await ctx.send("❌ Ce membre n'est pas en whitelist.")
        
        await self.bot.db.remove_whitelist(ctx.guild.id, member.id)
        await ctx.send(f"❌ {member.mention} retiré de la whitelist.")
    
    @commands.group(name="blrank", invoke_without_command=True)
    @is_owner_or_buyer()
    async def blacklist_rank(self, ctx):
        """Afficher la liste blacklist-rank"""
        blacklisted = await self.bot.db.get_blacklist_rank(ctx.guild.id)
        
        if not blacklisted:
            return await ctx.send("📋 Aucun membre en blacklist-rank.")
        
        members = []
        for user_id in blacklisted[:20]:  # Limité à 20
            user = ctx.guild.get_member(user_id)
            if user:
                members.append(f"• {user.mention}")
        
        if members:
            await ctx.send(f"📋 **Blacklist-rank :**\\n" + "\\n".join(members))
        else:
            await ctx.send("📋 Aucun membre en blacklist-rank.")
    
    @blacklist_rank.command(name="add")
    @is_owner_or_buyer()
    async def blacklist_rank_add(self, ctx, member: MemberConverter):
        """Ajouter au blacklist-rank"""
        if await self.bot.db.is_blacklist_rank(ctx.guild.id, member.id):
            return await ctx.send("❌ Ce membre est déjà en blacklist-rank.")
        
        await self.bot.db.add_blacklist_rank(ctx.guild.id, member.id, ctx.author.id)
        await ctx.send(f"✅ {member.mention} ajouté au blacklist-rank.")
    
    @blacklist_rank.command(name="del")
    @is_owner_or_buyer()
    async def blacklist_rank_remove(self, ctx, member: MemberConverter):
        """Retirer du blacklist-rank"""
        if not await self.bot.db.is_blacklist_rank(ctx.guild.id, member.id):
            return await ctx.send("❌ Ce membre n'est pas en blacklist-rank.")
        
        await self.bot.db.remove_blacklist_rank(ctx.guild.id, member.id)
        await ctx.send(f"❌ {member.mention} retiré du blacklist-rank.")
    
    @commands.command(name="setupbuyer")
    @commands.is_owner()
    async def setup_buyer(self, ctx, member: MemberConverter):
        """Setup initial buyer (bot owner only)"""
        recovery_code = await self.bot.db.set_buyer(ctx.guild.id, member.id)
        await ctx.send(f"✅ {member.mention} défini comme buyer initial.")
        
        try:
            await member.send(f"🔑 Vous êtes maintenant le buyer du bot sur **{ctx.guild.name}**.\nCode de récupération : `{recovery_code}`")
        except:
            pass

async def setup(bot):
    await bot.add_cog(Ownership(bot))