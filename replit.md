# CrowBot Gestion V2

## Overview

CrowBot Gestion V2 is a Discord moderation bot built with Python and discord.py. The bot provides comprehensive server management capabilities including user moderation (ban, kick, mute), administration tools (permission management, prefix configuration), and logging functionality. It features a role-based permission system that allows server administrators to granularly control which roles can execute specific bot commands.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Bot Architecture
- **Main Bot Class**: `CrowBot` extends discord.py's `commands.Bot` with custom initialization and database integration
- **Cog System**: Modular command organization using discord.py cogs for administration and moderation features
- **Async Design**: Built with asyncio for non-blocking database operations and Discord API interactions

### Database Layer
- **SQLite Database**: Local file-based storage (`crowbot.db`) for persistence
- **Async Operations**: Thread-safe database operations using asyncio locks
- **Schema Design**: 
  - Guild settings (prefixes, log channels, mute roles)
  - Command permissions (role-based access control)
  - Command cooldowns (rate limiting configuration)

### Permission System
- **Role-Based Access Control**: Commands can be restricted to specific Discord roles
- **Hierarchical Permissions**: Administrators and server owners have elevated privileges
- **Custom Decorators**: `@has_permission()` and `@admin_only()` decorators for command access control
- **Dynamic Configuration**: Permissions can be modified at runtime via bot commands

### Command Categories
- **Moderation Commands**: User management (ban, kick, mute, warn, infractions)
- **Administration Commands**: Bot configuration (setperm, prefix, cooldown, settings)
- **Utility Functions**: Time parsing, user fetching, role management helpers

### Error Handling
- **Custom Exceptions**: `PermissionError` for access control violations
- **Graceful Degradation**: DM failures and API errors are handled without breaking functionality
- **Comprehensive Logging**: File and console logging for debugging and monitoring

## External Dependencies

### Discord Integration
- **discord.py Library**: Primary framework for Discord bot functionality
- **Bot Token**: Requires `DISCORD_TOKEN` environment variable for authentication
- **Discord Permissions**: Needs specific intents (message_content, members, guilds) and server permissions

### Database
- **SQLite3**: Built-in Python library for local data persistence
- **No External Database**: Self-contained storage solution

### System Dependencies
- **Python 3.7+**: Required for asyncio and discord.py compatibility
- **File System Access**: For database file and log file storage
- **Environment Variables**: Token management via environment configuration