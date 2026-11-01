---
titel: Farm bot for Paper servers
kurz: Keep farms running, including crop growth and mob spawning, while nobody is online.
reihenfolge: 1
---

# Farm bot for Paper servers

Goal: farms keep running steadily, including crop growth and mob spawning, while nobody is online. The farms stay small.

We use the **FakePlayerPlugin**. Paper stays, all other plugins stay.

## Why a bot is needed

- Crops only grow when their chunk is loaded **and** a player is no more than **128 blocks** away. The same applies to mob spawning.
- `/forceload` alone is not enough. It only keeps hoppers, furnaces, redstone, villagers and iron farms running.
- The FakePlayerPlugin bot is a full player entity in the world. It appears in the tab list and the player count like a real player.

## 1. Preparation

1. **Check the server version:** type `version` in the server console.
2. **Check the Java version:** the plugin needs **Java 21** or newer. Check with `java -version`.
3. **Backup:** stop the server and copy the whole server folder.

## 2. Install the plugin

1. Open Hangar: <https://hangar.papermc.io/Janky-Development/FakePlayerPlugin>
2. In the **“Versions”** tab, pick the file that matches your server version.
3. Put the `.jar` into the `plugins` folder.
4. Start the server and check in the console that the plugin loaded without errors.

## 3. Set up the bot

1. Build a **safe spot** in the middle of your farms: closed on all sides and well lit.
2. Stand there and create the bot:
   ```
   /fpp spawn --name Farmbot
   ```
3. Freeze the bot so it cannot be pushed away:
   ```
   /fpp freeze Farmbot on
   ```
4. Turn off fake chat, otherwise the bot writes random chat messages:
   ```
   /fpp chat off
   ```
5. Check: `/fpp list` shows all bots with location and uptime.

The bot survives a server restart and returns to its spot.

| Command | Effect |
|---|---|
| `/fpp despawn Farmbot` | Remove the bot |
| `/fpp freeze Farmbot off` | Unfreeze the bot |
| `/fpp stats` | Show bots and server performance (TPS) |
| `/fpp reload` | Reload the config |

## 4. Sugar cane test

The plugin does not say explicitly that the bot also triggers crop growth. So test it once:

1. Plant 5 fresh sugar canes next to the bot with water beside them.
2. Log out and wait 30 to 60 minutes.
3. Log back in: if the sugar cane has grown, everything works.

## 5. Server settings

`server.properties`:

```
simulation-distance=6
pause-when-empty-seconds=0
```

- `simulation-distance=6` simulates about 96 blocks around players and the bot. With the [ServerEinstellungen](#/plugin/servereinstellungen) plugin you can also do this in game: `/einstellungen reichweite 6`.
- `pause-when-empty-seconds`: since 1.21.2 the server pauses when nobody has been online for 60 seconds. The value 0 should turn that off. If “Server empty for 60 seconds, pausing” still appears in the console after you log out, the setting is not working.

Game rule against phantoms, because the bot never sleeps:

```
/gamerule doInsomnia false
```

Keep `randomTickSpeed` at 3, otherwise everything grows faster than intended.

Laptop as server: set sleep and hibernation to “Never” and “When I close the lid” to “Do nothing”.

## 6. Location and size

- Put the bot in the **centre** and keep all farms within **80 blocks**.
- **Mini farms:** greenhouse 7 × 7 or 9 × 9, one row of 8 sugar canes, 6 to 8 kelp columns.
- **Storage as a limit:** a full barrel (1,728 items) backs up the line, surplus disappears after 5 minutes.
- **Stop switch:** comparator on the barrel, redstone dust to the collecting hopper. With 8 dust the farm stops when the barrel is about half full.
- **Light everything up:** monsters spawn around the bot at night, and zombies attack villagers.

## If the test fails

- **AFKDummyForFarming** (Paper 26.2 only, Java 25): <https://modrinth.com/plugin/afkdummyforfarming>, commands `/dafk add Farmbot`, `/dafk remove Farmbot`.
- **Fabric + Carpet:** the proven standard solution, but all Paper plugins are lost. World migration per the [Paper docs](https://docs.papermc.io/paper/migration/).

## Sources

- [FakePlayerPlugin (Hangar)](https://hangar.papermc.io/Janky-Development/FakePlayerPlugin) · [Docs](https://fpp.wtf)
- [Minecraft Wiki: server.properties](https://minecraft.wiki/w/Server.properties)
- [PaperMC forum: random ticks within 128 blocks](https://forums.papermc.io/threads/understanding-tick-updates.959)
