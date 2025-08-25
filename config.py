class Config:
    def __init__(self):
        self.default_prefix = "+"
        self.bot_description = "CrowBot Gestion V2 - Discord Moderation Bot"
        self.embed_color = 0x2F3136
        self.error_color = 0xFF0000
        self.success_color = 0x00FF00
        self.warning_color = 0xFFFF00
        
        # Command categories
        self.moderation_commands = [
            'ban', 'unban', 'kick', 'mute', 'unmute', 'warn', 
            'clear', 'lock', 'unlock', 'infractions', 'mutelist'
        ]
        
        self.admin_commands = [
            'setperm', 'unsetperm', 'perms', 'resetperms', 
            'cooldown', 'settings', 'prefix'
        ]
        
        # Time parsing formats
        self.time_units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800
        }
