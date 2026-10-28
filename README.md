# Grim Nuker

Token-based Discord server nuker with a terminal UI. Bans every bot, wipes every role and channel, and optionally floods the server with channels and spam. Auto-skips anything it doesn't have perms for.

## What it does

1. Bans every bot/app on the server
2. Deletes every role (skips roles above the bot)
3. Deletes every channel and category
4. *(optional)* Floods the server with channels and spams each one

Every destructive action is isolated. Missing perms, role hierarchy, rate limits, it will just skip it and keep going.

## Requirements

- Python 3.10+
- A bot token with **Administrator** (or at minimum Ban Members, Manage Roles, Manage Channels)
- The bot's role must sit **above** any role you want deleted

## Install

```bash
git clone https://github.com/YOU/grim-nuker
cd grim-nuker
pip install -r requirements.txt
cp config.example.json config.json
