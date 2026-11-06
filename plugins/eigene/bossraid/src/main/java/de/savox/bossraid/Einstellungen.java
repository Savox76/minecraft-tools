package de.savox.bossraid;

import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/** Werte aus config.yml. */
final class Einstellungen {
    record StufenWerte(double leben, double schaden, double loot) {
    }

    int radius, hoeheUnten, hoeheOben;
    final Map<Stufe, StufenWerte> stufen = new EnumMap<>(Stufe.class);
    double lebenProSpieler, heilungBeiTod, mindestAnteil;
    int fernkampfEntfernung;
    double fernkampfFaktor;
    int unerreichbarHoehe, unerreichbarSekunden;
    int kerzenZeit, ritualDauer, sammelnSekunden, auftrittSekunden;
    int fragmentTageslimit;
    int besitzerschutzMinuten;
    final List<String> nieAbnehmen = new ArrayList<>();
    final Set<String> ignoriert = new HashSet<>();
    boolean npcIgnorieren;
    int maxLebenpunkteWesen;

    void laden(FileConfiguration c) {
        radius = c.getInt("arena.radius", 30);
        hoeheUnten = c.getInt("arena.hoehe-unten", 10);
        hoeheOben = c.getInt("arena.hoehe-oben", 30);
        for (Stufe s : Stufe.values()) {
            ConfigurationSection sec = c.getConfigurationSection("stufen." + s.id());
            double l = sec == null ? 1 : sec.getDouble("leben", 1);
            double d = sec == null ? 1 : sec.getDouble("schaden", 1);
            double o = sec == null ? 1 : sec.getDouble("loot", 1);
            stufen.put(s, new StufenWerte(l, d, o));
        }
        lebenProSpieler = c.getDouble("leben-pro-weiterem-spieler", 0.4);
        heilungBeiTod = c.getDouble("heilung-bei-spielertod", 0.10);
        mindestAnteil = c.getDouble("loot.mindest-anteil", 0.05);
        fernkampfEntfernung = c.getInt("fernkampf.entfernung", 30);
        fernkampfFaktor = c.getDouble("fernkampf.faktor", 0.5);
        unerreichbarHoehe = c.getInt("unerreichbar.hoehe", 4);
        unerreichbarSekunden = c.getInt("unerreichbar.sekunden", 5);
        kerzenZeit = c.getInt("ritual.kerzen-zeit", 60);
        ritualDauer = c.getInt("ritual.dauer", 10);
        sammelnSekunden = c.getInt("sammeln-sekunden", 60);
        auftrittSekunden = c.getInt("auftritt-sekunden", 5);
        fragmentTageslimit = c.getInt("fragmente.tageslimit", 8);
        besitzerschutzMinuten = c.getInt("tod.normal-besitzerschutz-minuten", 10);
        nieAbnehmen.clear();
        for (String s : c.getStringList("tod.nie-abnehmen")) {
            nieAbnehmen.add(s.toLowerCase(Locale.ROOT));
        }
        ignoriert.clear();
        for (String s : c.getStringList("ignorierte-spieler")) {
            ignoriert.add(s.toLowerCase(Locale.ROOT));
        }
        npcIgnorieren = c.getBoolean("npc-ignorieren", true);
        maxLebenpunkteWesen = Math.max(20, c.getInt("max-lebenspunkte-wesen", 1000));
    }

    StufenWerte stufe(Stufe s) {
        return stufen.get(s);
    }

    /** Farm-Bots und andere Nicht-Spieler zählen nie als Teilnehmer. */
    boolean ignoriert(Player p) {
        if (ignoriert.contains(p.getName().toLowerCase(Locale.ROOT))) {
            return true;
        }
        return npcIgnorieren && p.hasMetadata("NPC");
    }

    /** Gegenstände wie das Hilfe-Buch werden bei keiner Todesregel abgenommen. */
    boolean nieAbnehmen(ItemStack i) {
        if (i == null || !i.hasItemMeta() || nieAbnehmen.isEmpty()) {
            return false;
        }
        ItemMeta m = i.getItemMeta();
        if (m.displayName() == null) {
            return false;
        }
        String name = PlainTextComponentSerializer.plainText().serialize(m.displayName()).toLowerCase(Locale.ROOT);
        for (String s : nieAbnehmen) {
            if (name.contains(s)) {
                return true;
            }
        }
        return false;
    }
}
