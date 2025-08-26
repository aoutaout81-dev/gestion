import discord
from discord.ext import commands
import asyncio
from typing import Set
from collections import deque
import time

class Triggers(commands.Cog):
    """Gestion des triggers automatiques et protections de salons"""

    def __init__(self, bot):
        self.bot = bot
        # Utiliser un cache LRU avec timestamp pour éviter les doublons
        self._processed_messages = {}
        self._cache_max_size = 500
        self._cache_cleanup_interval = 300  # 5 minutes
        
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

        # Éviter les doublons avec cache intelligent et timestamp
        current_time = time.time()
        message_key = f"{message.id}_{message.channel.id}"
        
        # Vérifier si le message a déjà été traité récemment (dans les 60 dernières secondes)
        if message_key in self._processed_messages:
            if current_time - self._processed_messages[message_key] < 60:
                return
        
        # Marquer le message comme traité
        self._processed_messages[message_key] = current_time
        
        # Nettoyer le cache de manière intelligente (supprimer les anciens)
        if len(self._processed_messages) > self._cache_max_size:
            # Supprimer les entrées plus anciennes que 5 minutes
            cutoff_time = current_time - self._cache_cleanup_interval
            old_keys = [k for k, t in self._processed_messages.items() if t < cutoff_time]
            for key in old_keys:
                del self._processed_messages[key]
            
            # Si encore trop d'entrées, garder seulement les plus récentes
            if len(self._processed_messages) > self._cache_max_size:
                sorted_items = sorted(self._processed_messages.items(), key=lambda x: x[1], reverse=True)
                self._processed_messages = dict(sorted_items[:self._cache_max_size])

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
        # Vérifier le salon sans logging excessif
        if message.channel.id != self.config["selfie_channel_id"]:
            return
        
        if not message.attachments:
            return

        # Vérifier que c'est un fichier média (image ou vidéo)
        attachment = message.attachments[0]
        media_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v')
        
        if not any(attachment.filename.lower().endswith(ext) for ext in media_extensions):
            return

        # Créer l'embed avec les règles du serveur
        embed = discord.Embed(
            title="<:rules:1407738894480314480> __**Règles du serveur**__",
            description="__**Les trolls seront sanctionnés immédiatement**__, veuillez *respecter les autres* pour que notre communauté reste agréable et conviviale.",
            color=0x0055FF
        )
        embed.set_thumbnail(url="https://giffiles.alphacoders.com/219/219182.gif")
        embed.set_image(url=attachment.url)

        try:
            await message.channel.send(embed=embed)
        except Exception as e:
            # Log uniquement les erreurs importantes
            self.bot.logger.error(f"Erreur lors de l'envoi de l'embed selfie: {e}")

async def setup(bot):
    await bot.add_cog(Triggers(bot))