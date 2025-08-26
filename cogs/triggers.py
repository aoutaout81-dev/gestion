import discord
from discord.ext import commands
from typing import Set

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
        # Ignorer les bots et webhooks
        if message.author.bot or message.webhook_id:
            return

        # Éviter les doublons avec cache intelligent
        if message.id in self._processed_messages:
            return
        self._processed_messages.add(message.id)
        
        # Nettoyer le cache périodiquement
        if len(self._processed_messages) > 1000:
            self._processed_messages.clear()

        # Traiter les différentes fonctionnalités
        await self.handle_blocked_channels(message)
        await self.handle_auto_reactions(message)
        await self.handle_selfie_embed(message)

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
        print(f"[🔍] handle_selfie_embed appelé - Channel ID: {message.channel.id}, Expected: {self.config['selfie_channel_id']}")
        
        if message.channel.id != self.config["selfie_channel_id"]:
            print(f"[❌] Mauvais salon - Channel: {message.channel.id}, Expected: {self.config['selfie_channel_id']}")
            return
        
        print(f"[✅] Bon salon selfie détecté!")
        
        if not message.attachments:
            print(f"[❌] Aucune pièce jointe trouvée")
            return

        print(f"[✅] {len(message.attachments)} pièce(s) jointe(s) trouvée(s)")

        # Vérifier que c'est un fichier image
        attachment = message.attachments[0]
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        print(f"[🔍] Vérification fichier: {attachment.filename}")
        
        if not any(attachment.filename.lower().endswith(ext) for ext in image_extensions):
            print(f"[❌] Fichier n'est pas une image: {attachment.filename}")
            return

        print(f"[✅] Image valide détectée: {attachment.filename}")

        # Créer l'embed avec les règles du serveur
        embed = discord.Embed(
            title="<:rules:1407738894480314480> __**Règles du serveur**__",
            description="__**Les trolls seront sanctionnés immédiatement**__, veuillez *respecter les autres* pour que notre communauté reste agréable et conviviale.",
            color=0x0055FF
        )
        embed.set_thumbnail(url="https://giffiles.alphacoders.com/219/219182.gif")
        embed.set_image(url=attachment.url)

        print(f"[🔍] Tentative d'envoi de l'embed...")
        try:
            sent_message = await message.channel.send(embed=embed)
            print(f"[✅] Embed envoyé avec succès! Message ID: {sent_message.id}")
        except Exception as e:
            print(f"[❌] Erreur embed selfie: {e}")
            import traceback
            traceback.print_exc()

async def setup(bot):
    await bot.add_cog(Triggers(bot))