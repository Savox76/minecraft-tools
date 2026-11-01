---
titel: Logging player actions
kurz: Use CoreProtect to see who built, broke or took what from chests.
reihenfolge: 2
---

# Logging player actions with CoreProtect

CoreProtect is the standard plugin on Paper for tracing who did what and when. It can also roll back placed or destroyed blocks.

## What gets logged

- Placing and breaking blocks
- Chests: who put in or took out what
- Dropping and picking up items, doors, levers and buttons
- Killed mobs, logins and logouts
- Chat, commands, sign text

## Installation

1. Make a **backup**.
2. Get the `.jar` from Modrinth: <https://modrinth.com/plugin/coreprotect> (under “Plugins”).
3. Put it into the `plugins` folder and restart the server.

The stable version supports Minecraft up to 26.1.2. Development builds for newer versions are on GitHub.

## Commands

| Command | What it does |
|---|---|
| `/co i` | Inspector on/off: click a block to see who placed or broke it |
| `/co lookup u:Name t:1d` | Everything this player did in the last day |
| `/co lookup u:Name t:3d a:container` | Their chest activity in the last 3 days |
| `/co lookup u:Name a:session` | When they were online |
| `/co lookup t:2h r:20` | Everything within 20 blocks in the last 2 hours |
| `/co rollback u:Name t:2h r:#global #preview` | Preview what would be rolled back |
| `/co rollback u:Name t:2h r:#global` | Actually roll back the changes |
| `/co undo` | Undo the last rollback |
| `/co purge t:30d` | Delete data older than 30 days |

Always give `r:` for a rollback, otherwise it only works within 10 blocks.

## Without a plugin

`logs/latest.log` in the server folder contains logins, chat and commands. Older days are stored next to it as `.log.gz`. Blocks and chests are not in there.

For the shared storage there is also `/lager protokoll` from the [InfiniteLager](#/plugin/infinitelager) plugin.

**Be fair:** tell the players on your server that their actions are being logged.

## Sources

- [GameServerKings: CoreProtect](https://www.gameserverkings.com/knowledge-base/minecraft/coreprotect-rollback/)
- [Mineguard: rolling back grief](https://mineguard.pro/en/blog/coreprotect-rollback-grief-recovery)
