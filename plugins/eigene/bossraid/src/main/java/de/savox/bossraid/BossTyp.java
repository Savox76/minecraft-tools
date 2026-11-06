package de.savox.bossraid;

import org.bukkit.boss.BarColor;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.entity.EntityType;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/** Ein Boss aus bosse.yml. */
final class BossTyp {
    record Schwaeche(String art, String wert, double faktor) {
    }

    record LootTopf(double chance, List<String> eintraege) {
    }

    final String id;
    String name;
    EntityType basis;
    double groesse, leben, schaden, ruestung, tempo, rueckstoss;
    int bossStufe;
    BarColor farbe;
    String beschwoerung;
    String phase2Text, phase3Text, auftrittText, siegText, flopText;
    final List<Faehigkeit> faehigkeiten = new ArrayList<>();
    final List<Schwaeche> schwaechen = new ArrayList<>();
    int erfahrung;
    final List<String> sicher = new ArrayList<>();
    LootTopf selten, episch, trophaee;

    BossTyp(String id) {
        this.id = id;
    }

    static BossTyp laden(String id, ConfigurationSection s) {
        BossTyp b = new BossTyp(id);
        b.name = s.getString("name", id);
        try {
            b.basis = EntityType.valueOf(s.getString("basis", "ZOMBIE").toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            b.basis = EntityType.ZOMBIE;
        }
        b.groesse = s.getDouble("groesse", 1.0);
        b.leben = s.getDouble("leben", 500);
        b.schaden = s.getDouble("schaden", 3);
        b.ruestung = s.getDouble("ruestung", 0);
        b.tempo = s.getDouble("tempo", 1.0);
        b.rueckstoss = s.getDouble("rueckstoss-schutz", 0.5);
        b.bossStufe = s.getInt("boss-stufe", 1);
        try {
            b.farbe = BarColor.valueOf(s.getString("farbe", "PURPLE").toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            b.farbe = BarColor.PURPLE;
        }
        b.beschwoerung = s.getString("beschwoerung");
        b.auftrittText = s.getString("texte.auftritt");
        b.phase2Text = s.getString("texte.phase2");
        b.phase3Text = s.getString("texte.phase3");
        b.siegText = s.getString("texte.sieg");
        b.flopText = s.getString("texte.gescheitert");
        for (Map<?, ?> m : s.getMapList("faehigkeiten")) {
            b.faehigkeiten.add(new Faehigkeit(m));
        }
        for (Map<?, ?> m : s.getMapList("schwaechen")) {
            Object art = m.get("art"), wert = m.get("wert"), faktor = m.get("faktor");
            double f = faktor instanceof Number n ? n.doubleValue() : 1.5;
            b.schwaechen.add(new Schwaeche(String.valueOf(art).toLowerCase(Locale.ROOT), wert == null ? "" : String.valueOf(wert), f));
        }
        ConfigurationSection l = s.getConfigurationSection("loot");
        if (l != null) {
            b.erfahrung = l.getInt("erfahrung", 0);
            b.sicher.addAll(l.getStringList("sicher"));
            b.selten = topf(l.getConfigurationSection("selten"));
            b.episch = topf(l.getConfigurationSection("episch"));
            b.trophaee = topf(l.getConfigurationSection("trophaee"));
        }
        return b;
    }

    private static LootTopf topf(ConfigurationSection s) {
        if (s == null) {
            return null;
        }
        return new LootTopf(s.getDouble("chance", 0), new ArrayList<>(s.getStringList("eintraege")));
    }

    String stufeText() {
        return switch (bossStufe) {
            case 1 -> "I";
            case 2 -> "II";
            case 3 -> "III";
            default -> "IV";
        };
    }
}
