import discord
from discord.ext import commands
from typing import Set
import asyncio

class Triggers(commands.Cog):
    """Gestion des triggers automatiques et protections de salons"""

    def __init__(self, bot):
        self.bot = bot
        self._processed_messages: Set[int] = set()

        # Configuration des salons spéciaux
        self.config = {
            "protected_channels": {
                1402704269458673826,
                1394459808106676314,
                1393676148629573807
            },
            "react_channels": {
                1408082781887664201: [
                    "<a:mochi:1408874019788423209>",
                    "<a:refused:1408873542078173245>"
                ],
                1393676148629573802: [
                    "<a:mochi:1408874019788423209>",
                    "<a:refused:1408873542078173245>"
                ]
            },
            "selfie_channel_id": 1393676148629573807
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Event déclenché à chaque nouveau message"""
        print(f"[📨] Nouveau message reçu - ID: {message.id}, Channel: {message.channel.id}, Author: {message.author}")

        # Ignorer les bots et webhooks
        if message.author.bot or message.webhook_id:
            print(f"[🤖] Message ignoré - Bot: {message.author.bot}, Webhook: {message.webhook_id}")
            return

        # Éviter les doublons avec cache intelligent
        if message.id in self._processed_messages:
            print(f"[🔄] Message déjà traité: {message.id}")
            return
        self._processed_messages.add(message.id)

        # Nettoyer le cache périodiquement
        if len(self._processed_messages) > 1000:
            self._processed_messages.clear()
            print(f"[🧹] Cache nettoyé")

        # Traiter les différentes fonctionnalités
        try:
            await self.handle_blocked_channels(message)
            await self.handle_auto_reactions(message)
            await self.handle_selfie_embed(message)
        except Exception as e:
            print(f"[💥] Erreur générale dans on_message: {e}")
            import traceback
            traceback.print_exc()

    async def handle_blocked_channels(self, message: discord.Message):
        """Gère les salons protégés où seuls les threads sont autorisés"""
        if message.channel.id not in self.config["protected_channels"]:
            return
        if isinstance(message.channel, discord.Thread):
            return
        if not (message.content and message.content.strip()):
            return

        try:
            await message.delete()
            await message.channel.send(
                "⚠️ Les messages texte ne sont autorisés que dans les threads !",
                delete_after=5
            )
        except (discord.NotFound, discord.Forbidden):
            pass
        except Exception as e:
            print(f"[❌] Erreur protection salon: {e}")

    async def handle_auto_reactions(self, message: discord.Message):
        """Ajoute des réactions automatiques sur certains salons"""
        if message.channel.id not in self.config["react_channels"]:
            return

        emojis = self.config["react_channels"][message.channel.id]
        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except (discord.NotFound, discord.Forbidden):
                pass
            except Exception as e:
                print(f"[❌] Erreur réaction {emoji}: {e}")

    async def handle_selfie_embed(self, message: discord.Message):
        """Crée un embed automatique pour les selfies avec règles du serveur"""
        print(f"[🔍] handle_selfie_embed appelé")
        print(f"[🔍] Channel ID reçu: {message.channel.id} (type: {type(message.channel.id)})")
        print(f"[🔍] Channel ID config: {self.config['selfie_channel_id']} (type: {type(self.config['selfie_channel_id'])})")
        print(f"[🔍] Égalité: {message.channel.id == self.config['selfie_channel_id']}")

        if message.channel.id != self.config["selfie_channel_id"]:
            print(f"[❌] Mauvais salon - Channel: {message.channel.id}, Expected: {self.config['selfie_channel_id']}")
            return

        print(f"[✅] Bon salon selfie détecté!")

        # Vérifier les permissions du bot
        try:
            permissions = message.channel.permissions_for(message.guild.me)
            print(f"[🔐] Permissions bot:")
            print(f"    - send_messages: {permissions.send_messages}")
            print(f"    - embed_links: {permissions.embed_links}")
            print(f"    - attach_files: {permissions.attach_files}")
            print(f"    - read_message_history: {permissions.read_message_history}")

            if not permissions.send_messages:
                print(f"[❌] Bot n'a pas la permission d'envoyer des messages!")
                return
            if not permissions.embed_links:
                print(f"[❌] Bot n'a pas la permission d'envoyer des embeds!")
                return
        except Exception as e:
            print(f"[❌] Erreur lors de la vérification des permissions: {e}")

        if not message.attachments:
            print(f"[❌] Aucune pièce jointe trouvée")
            print(f"[🔍] Contenu du message: '{message.content}'")
            return

        print(f"[✅] {len(message.attachments)} pièce(s) jointe(s) trouvée(s)")

        # Vérifier que c'est un fichier média (image ou vidéo)
        attachment = message.attachments[0]
        media_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v')
        print(f"[🔍] Vérification fichier: {attachment.filename}")
        print(f"[🔍] Taille: {attachment.size} bytes")
        print(f"[🔍] Content type: {getattr(attachment, 'content_type', 'N/A')}")

        if not any(attachment.filename.lower().endswith(ext) for ext in media_extensions):
            print(f"[❌] Fichier n'est pas un média supporté: {attachment.filename}")
            return

        print(f"[✅] Média valide détecté: {attachment.filename}")

        # Attendre un peu pour éviter les conflits de rate limiting
        await asyncio.sleep(0.5)

        # Créer l'embed avec les règles du serveur
        try:
            embed = discord.Embed(
                title="<:rules:1407738894480314480> __**Règles du serveur**__",
                description="__**Les trolls seront sanctionnés immédiatement**__, veuillez *respecter les autres* pour que notre communauté reste agréable et conviviale.",
                color=0x0055FF
            )

            # Vérifier si l'URL de l'image est accessible
            print(f"[🔍] URL de l'image: {attachment.url}")
            embed.set_thumbnail(url="https://giffiles.alphacoders.com/219/219182.gif")
            embed.set_image(url=attachment.url)

            print(f"[🔍] Embed créé avec succès")

        except Exception as e:
            print(f"[❌] Erreur lors de la création de l'embed: {e}")
            return

        print(f"[🔍] Tentative d'envoi de l'embed...")
        try:
            # Test d'envoi simple d'abord
            test_message = await message.channel.send("🔍 Test d'envoi...")
            print(f"[✅] Test d'envoi réussi! ID: {test_message.id}")
            await asyncio.sleep(1)
            await test_message.delete()

            # Maintenant envoyer l'embed
            sent_message = await message.channel.send(embed=embed)
            print(f"[✅] Embed envoyé avec succès! Message ID: {sent_message.id}")

        except discord.HTTPException as e:
            print(f"[❌] Erreur HTTP Discord: {e}")
            print(f"[❌] Code d'erreur: {e.status}")
            print(f"[❌] Texte d'erreur: {e.text}")
        except discord.Forbidden as e:
            print(f"[❌] Permissions insuffisantes: {e}")
        except discord.NotFound as e:
            print(f"[❌] Canal non trouvé: {e}")
        except Exception as e:
            print(f"[❌] Erreur embed selfie: {e}")
            import traceback
            traceback.print_exc()

    @commands.command(name="test_selfie")
    @commands.has_permissions(administrator=True)
    async def test_selfie_command(self, ctx):
        """Commande de test pour vérifier la configuration du salon selfie"""
        channel_id = self.config["selfie_channel_id"]
        channel = self.bot.get_channel(channel_id)

        if not channel:
            await ctx.send(f"❌ Canal selfie non trouvé! ID: {channel_id}")
            return

        permissions = channel.permissions_for(ctx.guild.me)

        embed = discord.Embed(
            title="🔍 Test Configuration Selfie",
            color=0x00ff00
        )
        embed.add_field(
            name="Canal",
            value=f"{channel.mention} (ID: {channel_id})",
            inline=False
        )
        embed.add_field(
            name="Permissions",
            value=f"Send Messages: {permissions.send_messages}\n"
                  f"Embed Links: {permissions.embed_links}\n"
                  f"Attach Files: {permissions.attach_files}",
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Triggers(bot))