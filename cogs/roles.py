import discord
from discord.ext import commands
from typing import Optional
from utils.permissions import has_permission
from utils.converters import MemberConverter, RoleConverter

class RoleManagement(commands.Cog):
    """Gestion des rôles du serveur"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="addrole")
    @has_permission()
    async def add_role(self, ctx, member: MemberConverter, role: RoleConverter):
        """Ajouter un rôle à un membre"""
        if member == ctx.author and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous ne pouvez pas vous ajouter des rôles à vous-même.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        # Vérifier la hiérarchie des rôles
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous ne pouvez pas gérer un rôle supérieur ou égal au vôtre.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        if role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Je ne peux pas gérer ce rôle car il est supérieur au mien.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        # Vérifier si le membre a déjà le rôle
        if role in member.roles:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"**{member}** possède déjà le rôle {role.mention}.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.add_roles(role, reason=f"Ajouté par {ctx.author}")
            
            # Log de l'action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, member.id, ctx.author.id, "addrole", 
                f"Rôle {role.name} ajouté"
            )
            
            embed = discord.Embed(
                title="✅ Rôle ajouté",
                description=f"Le rôle {role.mention} a été ajouté à **{member}**.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Je n'ai pas la permission d'ajouter ce rôle.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Échec de l'ajout du rôle : {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="delrole", aliases=["removerole"])
    @has_permission()
    async def remove_role(self, ctx, member: MemberConverter, role: RoleConverter):
        """Retirer un rôle d'un membre"""
        if member == ctx.author and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous ne pouvez pas vous retirer des rôles à vous-même.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        # Vérifier la hiérarchie des rôles
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous ne pouvez pas gérer un rôle supérieur ou égal au vôtre.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        if role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Je ne peux pas gérer ce rôle car il est supérieur au mien.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        # Vérifier si le membre a le rôle
        if role not in member.roles:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"**{member}** ne possède pas le rôle {role.mention}.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.remove_roles(role, reason=f"Retiré par {ctx.author}")
            
            # Log de l'action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, member.id, ctx.author.id, "delrole", 
                f"Rôle {role.name} retiré"
            )
            
            embed = discord.Embed(
                title="✅ Rôle retiré",
                description=f"Le rôle {role.mention} a été retiré de **{member}**.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Je n'ai pas la permission de retirer ce rôle.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Échec du retrait du rôle : {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="createrole")
    @has_permission()
    async def create_role(self, ctx, name: str, color: str = None, *, permissions: str = None):
        """Créer un nouveau rôle"""
        # Vérifier si le rôle existe déjà
        if discord.utils.get(ctx.guild.roles, name=name):
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Un rôle nommé **{name}** existe déjà.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        # Traitement de la couleur
        role_color = discord.Color.default()
        if color:
            try:
                if color.startswith('#'):
                    role_color = discord.Color(int(color[1:], 16))
                else:
                    # Couleurs prédéfinies
                    color_map = {
                        'rouge': discord.Color.red(),
                        'bleu': discord.Color.blue(),
                        'vert': discord.Color.green(),
                        'jaune': discord.Color.yellow(),
                        'orange': discord.Color.orange(),
                        'violet': discord.Color.purple(),
                        'rose': discord.Color.magenta(),
                        'cyan': discord.Color.teal(),
                        'noir': discord.Color.from_rgb(0, 0, 0),
                        'blanc': discord.Color.from_rgb(255, 255, 255)
                    }
                    role_color = color_map.get(color.lower(), discord.Color.default())
            except ValueError:
                embed = discord.Embed(
                    title="❌ Couleur invalide",
                    description="Format de couleur invalide. Utilisez #RRGGBB ou un nom de couleur.",
                    color=self.bot.config.error_color
                )
                await ctx.send(embed=embed)
                return
        
        # Traitement des permissions (optionnel - par défaut aucune permission spéciale)
        role_permissions = discord.Permissions.none()
        if permissions:
            if 'admin' in permissions.lower():
                role_permissions = discord.Permissions.all()
            elif 'mod' in permissions.lower() or 'moderator' in permissions.lower():
                role_permissions = discord.Permissions(
                    manage_messages=True,
                    kick_members=True,
                    ban_members=True,
                    manage_roles=True
                )
        
        try:
            new_role = await ctx.guild.create_role(
                name=name,
                color=role_color,
                permissions=role_permissions,
                reason=f"Créé par {ctx.author}"
            )
            
            # Log de l'action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "createrole", 
                f"Rôle {name} créé"
            )
            
            embed = discord.Embed(
                title="✅ Rôle créé",
                description=f"Le rôle {new_role.mention} a été créé avec succès.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Nom", value=name, inline=True)
            embed.add_field(name="Couleur", value=color or "Défaut", inline=True)
            embed.add_field(name="ID", value=new_role.id, inline=True)
            embed.add_field(name="Créé par", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Je n'ai pas la permission de créer des rôles.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Échec de la création du rôle : {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="deleterole")
    @has_permission()
    async def delete_role(self, ctx, role: RoleConverter):
        """Supprimer un rôle existant"""
        # Vérifier la hiérarchie des rôles
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous ne pouvez pas supprimer un rôle supérieur ou égal au vôtre.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        if role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Je ne peux pas supprimer ce rôle car il est supérieur au mien.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        # Vérifier s'il s'agit d'un rôle système
        if role.is_default() or role.managed:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Ce rôle ne peut pas être supprimé (rôle système ou géré par une intégration).",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
            return
        
        role_name = role.name
        member_count = len(role.members)
        
        try:
            await role.delete(reason=f"Supprimé par {ctx.author}")
            
            # Log de l'action
            await self.bot.db.log_moderation_action(
                ctx.guild.id, 0, ctx.author.id, "deleterole", 
                f"Rôle {role_name} supprimé"
            )
            
            embed = discord.Embed(
                title="✅ Rôle supprimé",
                description=f"Le rôle **{role_name}** a été supprimé.",
                color=self.bot.config.success_color
            )
            embed.add_field(name="Membres affectés", value=member_count, inline=True)
            embed.add_field(name="Supprimé par", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Je n'ai pas la permission de supprimer ce rôle.",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Échec de la suppression du rôle : {str(e)}",
                color=self.bot.config.error_color
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="rolestats", aliases=["roleinfo"])
    @has_permission()
    async def role_stats(self, ctx, role: RoleConverter):
        """Afficher les statistiques d'un rôle"""
        members_with_role = role.members
        
        embed = discord.Embed(
            title=f"📊 Statistiques du rôle {role.name}",
            color=role.color if role.color != discord.Color.default() else self.bot.config.embed_color
        )
        
        embed.add_field(name="Nom", value=role.name, inline=True)
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Membres", value=len(members_with_role), inline=True)
        
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Couleur", value=str(role.color), inline=True)
        embed.add_field(name="Mentionnable", value="Oui" if role.mentionable else "Non", inline=True)
        
        embed.add_field(name="Affiché séparément", value="Oui" if role.hoist else "Non", inline=True)
        embed.add_field(name="Géré par bot", value="Oui" if role.managed else "Non", inline=True)
        embed.add_field(name="Créé le", value=role.created_at.strftime("%d/%m/%Y à %H:%M"), inline=True)
        
        # Liste des membres (limité à 20 pour éviter les messages trop longs)
        if members_with_role:
            member_list = []
            for i, member in enumerate(members_with_role[:20]):
                member_list.append(f"{i+1}. {member.mention}")
            
            members_text = "\n".join(member_list)
            if len(members_with_role) > 20:
                members_text += f"\n... et {len(members_with_role) - 20} autres"
            
            embed.add_field(
                name="Membres possédant ce rôle",
                value=members_text,
                inline=False
            )
        else:
            embed.add_field(
                name="Membres possédant ce rôle",
                value="Aucun membre ne possède ce rôle.",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))