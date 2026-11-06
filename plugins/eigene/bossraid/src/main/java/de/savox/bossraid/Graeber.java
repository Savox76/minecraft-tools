package de.savox.bossraid;

import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.block.BlockState;
import org.bukkit.block.TileState;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Item;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.persistence.PersistentDataType;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** Grabtruhen: Sachen eines im Raid gestorbenen Spielers, nur für ihn selbst zu öffnen. */
final class Graeber {
    static final class Grab {
        final String id;
        final UUID besitzer;
        final String name;
        final Location ort;
        final List<ItemStack> sachen;

        Grab(String id, UUID besitzer, String name, Location ort, List<ItemStack> sachen) {
            this.id = id;
            this.besitzer = besitzer;
            this.name = name;
            this.ort = ort;
            this.sachen = sachen;
        }
    }

    private final BossRaidPlugin pl;
    private final Map<String, Grab> graeber = new LinkedHashMap<>();

    Graeber(BossRaidPlugin pl) {
        this.pl = pl;
        laden();
    }

    /** Legt eine Grabtruhe am Todesort an (oder knapp darüber, wenn der Platz belegt ist). */
    void anlegen(Player p, Location tod, List<ItemStack> sachen) {
        if (sachen.isEmpty()) {
            return;
        }
        if (tod.getY() < tod.getWorld().getMinHeight() + 1 || tod.getY() > tod.getWorld().getMaxHeight() - 2) {
            tod = tod.getWorld().getHighestBlockAt(tod).getLocation().add(0, 1, 0);
        }
        Block b = freierPlatz(tod.getBlock());
        if (b == null) {
            // kein Platz: Sachen fallen lassen, nur für den Besitzer
            for (ItemStack i : sachen) {
                Item it = tod.getWorld().dropItemNaturally(tod, i);
                it.setOwner(p.getUniqueId());
            }
            return;
        }
        String id = UUID.randomUUID().toString().substring(0, 8);
        b.setType(Material.CHEST, false);
        BlockState st = b.getState();
        if (st instanceof TileState ts) {
            ts.getPersistentDataContainer().set(Keys.GRAB, PersistentDataType.STRING, id);
            ts.update(true, false);
        }
        graeber.put(id, new Grab(id, p.getUniqueId(), p.getName(), b.getLocation(), new ArrayList<>(sachen)));
        speichern();
        Txt.an(p, "&7Deine Sachen liegen in deiner &6Grabtruhe &7bei &f" + b.getX() + " " + b.getY() + " " + b.getZ()
                + "&7. Nur du kannst sie öffnen (Rechtsklick).");
    }

    private Block freierPlatz(Block b) {
        for (int i = 0; i < 6; i++) {
            Block x = b.getRelative(0, i, 0);
            if (x.getType().isAir() || x.isReplaceable()) {
                return x;
            }
        }
        return null;
    }

    Grab grabVon(Block b) {
        if (b == null || b.getType() != Material.CHEST) {
            return null;
        }
        if (!(b.getState() instanceof TileState ts)) {
            return null;
        }
        String id = ts.getPersistentDataContainer().get(Keys.GRAB, PersistentDataType.STRING);
        return id == null ? null : graeber.get(id);
    }

    /** Rechtsklick auf die Grabtruhe: der Besitzer bekommt alles zurück, was ins Inventar passt. */
    void oeffnen(Player p, Grab g) {
        if (!p.getUniqueId().equals(g.besitzer)) {
            Txt.an(p, "&cDas ist die Grabtruhe von &f" + g.name + "&c. Nur " + g.name + " kann sie öffnen.");
            return;
        }
        List<ItemStack> rest = new ArrayList<>();
        for (ItemStack i : g.sachen) {
            HashMap<Integer, ItemStack> passtNicht = p.getInventory().addItem(i);
            rest.addAll(passtNicht.values());
        }
        g.sachen.clear();
        g.sachen.addAll(rest);
        if (rest.isEmpty()) {
            g.ort.getBlock().setType(Material.AIR, false);
            graeber.remove(g.id);
            Txt.an(p, "&aDu hast alles aus deiner Grabtruhe zurück.");
        } else {
            Txt.an(p, "&eDein Inventar ist voll. &7In der Grabtruhe liegen noch &f" + rest.size() + " &7Stapel.");
        }
        speichern();
    }

    private void laden() {
        File f = new File(pl.getDataFolder(), "graeber.yml");
        if (!f.exists()) {
            return;
        }
        YamlConfiguration c = YamlConfiguration.loadConfiguration(f);
        ConfigurationSection s = c.getConfigurationSection("graeber");
        if (s == null) {
            return;
        }
        for (String id : s.getKeys(false)) {
            ConfigurationSection g = s.getConfigurationSection(id);
            if (g == null || g.getLocation("ort") == null) {
                continue;
            }
            List<ItemStack> sachen = new ArrayList<>();
            for (Object o : g.getList("sachen", List.of())) {
                if (o instanceof ItemStack i) {
                    sachen.add(i);
                }
            }
            graeber.put(id, new Grab(id, UUID.fromString(g.getString("besitzer")), g.getString("name", "?"), g.getLocation("ort"), sachen));
        }
    }

    void speichern() {
        YamlConfiguration c = new YamlConfiguration();
        for (Grab g : graeber.values()) {
            String p = "graeber." + g.id + ".";
            c.set(p + "besitzer", g.besitzer.toString());
            c.set(p + "name", g.name);
            c.set(p + "ort", g.ort);
            c.set(p + "sachen", g.sachen);
        }
        try {
            c.save(new File(pl.getDataFolder(), "graeber.yml"));
        } catch (IOException e) {
            pl.getLogger().warning("Konnte graeber.yml nicht speichern: " + e.getMessage());
        }
    }

    int anzahl() {
        return graeber.size();
    }
}
