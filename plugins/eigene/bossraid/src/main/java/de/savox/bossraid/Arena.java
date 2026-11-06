package de.savox.bossraid;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.block.data.Lightable;
import org.bukkit.block.data.type.Candle;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.List;

/** Ein Kampfgebiet: Kreis mit festem Radius um die Mitte, dazu Boss-Spawn, Eingang, Altar und Tor. */
final class Arena {
    record TorBlock(int x, int y, int z, String daten) {
    }

    final String name;
    String welt;
    double x, y, z;
    Location bossSpawn;
    Location eingang;
    boolean hatAltar;
    int altarX, altarY, altarZ;
    String altarRaid;
    final List<TorBlock> tor = new ArrayList<>();
    long abklingBis;

    Arena(String name) {
        this.name = name;
    }

    World world() {
        return Bukkit.getWorld(welt);
    }

    Location mitte() {
        return new Location(world(), x, y, z);
    }

    boolean enthaelt(Location l) {
        Einstellungen e = BossRaidPlugin.get().einst;
        if (l == null || l.getWorld() == null || !l.getWorld().getName().equals(welt)) {
            return false;
        }
        double dx = l.getX() - x, dz = l.getZ() - z;
        return dx * dx + dz * dz <= (double) e.radius * e.radius && l.getY() >= y - e.hoeheUnten && l.getY() <= y + e.hoeheOben;
    }

    boolean enthaelt(Player p) {
        return p != null && p.isOnline() && enthaelt(p.getLocation());
    }

    List<Player> spielerDrin() {
        List<Player> l = new ArrayList<>();
        for (Player p : Bukkit.getOnlinePlayers()) {
            if (!p.isDead() && enthaelt(p) && !BossRaidPlugin.get().einst.ignoriert(p)) {
                l.add(p);
            }
        }
        return l;
    }

    boolean bereit() {
        return bossSpawn != null && eingang != null && world() != null;
    }

    Block altar() {
        World w = world();
        return (w == null || !hatAltar) ? null : w.getBlockAt(altarX, altarY, altarZ);
    }

    boolean istAltar(Block b) {
        return hatAltar && b != null && b.getWorld().getName().equals(welt) && b.getX() == altarX && b.getY() == altarY && b.getZ() == altarZ;
    }

    List<Block> kerzen() {
        List<Block> l = new ArrayList<>();
        World w = world();
        if (w == null || !hatAltar) {
            return l;
        }
        int[][] ecken = {{3, 3}, {-3, 3}, {3, -3}, {-3, -3}};
        for (int[] e : ecken) {
            l.add(w.getBlockAt(altarX + e[0], altarY, altarZ + e[1]));
        }
        return l;
    }

    /** Setzt an allen Kerzenplätzen eine nicht brennende Kerze (wenn der Platz frei ist). Liefert die belegten Plätze. */
    List<Block> kerzenSetzen() {
        List<Block> belegt = new ArrayList<>();
        for (Block b : kerzen()) {
            if (b.getType().isAir() || b.getType().name().endsWith("CANDLE")) {
                Candle c = (Candle) Bukkit.createBlockData(Material.CANDLE);
                c.setCandles(1);
                c.setLit(false);
                b.setBlockData(c, false);
            } else {
                belegt.add(b);
            }
        }
        return belegt;
    }

    void kerzenLoeschen() {
        for (Block b : kerzen()) {
            BlockData d = b.getBlockData();
            if (b.getType().name().endsWith("CANDLE") && d instanceof Lightable l && l.isLit()) {
                l.setLit(false);
                b.setBlockData(l, false);
            }
        }
    }

    int kerzenAn() {
        int n = 0;
        for (Block b : kerzen()) {
            if (b.getType().name().endsWith("CANDLE") && b.getBlockData() instanceof Lightable l && l.isLit()) {
                n++;
            }
        }
        return n;
    }

    void torSchliessen() {
        World w = world();
        if (w == null) {
            return;
        }
        for (TorBlock t : tor) {
            try {
                w.getBlockAt(t.x(), t.y(), t.z()).setBlockData(Bukkit.createBlockData(t.daten()), false);
            } catch (IllegalArgumentException ignored) {
                // unbekannter Block aus einer anderen Version
            }
        }
    }

    void torOeffnen() {
        World w = world();
        if (w == null) {
            return;
        }
        for (TorBlock t : tor) {
            w.getBlockAt(t.x(), t.y(), t.z()).setType(Material.AIR, false);
        }
    }
}
