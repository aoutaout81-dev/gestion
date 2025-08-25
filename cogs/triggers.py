import discord
from discord.ext import commands
import asyncio

class Triggers(commands.Cog):
    """Gestion des triggers automatiques et protections de salons"""

    def __init__(self, bot):
        self.bot = bot

        # 🔹 Salons protégés (texte interdit hors threads)
        self.protected_channels = [
            1402704269458673826,
            1394459808106676314,
            1393676148629573807
        ]

        # 🔹 Salons avec réactions automatiques (uniquement emojis animés)
        self.react_channels = {
            1408082781887664201: [
                "<a:mochi:1408874019788423209>",
                "<a:refused:1408873542078173245>"
            ],
            1393676148629573802: [
                "<a:mochi:1408874019788423209>",
                "<a:refused:1408873542078173245>"
            ]
        }

        # 🔹 Salon selfie pour embed automatique
        self.selfie_channel_id = 1393676148629573807

        # 🔹 Lock pour éviter les doublons
        self.processed_messages = set()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignorer les bots et webhooks
        if message.author.bot or message.webhook_id:
            return

        # Eviter de traiter plusieurs fois le même message
        if message.id in self.processed_messages:
            return
        self.processed_messages.add(message.id)

        # Gestion salons protégés
        await self.handle_blocked_channels(message)

        # Réactions automatiques
        await self.handle_auto_reactions(message)

        # Embed automatique pour selfies
        await self.handle_selfie_embed(message)

    async def handle_blocked_channels(self, message: discord.Message):
        if message.channel.id not in self.protected_channels:
            return
        if isinstance(message.channel, discord.Thread):
            return
        if message.content and message.content.strip():
            try:
                await message.delete()
                warn_msg = await message.channel.send(
                    "⚠️ Les messages texte ne sont autorisés que dans les threads !"
                )
                await asyncio.sleep(5)
                await warn_msg.delete()
            except Exception as e:
                print(f"[❌] Erreur handle_blocked_channels: {e}")

    async def handle_auto_reactions(self, message: discord.Message):
        if message.channel.id not in self.react_channels:
            return
        for emoji in self.react_channels[message.channel.id]:
            if emoji.startswith("<a:"):
                try:
                    await message.add_reaction(emoji)
                except Exception as e:
                    print(f"[❌] Erreur en ajoutant {emoji}: {e}")

    async def handle_selfie_embed(self, message: discord.Message):
        if message.channel.id != self.selfie_channel_id:
            return
        if not message.attachments:
            return

        # Eviter d’envoyer plusieurs embeds pour le même message
        if getattr(message, "_embed_sent", False):
            return
        message._embed_sent = True

        embed = discord.Embed(
            title="<:rules:1407738894480314480> __**Règles du serveur**__",
            description="__**Les trolls seront sanctionnés immédiatement**__, veuillez *respecter les autres* pour que notre communauté reste agréable et conviviale.",
            color=0x0055FF
        )
        embed.set_thumbnail(url="https://giffiles.alphacoders.com/219/219182.gif")
        embed.set_image(url=message.attachments[0].url)

        try:
            await message.channel.send(embed=embed)
        except Exception as e:
            print(f"[❌] Erreur handle_selfie_embed: {e}")

async def setup(bot):
    await bot.add_cog(Triggers(bot))
