package de.savox.bossraid;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Blöcke, die das Plugin nur für einen Kampf setzt (Kessel, Eis, Eier ...).
 * Der alte Zustand wird in aufraeumen.yml gemerkt, damit nach einem Absturz nichts liegen bleibt.
 */
final class TempBloecke {
    private final BossRaidPlugin pl;
    private final Map<Location, String> alt = new LinkedHashMap<>();

    TempBloecke(BossRaidPlugin pl) {
        this.pl = pl;
    }

    void setzen(Block b, BlockData neu) {
        Location l = b.getLocation();
        alt.putIfAbsent(l, b.getBlockData().getAsString());
        b.setBlockData(neu, false);
        speichern();
    }

    boolean istTemp(Block b) {
        return alt.containsKey(b.getLocation());
    }

    void zurueck(Block b) {
        String d = alt.remove(b.getLocation());
        if (d != null) {
            try {
                b.setBlockData(Bukkit.createBlockData(d), false);
            } catch (IllegalArgumentException e) {
                b.setType(org.bukkit.Material.AIR, false);
            }
            speichern();
        }
    }

    void allesZurueck() {
        for (Location l : new ArrayList<>(alt.keySet())) {
            if (l.getWorld() != null) {
                zurueck(l.getBlock());
            }
        }
        alt.clear();
        speichern();
    }

    /** Beim Start: Blöcke aus einem abgebrochenen Kampf wiederherstellen. */
    void wiederherstellen() {
        File f = new File(pl.getDataFolder(), "aufraeumen.yml");
        if (!f.exists()) {
            return;
        }
        YamlConfiguration c = YamlConfiguration.loadConfiguration(f);
        int n = 0;
        for (String z : c.getStringList("bloecke")) {
            String[] p = z.split(";", 5);
            if (p.length < 5) {
                continue;
            }
            World w = Bukkit.getWorld(p[0]);
            if (w == null) {
                continue;
            }
            try {
                w.getBlockAt(Integer.parseInt(p[1]), Integer.parseInt(p[2]), Integer.parseInt(p[3]))
                        .setBlockData(Bukkit.createBlockData(p[4]), false);
                n++;
            } catch (IllegalArgumentException ignored) {
                // überspringen
            }
        }
        if (n > 0) {
            pl.getLogger().info(n + " Blöcke aus einem abgebrochenen Kampf wiederhergestellt.");
        }
        f.delete();
    }

    private void speichern() {
        YamlConfiguration c = new YamlConfiguration();
        List<String> l = new ArrayList<>();
        for (Map.Entry<Location, String> e : alt.entrySet()) {
            Location o = e.getKey();
            if (o.getWorld() != null) {
                l.add(o.getWorld().getName() + ";" + o.getBlockX() + ";" + o.getBlockY() + ";" + o.getBlockZ() + ";" + e.getValue());
            }
        }
        c.set("bloecke", l);
        try {
            c.save(new File(pl.getDataFolder(), "aufraeumen.yml"));
        } catch (IOException ignored) {
            // nicht kritisch
        }
    }
}
