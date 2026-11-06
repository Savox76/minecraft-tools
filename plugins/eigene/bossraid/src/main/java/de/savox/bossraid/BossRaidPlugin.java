package de.savox.bossraid;

import org.bukkit.Bukkit;
import org.bukkit.World;
import org.bukkit.command.PluginCommand;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Entity;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/** BossRaid: Boss-Kämpfe mit Arena, Beschwörung am Altar und Raid-Vorlagen. */
public final class BossRaidPlugin extends JavaPlugin {
    private static BossRaidPlugin instanz;

    final Einstellungen einst = new Einstellungen();
    final Map<String, BossTyp> bosse = new LinkedHashMap<>();
    Speicher speicher;
    Gegenstaende gegenstaende;
    Kaempfe kaempfe;
    Graeber graeber;
    TempBloecke temp;
    Befehle befehle;

    static BossRaidPlugin get() {
        return instanz;
    }

    @Override
    public void onEnable() {
        instanz = this;
        Keys.init(this);
        saveDefaultConfig();
        if (!new File(getDataFolder(), "bosse.yml").exists()) {
            saveResource("bosse.yml", false);
        }
        temp = new TempBloecke(this);
        temp.wiederherstellen();
        speicher = new Speicher(this);
        gegenstaende = new Gegenstaende(this);
        laden();
        graeber = new Graeber(this);
        kaempfe = new Kaempfe(this);
        befehle = new Befehle(this);
        for (String c : new String[]{"bossarena", "raid"}) {
            PluginCommand pc = getCommand(c);
            if (pc != null) {
                pc.setExecutor(befehle);
                pc.setTabCompleter(befehle);
            }
        }
        Bukkit.getPluginManager().registerEvents(new KampfListener(this), this);
        Bukkit.getPluginManager().registerEvents(new GegenstandListener(this), this);
        // Nach einem Absturz: Tore öffnen, Kerzen löschen, übrig gebliebene Bosse und Helfer entfernen
        for (Arena a : speicher.arenen.values()) {
            a.torOeffnen();
            a.kerzenLoeschen();
        }
        int weg = 0;
        for (World w : Bukkit.getWorlds()) {
            for (Entity e : w.getEntities()) {
                if (aufraeumen(e)) {
                    weg++;
                }
            }
        }
        if (weg > 0) {
            getLogger().info(weg + " übrig gebliebene Bosse oder Helfer entfernt.");
        }
        getLogger().info("BossRaid bereit: " + bosse.size() + " Bosse, " + speicher.arenen.size() + " Arenen, "
                + speicher.raids.size() + " Raids, " + graeber.anzahl() + " Grabtruhen.");
    }

    /** Liest config.yml, bosse.yml, Arenen und Raids (auch für /raid neuladen). */
    void laden() {
        reloadConfig();
        einst.laden(getConfig());
        YamlConfiguration b = YamlConfiguration.loadConfiguration(new File(getDataFolder(), "bosse.yml"));
        var standard = getResource("bosse.yml");
        if (standard != null) {
            b.setDefaults(YamlConfiguration.loadConfiguration(new InputStreamReader(standard, StandardCharsets.UTF_8)));
        }
        bosse.clear();
        ConfigurationSection bs = b.getConfigurationSection("bosse");
        if (bs != null) {
            for (String id : bs.getKeys(false)) {
                ConfigurationSection s = bs.getConfigurationSection(id);
                if (s != null) {
                    bosse.put(id.toLowerCase(Locale.ROOT), BossTyp.laden(id.toLowerCase(Locale.ROOT), s));
                }
            }
        }
        gegenstaende.laden(b.getConfigurationSection("gegenstaende"), b.getConfigurationSection("fragmente"));
        gegenstaende.rezepteAnmelden();
        speicher.arenenLaden();
        speicher.raidsLaden();
        speicher.datenLaden();
    }

    /** Entfernt Bosse, Helfer, Würfe und Begleiter, die zu keinem laufenden Kampf gehören. */
    boolean aufraeumen(Entity e) {
        boolean weg = false;
        if (Keys.hat(e, Keys.BOSS)) {
            weg = kaempfe == null || kaempfe.mitBoss(e) == null;
        } else if (Keys.hat(e, Keys.HELFER) || Keys.hat(e, Keys.WURF) || Keys.hat(e, Keys.PFEIL)) {
            Kampf k = kaempfe == null ? null : kaempfe.an(e.getLocation());
            weg = k == null || (Keys.hat(e, Keys.HELFER) && !k.istHelfer(e));
        } else if (Keys.hat(e, Keys.BEGLEITER)) {
            weg = true;
        }
        if (weg) {
            e.remove();
        }
        return weg;
    }

    @Override
    public void onDisable() {
        if (kaempfe != null) {
            kaempfe.alleAbbrechen("Der Server wird neu gestartet.");
        }
        if (temp != null) {
            temp.allesZurueck();
        }
        if (graeber != null) {
            graeber.speichern();
        }
        if (speicher != null) {
            speicher.allesSpeichern();
        }
    }
}
