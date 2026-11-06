package de.savox.bossraid;

import org.bukkit.Location;
import org.bukkit.block.Block;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.logging.Level;

/** Arenen (arenen.yml), Raid-Vorlagen (raids.yml) und Fragment-Zähler (daten.yml). */
final class Speicher {
    private final BossRaidPlugin pl;
    final Map<String, Arena> arenen = new LinkedHashMap<>();
    final Map<String, RaidVorlage> raids = new LinkedHashMap<>();
    private YamlConfiguration daten;

    Speicher(BossRaidPlugin pl) {
        this.pl = pl;
    }

    private File datei(String name) {
        return new File(pl.getDataFolder(), name);
    }

    static String key(String name) {
        return name.toLowerCase(Locale.ROOT);
    }

    // ---------- Arenen ----------

    Arena arena(String name) {
        return name == null ? null : arenen.get(key(name));
    }

    Arena arenaAn(Location l) {
        for (Arena a : arenen.values()) {
            if (a.enthaelt(l)) {
                return a;
            }
        }
        return null;
    }

    Arena arenaMitAltar(Block b) {
        for (Arena a : arenen.values()) {
            if (a.istAltar(b)) {
                return a;
            }
        }
        return null;
    }

    Arena arenaMitKerze(Block b) {
        for (Arena a : arenen.values()) {
            for (Block k : a.kerzen()) {
                if (k.equals(b)) {
                    return a;
                }
            }
        }
        return null;
    }

    void arenenLaden() {
        arenen.clear();
        YamlConfiguration c = YamlConfiguration.loadConfiguration(datei("arenen.yml"));
        ConfigurationSection s = c.getConfigurationSection("arenen");
        if (s == null) {
            return;
        }
        for (String k : s.getKeys(false)) {
            ConfigurationSection a = s.getConfigurationSection(k);
            if (a == null) {
                continue;
            }
            Arena ar = new Arena(a.getString("name", k));
            ar.welt = a.getString("welt");
            ar.x = a.getDouble("x");
            ar.y = a.getDouble("y");
            ar.z = a.getDouble("z");
            ar.bossSpawn = a.getLocation("bossspawn");
            ar.eingang = a.getLocation("eingang");
            ar.hatAltar = a.contains("altar.x");
            ar.altarX = a.getInt("altar.x");
            ar.altarY = a.getInt("altar.y");
            ar.altarZ = a.getInt("altar.z");
            ar.altarRaid = a.getString("altar.raid");
            ar.abklingBis = a.getLong("abkling-bis");
            for (String t : a.getStringList("tor")) {
                String[] p = t.split(";", 4);
                if (p.length == 4) {
                    try {
                        ar.tor.add(new Arena.TorBlock(Integer.parseInt(p[0]), Integer.parseInt(p[1]), Integer.parseInt(p[2]), p[3]));
                    } catch (NumberFormatException ignored) {
                        // fehlerhafte Zeile überspringen
                    }
                }
            }
            arenen.put(key(ar.name), ar);
        }
    }

    void arenenSpeichern() {
        YamlConfiguration c = new YamlConfiguration();
        c.options().setHeader(List.of("BossRaid: Arenen. Wird vom Plugin geschrieben, am besten nur mit /bossarena ändern."));
        for (Arena ar : arenen.values()) {
            String p = "arenen." + key(ar.name) + ".";
            c.set(p + "name", ar.name);
            c.set(p + "welt", ar.welt);
            c.set(p + "x", ar.x);
            c.set(p + "y", ar.y);
            c.set(p + "z", ar.z);
            c.set(p + "bossspawn", ar.bossSpawn);
            c.set(p + "eingang", ar.eingang);
            if (ar.hatAltar) {
                c.set(p + "altar.x", ar.altarX);
                c.set(p + "altar.y", ar.altarY);
                c.set(p + "altar.z", ar.altarZ);
                c.set(p + "altar.raid", ar.altarRaid);
            }
            c.set(p + "abkling-bis", ar.abklingBis);
            List<String> tor = new ArrayList<>();
            for (Arena.TorBlock t : ar.tor) {
                tor.add(t.x() + ";" + t.y() + ";" + t.z() + ";" + t.daten());
            }
            c.set(p + "tor", tor);
        }
        speichern(c, "arenen.yml");
    }

    // ---------- Raids ----------

    RaidVorlage raid(String name) {
        return name == null ? null : raids.get(key(name));
    }

    void raidsLaden() {
        raids.clear();
        YamlConfiguration c = YamlConfiguration.loadConfiguration(datei("raids.yml"));
        ConfigurationSection s = c.getConfigurationSection("raids");
        if (s == null) {
            return;
        }
        for (String k : s.getKeys(false)) {
            ConfigurationSection r = s.getConfigurationSection(k);
            if (r == null) {
                continue;
            }
            RaidVorlage v = new RaidVorlage(r.getString("name", k));
            v.boss = r.getString("boss");
            v.arena = r.getString("arena");
            Stufe st = Stufe.von(r.getString("stufe"));
            v.stufe = st == null ? Stufe.NORMAL : st;
            Todesregel t = Todesregel.von(r.getString("tod"));
            v.tod = t == null ? Todesregel.GRABTRUHE : t;
            v.leben = r.getInt("leben", 3);
            v.zeitMinuten = r.getInt("zeit", 15);
            v.leerSekunden = r.getInt("leer", 60);
            v.spielerMin = r.getInt("spieler-min", 1);
            v.spielerMax = r.getInt("spieler-max", 8);
            v.loot = r.getDouble("loot", 1.0);
            v.abklingzeitMinuten = r.getInt("abklingzeit", 60);
            v.beschwoerung = r.getBoolean("beschwoerung", true);
            v.siege = r.getInt("statistik.siege");
            v.gescheitert = r.getInt("statistik.gescheitert");
            v.besteZeit = r.getInt("statistik.beste-zeit");
            v.letzteRangliste.addAll(r.getStringList("statistik.letzte-rangliste"));
            raids.put(key(v.name), v);
        }
    }

    void raidsSpeichern() {
        YamlConfiguration c = new YamlConfiguration();
        c.options().setHeader(List.of("BossRaid: Raid-Vorlagen. Am besten mit /raid set ändern."));
        for (RaidVorlage v : raids.values()) {
            String p = "raids." + key(v.name) + ".";
            c.set(p + "name", v.name);
            c.set(p + "boss", v.boss);
            c.set(p + "arena", v.arena);
            c.set(p + "stufe", v.stufe.id());
            c.set(p + "tod", v.tod.id);
            c.set(p + "leben", v.leben);
            c.set(p + "zeit", v.zeitMinuten);
            c.set(p + "leer", v.leerSekunden);
            c.set(p + "spieler-min", v.spielerMin);
            c.set(p + "spieler-max", v.spielerMax);
            c.set(p + "loot", v.loot);
            c.set(p + "abklingzeit", v.abklingzeitMinuten);
            c.set(p + "beschwoerung", v.beschwoerung);
            c.set(p + "statistik.siege", v.siege);
            c.set(p + "statistik.gescheitert", v.gescheitert);
            c.set(p + "statistik.beste-zeit", v.besteZeit);
            c.set(p + "statistik.letzte-rangliste", new ArrayList<>(v.letzteRangliste));
        }
        speichern(c, "raids.yml");
    }

    // ---------- Fragment-Tageslimit ----------

    void datenLaden() {
        daten = YamlConfiguration.loadConfiguration(datei("daten.yml"));
    }

    /** Erhöht den Tageszähler, wenn das Limit noch nicht erreicht ist. Liefert den neuen Stand oder -1. */
    int fragmentZaehlen(UUID spieler, int limit) {
        String heute = LocalDate.now().toString();
        String p = "fragmente." + spieler + ".";
        int anzahl = heute.equals(daten.getString(p + "tag")) ? daten.getInt(p + "anzahl") : 0;
        if (anzahl >= limit) {
            return -1;
        }
        daten.set(p + "tag", heute);
        daten.set(p + "anzahl", anzahl + 1);
        speichern(daten, "daten.yml");
        return anzahl + 1;
    }

    void allesSpeichern() {
        arenenSpeichern();
        raidsSpeichern();
    }

    private void speichern(YamlConfiguration c, String name) {
        try {
            if (!pl.getDataFolder().exists()) {
                pl.getDataFolder().mkdirs();
            }
            c.save(datei(name));
        } catch (IOException e) {
            pl.getLogger().log(Level.WARNING, "Konnte " + name + " nicht speichern", e);
        }
    }

    Collection<String> arenaNamen() {
        List<String> l = new ArrayList<>();
        for (Arena a : arenen.values()) {
            l.add(a.name);
        }
        return l;
    }

    Collection<String> raidNamen() {
        List<String> l = new ArrayList<>();
        for (RaidVorlage r : raids.values()) {
            l.add(r.name);
        }
        return l;
    }
}
