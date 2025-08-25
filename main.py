import asyncio
import logging
import os
from bot import CrowBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crowbot.log'),
        logging.StreamHandler()
    ]
)

async def main():
    """Main entry point for the bot"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logging.error("DISCORD_TOKEN environment variable not set!")
        return
    
    bot = CrowBot()
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Bot encountered an error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
