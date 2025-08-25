import sqlite3
import asyncio
import json
import time
import secrets
from typing import List, Optional, Dict, Any

class Database:
    def __init__(self, db_path: str = "crowbot.db"):
        self.db_path = db_path
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the database with required tables"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Guild settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT DEFAULT '+',
                    log_channel_id INTEGER,
                    mute_role_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Command permissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    command_name TEXT,
                    role_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, command_name, role_id)
                )
            ''')
            
            # Command cooldowns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_cooldowns (
                    guild_id INTEGER,
                    command_name TEXT,
                    cooldown_seconds INTEGER,
                    PRIMARY KEY(guild_id, command_name)
                )
            ''')
            
            # Command usage tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_usage (
                    guild_id INTEGER,
                    user_id INTEGER,
                    command_name TEXT,
                    last_used TIMESTAMP,
                    PRIMARY KEY(guild_id, user_id, command_name)
                )
            ''')
            
            # Infractions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS infractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    infraction_type TEXT,
                    reason TEXT,
                    duration INTEGER,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Muted users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS muted_users (
                    guild_id INTEGER,
                    user_id INTEGER,
                    muted_until TIMESTAMP,
                    reason TEXT,
                    moderator_id INTEGER,
                    PRIMARY KEY(guild_id, user_id)
                )
            ''')
            
            # Moderation logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS moderation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    action TEXT,
                    reason TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bot ownership tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_ownership (
                    guild_id INTEGER PRIMARY KEY,
                    buyer_id INTEGER,
                    recovery_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Owners table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS owners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    added_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, user_id)
                )
            ''')
            
            # Whitelist table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whitelist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    added_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, user_id)
                )
            ''')
            
            # Blacklist rank table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blacklist_rank (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    added_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, user_id)
                )
            ''')
            
            # Leash system table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leash_system (
                    guild_id INTEGER,
                    user_id INTEGER,
                    owner_id INTEGER,
                    original_nick TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(guild_id, user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
    
    # Extensions from database_extensions.py
    # Bot Ownership methods
    async def set_buyer(self, guild_id: int, buyer_id: int) -> str:
        """Set the buyer/owner of the bot for a guild and generate recovery code"""
        recovery_code = secrets.token_hex(16)
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO bot_ownership (guild_id, buyer_id, recovery_code)
                VALUES (?, ?, ?)
            ''', (guild_id, buyer_id, recovery_code))
            
            conn.commit()
            conn.close()
            
        return recovery_code
    
    async def get_buyer(self, guild_id: int) -> Optional[int]:
        """Get the buyer ID for a guild"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT buyer_id FROM bot_ownership WHERE guild_id = ?
            ''', (guild_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
    
    async def verify_recovery_code(self, guild_id: int, code: str) -> bool:
        """Verify recovery code for buyer transfer"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT recovery_code FROM bot_ownership WHERE guild_id = ?
            ''', (guild_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result and result[0] == code
    
    # Owners methods
    async def add_owner(self, guild_id: int, user_id: int, added_by: int):
        """Add an owner"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO owners (guild_id, user_id, added_by)
                VALUES (?, ?, ?)
            ''', (guild_id, user_id, added_by))
            
            conn.commit()
            conn.close()
    
    async def remove_owner(self, guild_id: int, user_id: int):
        """Remove an owner"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM owners WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            conn.commit()
            conn.close()
    
    async def is_owner(self, guild_id: int, user_id: int) -> bool:
        """Check if user is an owner"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 1 FROM owners WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return bool(result)
    
    async def get_owners(self, guild_id: int) -> List[int]:
        """Get all owners for a guild"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id FROM owners WHERE guild_id = ?
            ''', (guild_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [result[0] for result in results]
    
    # Whitelist methods
    async def add_whitelist(self, guild_id: int, user_id: int, added_by: int):
        """Add user to whitelist"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO whitelist (guild_id, user_id, added_by)
                VALUES (?, ?, ?)
            ''', (guild_id, user_id, added_by))
            
            conn.commit()
            conn.close()
    
    async def remove_whitelist(self, guild_id: int, user_id: int):
        """Remove user from whitelist"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM whitelist WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            conn.commit()
            conn.close()
    
    async def is_whitelisted(self, guild_id: int, user_id: int) -> bool:
        """Check if user is whitelisted"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 1 FROM whitelist WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return bool(result)
    
    async def get_whitelist(self, guild_id: int) -> List[int]:
        """Get all whitelisted users"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id FROM whitelist WHERE guild_id = ?
            ''', (guild_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [result[0] for result in results]
    
    # Blacklist rank methods
    async def add_blacklist_rank(self, guild_id: int, user_id: int, added_by: int):
        """Add user to blacklist rank"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO blacklist_rank (guild_id, user_id, added_by)
                VALUES (?, ?, ?)
            ''', (guild_id, user_id, added_by))
            
            conn.commit()
            conn.close()
    
    async def remove_blacklist_rank(self, guild_id: int, user_id: int):
        """Remove user from blacklist rank"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM blacklist_rank WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            conn.commit()
            conn.close()
    
    async def is_blacklist_rank(self, guild_id: int, user_id: int) -> bool:
        """Check if user is in blacklist rank"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 1 FROM blacklist_rank WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return bool(result)
    
    async def get_blacklist_rank(self, guild_id: int) -> List[int]:
        """Get all blacklisted rank users"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id FROM blacklist_rank WHERE guild_id = ?
            ''', (guild_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [result[0] for result in results]
    
    # Leash system methods
    async def add_leash(self, guild_id: int, user_id: int, owner_id: int, original_nick: str):
        """Put user on leash"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO leash_system (guild_id, user_id, owner_id, original_nick)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, user_id, owner_id, original_nick))
            
            conn.commit()
            conn.close()
    
    async def remove_leash(self, guild_id: int, user_id: int):
        """Remove user from leash"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM leash_system WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            conn.commit()
            conn.close()
    
    async def get_leash_info(self, guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get leash info for user"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT owner_id, original_nick FROM leash_system 
                WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'owner_id': result[0],
                    'original_nick': result[1]
                }
            return None
    
    async def is_leashed(self, guild_id: int, user_id: int) -> bool:
        """Check if user is leashed"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 1 FROM leash_system WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return bool(result)
    
    async def setup_guild(self, guild_id: int):
        """Setup a new guild in the database"""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)
            ''', (guild_id,))
            
            conn.commit()
            conn.close()
    
