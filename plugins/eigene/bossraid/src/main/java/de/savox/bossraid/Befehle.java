package de.savox.bossraid;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.block.Block;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabExecutor;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.scheduler.BukkitRunnable;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** /bossarena (Arenen einrichten) und /raid (Vorlagen, Start, Beitreten, Ranglisten). */
final class Befehle implements TabExecutor {
    private final BossRaidPlugin pl;
    /** Torauswahl je Admin: Arena und markierte Blöcke. */
    private final Map<UUID, String> torArena = new HashMap<>();
    private final Map<UUID, Set<Block>> torBloecke = new HashMap<>();

    Befehle(BossRaidPlugin pl) {
        this.pl = pl;
    }

    @Override
    public boolean onCommand(CommandSender s, Command cmd, String label, String[] a) {
        if (cmd.getName().equalsIgnoreCase("bossarena")) {
            arena(s, a);
        } else {
            raid(s, a);
        }
        return true;
    }

    private static String arg(String[] a, int i) {
        return a.length > i ? a[i] : null;
    }

    private boolean admin(CommandSender s) {
        if (s.hasPermission("bossraid.admin")) {
            return true;
        }
        Txt.an(s, "&cDas dürfen nur Admins.");
        return false;
    }

    private Player spieler(CommandSender s) {
        if (s instanceof Player p) {
            return p;
        }
        Txt.an(s, "&cDas geht nur im Spiel.");
        return null;
    }

    // ===================== /bossarena =====================

    private void arena(CommandSender s, String[] a) {
        if (!admin(s)) {
            return;
        }
        String sub = arg(a, 0) == null ? "hilfe" : a[0].toLowerCase(Locale.ROOT);
        String name = arg(a, 1);
        Arena ar = pl.speicher.arena(name);
        switch (sub) {
            case "erstellen" -> {
                Player p = spieler(s);
                if (p == null) {
                    return;
                }
                if (name == null || !name.matches("[A-Za-z0-9_-]{1,32}")) {
                    Txt.an(s, "&c/bossarena erstellen <name> &7(Buchstaben, Zahlen, - und _)");
                    return;
                }
                if (ar != null) {
                    Txt.an(s, "&cDie Arena &f" + name + " &cgibt es schon.");
                    return;
                }
                Location l = p.getLocation().getBlock().getLocation().add(0.5, 0, 0.5);
                Arena neu = new Arena(name);
                neu.welt = l.getWorld().getName();
                neu.x = l.getX();
                neu.y = l.getY();
                neu.z = l.getZ();
                pl.speicher.arenen.put(Speicher.key(name), neu);
                pl.speicher.arenenSpeichern();
                Txt.an(s, "&aArena &f" + name + " &aerstellt. &7Mitte ist hier, Radius fest &f" + pl.einst.radius + " Blöcke&7.");
                Txt.an(s, "&7Weiter: &f/bossarena bossspawn " + name + "&7, &f/bossarena eingang " + name
                        + "&7, &f/bossarena altar " + name + " <raid>&7, optional &f/bossarena tor " + name);
                zeigen(neu);
            }
            case "bossspawn", "eingang" -> {
                Player p = spieler(s);
                if (p == null || !gibtEs(s, ar, name)) {
                    return;
                }
                if (!ar.enthaelt(p.getLocation())) {
                    Txt.an(s, "&cDu stehst nicht in der Arena &f" + ar.name + "&c.");
                    return;
                }
                if (sub.equals("bossspawn")) {
                    ar.bossSpawn = p.getLocation().clone();
                } else {
                    ar.eingang = p.getLocation().clone();
                }
                pl.speicher.arenenSpeichern();
                Txt.an(s, "&a" + (sub.equals("bossspawn") ? "Boss-Spawn" : "Eingang") + " von &f" + ar.name + " &agesetzt.");
            }
            case "altar" -> {
                Player p = spieler(s);
                if (p == null || !gibtEs(s, ar, name)) {
                    return;
                }
                RaidVorlage r = pl.speicher.raid(arg(a, 2));
                if (r == null) {
                    Txt.an(s, "&c/bossarena altar " + ar.name + " <raid> &7– den Raid zuerst mit &f/raid erstellen &7anlegen.");
                    return;
                }
                Block b = p.getTargetBlockExact(6);
                if (b == null || b.getType().isAir() || !ar.enthaelt(b.getLocation())) {
                    Txt.an(s, "&cSchau auf einen Block in der Arena (höchstens 6 Blöcke entfernt), der der Altar werden soll.");
                    return;
                }
                ar.hatAltar = true;
                ar.altarX = b.getX();
                ar.altarY = b.getY();
                ar.altarZ = b.getZ();
                ar.altarRaid = r.name;
                List<Block> belegt = ar.kerzenSetzen();
                pl.speicher.arenenSpeichern();
                Txt.an(s, "&aAltar gesetzt und mit dem Raid &f" + r.name + " &averbunden. &7Die vier Kerzen stehen 3 Blöcke schräg daneben.");
                for (Block k : belegt) {
                    Txt.an(s, "&eKerzenplatz belegt bei &f" + k.getX() + " " + k.getY() + " " + k.getZ() + " &e– bitte frei machen und &f/bossarena altar &eerneut ausführen.");
                }
            }
            case "tor" -> {
                Player p = spieler(s);
                if (p == null || !gibtEs(s, ar, name)) {
                    return;
                }
                String was = arg(a, 2) == null ? "" : a[2].toLowerCase(Locale.ROOT);
                switch (was) {
                    case "speichern" -> torSpeichern(p, ar);
                    case "loeschen" -> {
                        ar.tor.clear();
                        pl.speicher.arenenSpeichern();
                        Txt.an(s, "&aTor von &f" + ar.name + " &agelöscht.");
                    }
                    default -> {
                        torArena.put(p.getUniqueId(), Speicher.key(ar.name));
                        torBloecke.put(p.getUniqueId(), new LinkedHashSet<>());
                        ItemStack stab = new ItemStack(Material.BLAZE_ROD);
                        ItemMeta m = stab.getItemMeta();
                        m.displayName(Txt.komp("&6Torstab (" + ar.name + ")"));
                        m.getPersistentDataContainer().set(Keys.TORSTAB, PersistentDataType.BYTE, (byte) 1);
                        stab.setItemMeta(m);
                        p.getInventory().addItem(stab);
                        Txt.an(s, "&7Baue das Tor im &fgeschlossenen &7Zustand (z. B. Eisengitter). Dann klicke jeden Tor-Block mit dem &6Torstab &7an.");
                        Txt.an(s, "&7Fertig: &f/bossarena tor " + ar.name + " speichern &7– das Tor öffnet sich dann und schließt sich zu jedem Kampf.");
                    }
                }
            }
            case "zeigen" -> {
                if (gibtEs(s, ar, name)) {
                    zeigen(ar);
                    Txt.an(s, "&7Der Rand der Arena leuchtet 15 Sekunden.");
                }
            }
            case "info" -> {
                if (!gibtEs(s, ar, name)) {
                    return;
                }
                Txt.an(s, "&6Arena &f" + ar.name + "&7: Welt " + ar.welt + ", Mitte " + (int) ar.x + " " + (int) ar.y + " " + (int) ar.z
                        + ", Radius " + pl.einst.radius);
                Txt.an(s, "&7Boss-Spawn: " + ort(ar.bossSpawn) + "&7, Eingang: " + ort(ar.eingang));
                Txt.an(s, "&7Altar: " + (ar.hatAltar ? "&f" + ar.altarX + " " + ar.altarY + " " + ar.altarZ + " &7→ Raid &f" + ar.altarRaid : "&ckeiner")
                        + "&7, Tor: &f" + ar.tor.size() + " Blöcke");
                long rest = ar.abklingBis - System.currentTimeMillis();
                if (rest > 0) {
                    Txt.an(s, "&7Altar ruht noch &f" + Txt.zeit((int) (rest / 1000)));
                }
                Txt.an(s, ar.bereit() ? "&aStartklar." : "&cNoch nicht startklar: Boss-Spawn und Eingang setzen.");
            }
            case "liste" -> {
                if (pl.speicher.arenen.isEmpty()) {
                    Txt.an(s, "&7Noch keine Arenen. &f/bossarena erstellen <name>");
                }
                for (Arena x : pl.speicher.arenen.values()) {
                    Txt.an(s, "&f" + x.name + " &7(" + x.welt + " " + (int) x.x + " " + (int) x.y + " " + (int) x.z + ") "
                            + (x.bereit() ? "&astartklar" : "&cunvollständig"));
                }
            }
            case "loeschen" -> {
                if (!gibtEs(s, ar, name)) {
                    return;
                }
                if (pl.kaempfe.belegt(ar)) {
                    Txt.an(s, "&cIn der Arena läuft gerade ein Kampf oder Ritual.");
                    return;
                }
                pl.speicher.arenen.remove(Speicher.key(ar.name));
                pl.speicher.arenenSpeichern();
                Txt.an(s, "&aArena &f" + ar.name + " &agelöscht.");
            }
            default -> {
                Txt.an(s, "&6/bossarena &7– Arenen einrichten");
                Txt.an(s, "&f erstellen <name> &7Mitte = deine Position, Radius fest " + pl.einst.radius);
                Txt.an(s, "&f bossspawn <name> &7| &feingang <name> &7Stelle, an der du stehst");
                Txt.an(s, "&f altar <name> <raid> &7Block, auf den du schaust");
                Txt.an(s, "&f tor <name> [speichern|loeschen] &7Tor mit dem Torstab markieren");
                Txt.an(s, "&f zeigen | info | liste | loeschen");
            }
        }
    }

    private boolean gibtEs(CommandSender s, Arena ar, String name) {
        if (ar == null) {
            Txt.an(s, "&cArena " + (name == null ? "fehlt" : "&f" + name + " &cgibt es nicht") + "&c. &7/bossarena liste");
            return false;
        }
        return true;
    }

    private static String ort(Location l) {
        return l == null ? "&cfehlt" : "&f" + l.getBlockX() + " " + l.getBlockY() + " " + l.getBlockZ();
    }

    private void zeigen(Arena ar) {
        new BukkitRunnable() {
            int i;

            @Override
            public void run() {
                if (i++ >= 15 || ar.world() == null) {
                    cancel();
                    return;
                }
                int r = pl.einst.radius;
                for (int g = 0; g < 360; g += 3) {
                    double w = Math.toRadians(g);
                    Location l = new Location(ar.world(), ar.x + Math.cos(w) * r, ar.y + 0.5, ar.z + Math.sin(w) * r);
                    ar.world().spawnParticle(Particle.HAPPY_VILLAGER, l, 1, 0, 0.3, 0, 0);
                }
            }
        }.runTaskTimer(pl, 0, 20);
    }

    void torstabKlick(Player p, Block b) {
        Set<Block> sel = torBloecke.get(p.getUniqueId());
        if (sel == null) {
            Txt.an(p, "&7Starte die Auswahl zuerst mit &f/bossarena tor <arena>&7.");
            return;
        }
        if (b.getType().isAir()) {
            return;
        }
        if (sel.remove(b)) {
            Txt.an(p, "&7Block entfernt (&f" + sel.size() + " &7markiert).");
        } else {
            sel.add(b);
            b.getWorld().spawnParticle(Particle.HAPPY_VILLAGER, b.getLocation().add(0.5, 0.5, 0.5), 10, 0.3, 0.3, 0.3, 0);
            Txt.an(p, "&aBlock markiert (&f" + sel.size() + " &a markiert).");
        }
    }

    private void torSpeichern(Player p, Arena ar) {
        Set<Block> sel = torBloecke.get(p.getUniqueId());
        if (sel == null || sel.isEmpty() || !Speicher.key(ar.name).equals(torArena.get(p.getUniqueId()))) {
            Txt.an(p, "&cKeine Tor-Blöcke markiert. &7Erst &f/bossarena tor " + ar.name + " &7und dann mit dem Torstab klicken.");
            return;
        }
        ar.tor.clear();
        for (Block b : sel) {
            ar.tor.add(new Arena.TorBlock(b.getX(), b.getY(), b.getZ(), b.getBlockData().getAsString()));
        }
        ar.torOeffnen();
        pl.speicher.arenenSpeichern();
        torBloecke.remove(p.getUniqueId());
        torArena.remove(p.getUniqueId());
        Txt.an(p, "&aTor mit &f" + ar.tor.size() + " &aBlöcken gespeichert und geöffnet. Es schließt sich zu jedem Kampf.");
    }

    // ===================== /raid =====================

    private void raid(CommandSender s, String[] a) {
        String sub = arg(a, 0) == null ? "hilfe" : a[0].toLowerCase(Locale.ROOT);
        String name = arg(a, 1);
        RaidVorlage r = pl.speicher.raid(name);
        switch (sub) {
            case "beitreten" -> {
                Player p = spieler(s);
                if (p == null) {
                    return;
                }
                Kampf ziel = null;
                for (Kampf k : pl.kaempfe.alle()) {
                    if (k.zustand == Kampf.Zustand.SAMMELN && (name == null || k.raid.name.equalsIgnoreCase(name))) {
                        ziel = k;
                        break;
                    }
                }
                if (ziel == null) {
                    Txt.an(s, "&7Gerade kann man keinem Raid beitreten. Raids startet ein Admin oder ein Ritual am Altar.");
                    return;
                }
                ziel.beitreten(p);
            }
            case "top", "info" -> {
                if (r == null) {
                    Txt.an(s, "&c/raid " + sub + " <raid> &7– &f/raid liste &7zeigt alle Raids.");
                    return;
                }
                BossTyp b = pl.bosse.get(r.boss);
                Txt.an(s, "&6Raid &f" + r.name + "&7: " + (b == null ? "&ckein Boss" : Txt.c(b.name)) + " &7in &f" + r.arena
                        + "&7, Stufe &f" + r.stufe.id());
                if (sub.equals("info")) {
                    Txt.an(s, "&7Tod: &f" + r.tod.id + "&7, Leben: &f" + r.leben + "&7, Zeit: &f" + r.zeitMinuten + " min&7, leer: &f"
                            + r.leerSekunden + " s&7, Spieler: &f" + r.spielerMin + "-" + r.spielerMax + "&7, Loot: &f×" + r.loot
                            + "&7, Abklingzeit: &f" + r.abklingzeitMinuten + " min&7, Beschwörung: &f" + (r.beschwoerung ? "an" : "aus"));
                }
                Txt.an(s, "&7Siege: &a" + r.siege + "&7, gescheitert: &c" + r.gescheitert
                        + (r.besteZeit > 0 ? "&7, Bestzeit: &f" + Txt.zeit(r.besteZeit) : ""));
                for (String z : r.letzteRangliste) {
                    Txt.an(s, "&7  " + z);
                }
            }
            case "liste" -> {
                if (pl.speicher.raids.isEmpty()) {
                    Txt.an(s, "&7Noch keine Raids.");
                }
                for (RaidVorlage x : pl.speicher.raids.values()) {
                    BossTyp b = pl.bosse.get(x.boss);
                    Txt.an(s, "&f" + x.name + " &7– " + (b == null ? "?" : Txt.c(b.name)) + " &7in " + x.arena + ", " + x.stufe.id());
                }
            }
            case "bosse" -> {
                for (BossTyp b : pl.bosse.values()) {
                    Txt.an(s, Txt.c(b.name) + " &7(" + b.id + ", Stufe " + b.stufeText() + ") – beschwören mit &f"
                            + Txt.c(pl.gegenstaende.name(b.beschwoerung == null ? "" : b.beschwoerung)));
                }
            }
            case "rezepte" -> {
                Txt.an(s, "&6Rezepte &7(Werkbank, 8 Fragmente rund um den Kern):");
                for (Gegenstaende.RezeptInfo z : pl.gegenstaende.rezeptInfos) {
                    s.sendMessage(Txt.komp(Txt.PREFIX).append(pl.gegenstaende.rezeptText(z)));
                }
                Txt.an(s, "&7Fragmente fallen selten von Monstern (höchstens &f" + pl.einst.fragmentTageslimit + " &7pro Tag), nicht in Arenen.");
            }
            case "erstellen" -> {
                if (!admin(s)) {
                    return;
                }
                if (name == null || !name.matches("[A-Za-z0-9_-]{1,32}")) {
                    Txt.an(s, "&c/raid erstellen <name> [boss] [arena]");
                    return;
                }
                if (r != null) {
                    Txt.an(s, "&cDen Raid &f" + name + " &cgibt es schon.");
                    return;
                }
                RaidVorlage neu = new RaidVorlage(name);
                if (arg(a, 2) != null && pl.bosse.containsKey(a[2].toLowerCase(Locale.ROOT))) {
                    neu.boss = a[2].toLowerCase(Locale.ROOT);
                }
                if (arg(a, 3) != null && pl.speicher.arena(a[3]) != null) {
                    neu.arena = pl.speicher.arena(a[3]).name;
                }
                pl.speicher.raids.put(Speicher.key(name), neu);
                pl.speicher.raidsSpeichern();
                Txt.an(s, "&aRaid &f" + name + " &aangelegt. &7Einstellen mit &f/raid set " + name + " <feld> <wert>&7, prüfen mit &f/raid info " + name);
            }
            case "set" -> {
                if (!admin(s)) {
                    return;
                }
                if (r == null || arg(a, 3) == null) {
                    Txt.an(s, "&c/raid set <raid> <feld> <wert>");
                    Txt.an(s, "&7Felder: boss, arena, stufe (leicht|normal|schwer), tod (normal|grabtruhe|behalten), leben, zeit (Minuten), "
                            + "leer (Sekunden), spieler (z. B. 2-8), loot (z. B. 1.5), abklingzeit (Minuten), beschwoerung (an|aus)");
                    return;
                }
                String fehler = setzen(r, a[2].toLowerCase(Locale.ROOT), a[3]);
                if (fehler != null) {
                    Txt.an(s, "&c" + fehler);
                    return;
                }
                pl.speicher.raidsSpeichern();
                Txt.an(s, "&a" + a[2] + " &avon &f" + r.name + " &aist jetzt &f" + a[3] + "&a.");
            }
            case "loeschen" -> {
                if (!admin(s) || r == null) {
                    if (r == null) {
                        Txt.an(s, "&c/raid loeschen <raid>");
                    }
                    return;
                }
                pl.speicher.raids.remove(Speicher.key(r.name));
                pl.speicher.raidsSpeichern();
                Txt.an(s, "&aRaid &f" + r.name + " &agelöscht.");
            }
            case "start" -> {
                if (!admin(s)) {
                    return;
                }
                if (r == null) {
                    Txt.an(s, "&c/raid start <raid> [sofort]");
                    return;
                }
                String fehler = pl.kaempfe.pruefen(r);
                if (fehler != null) {
                    Txt.an(s, "&c" + fehler);
                    return;
                }
                boolean sofort = "sofort".equalsIgnoreCase(arg(a, 2));
                if (sofort) {
                    int drin = pl.speicher.arena(r.arena).spielerDrin().size();
                    if (drin < Math.max(1, r.spielerMin)) {
                        Txt.an(s, "&cZu wenige Spieler in der Arena (" + drin + " von mindestens " + Math.max(1, r.spielerMin) + ").");
                        return;
                    }
                }
                pl.kaempfe.adminStart(r, sofort);
            }
            case "stopp" -> {
                if (!admin(s)) {
                    return;
                }
                int n = 0;
                for (Kampf k : pl.kaempfe.alle()) {
                    if (name == null || k.raid.name.equalsIgnoreCase(name) || k.arena.name.equalsIgnoreCase(name)) {
                        k.scheitern("Von einem Admin gestoppt.");
                        n++;
                    }
                }
                Txt.an(s, n == 0 ? "&7Kein passender Raid läuft." : "&a" + n + " Raid(s) gestoppt.");
            }
            case "gegenstand" -> {
                if (!admin(s)) {
                    return;
                }
                String id = name == null ? null : name.toLowerCase(Locale.ROOT);
                if (id == null || !pl.gegenstaende.defs.containsKey(id)) {
                    Txt.an(s, "&c/raid gegenstand <id> [anzahl] [verflucht] [spieler] &7– IDs: &f" + String.join(", ", pl.gegenstaende.defs.keySet()));
                    return;
                }
                int anzahl = 1;
                boolean verflucht = false;
                Player ziel = s instanceof Player p ? p : null;
                for (int i = 2; i < a.length; i++) {
                    if (a[i].matches("\\d+")) {
                        anzahl = Math.min(64, Integer.parseInt(a[i]));
                    } else if (a[i].equalsIgnoreCase("verflucht")) {
                        verflucht = true;
                    } else if (Bukkit.getPlayerExact(a[i]) != null) {
                        ziel = Bukkit.getPlayerExact(a[i]);
                    }
                }
                if (ziel == null) {
                    Txt.an(s, "&cKein Spieler angegeben.");
                    return;
                }
                ItemStack it = pl.gegenstaende.erzeuge(id, anzahl, verflucht && pl.gegenstaende.art(id).equals("beschwoerung"));
                ziel.getInventory().addItem(it);
                Txt.an(s, "&a" + anzahl + "× " + Txt.c(pl.gegenstaende.name(id)) + " &aan &f" + ziel.getName() + " &agegeben.");
            }
            case "neuladen" -> {
                if (!admin(s)) {
                    return;
                }
                if (pl.kaempfe.irgendwas()) {
                    Txt.an(s, "&cWährend ein Kampf oder Ritual läuft, lädt das Plugin nicht neu.");
                    return;
                }
                pl.laden();
                Txt.an(s, "&aConfig, Bosse, Arenen und Raids neu geladen.");
            }
            default -> {
                Txt.an(s, "&6/raid &7– Boss-Raids");
                Txt.an(s, "&f beitreten &7| &ftop <raid> &7| &finfo <raid> &7| &fliste &7| &fbosse &7| &frezepte");
                if (s.hasPermission("bossraid.admin")) {
                    Txt.an(s, "&f erstellen <name> [boss] [arena] &7| &fset <raid> <feld> <wert> &7| &floeschen <raid>");
                    Txt.an(s, "&f start <raid> [sofort] &7| &fstopp [raid|arena] &7| &fgegenstand <id> [anzahl] [verflucht] [spieler] &7| &fneuladen");
                }
            }
        }
    }

    private String setzen(RaidVorlage r, String feld, String wert) {
        try {
            switch (feld) {
                case "boss" -> {
                    if (!pl.bosse.containsKey(wert.toLowerCase(Locale.ROOT))) {
                        return "Unbekannter Boss. /raid bosse";
                    }
                    r.boss = wert.toLowerCase(Locale.ROOT);
                }
                case "arena" -> {
                    Arena ar = pl.speicher.arena(wert);
                    if (ar == null) {
                        return "Unbekannte Arena. /bossarena liste";
                    }
                    r.arena = ar.name;
                }
                case "stufe" -> {
                    Stufe st = Stufe.von(wert);
                    if (st == null) {
                        return "Stufe: leicht, normal oder schwer";
                    }
                    r.stufe = st;
                }
                case "tod" -> {
                    Todesregel t = Todesregel.von(wert);
                    if (t == null) {
                        return "Tod: normal, grabtruhe oder behalten";
                    }
                    r.tod = t;
                }
                case "leben" -> r.leben = bereich(Integer.parseInt(wert), 1, 99);
                case "zeit" -> r.zeitMinuten = bereich(Integer.parseInt(wert), 1, 120);
                case "leer" -> r.leerSekunden = bereich(Integer.parseInt(wert), 5, 600);
                case "spieler" -> {
                    String[] p = wert.split("-");
                    int min = Integer.parseInt(p[0]);
                    int max = p.length > 1 ? Integer.parseInt(p[1]) : Math.max(min, r.spielerMax);
                    if (min < 1 || max < min) {
                        return "Spieler: z. B. 2-8 (mindestens 1)";
                    }
                    r.spielerMin = min;
                    r.spielerMax = max;
                }
                case "loot" -> {
                    double d = Double.parseDouble(wert.replace(',', '.'));
                    if (d < 0 || d > 10) {
                        return "Loot-Faktor zwischen 0 und 10";
                    }
                    r.loot = d;
                }
                case "abklingzeit" -> r.abklingzeitMinuten = bereich(Integer.parseInt(wert), 0, 10080);
                case "beschwoerung" -> {
                    if (!wert.equalsIgnoreCase("an") && !wert.equalsIgnoreCase("aus")) {
                        return "beschwoerung: an oder aus";
                    }
                    r.beschwoerung = wert.equalsIgnoreCase("an");
                }
                default -> {
                    return "Unbekanntes Feld. /raid set zeigt alle Felder.";
                }
            }
        } catch (NumberFormatException e) {
            return "Das ist keine gültige Zahl: " + wert;
        }
        return null;
    }

    private static int bereich(int x, int min, int max) {
        if (x < min || x > max) {
            throw new NumberFormatException();
        }
        return x;
    }

    // ===================== Tab =====================

    @Override
    public List<String> onTabComplete(CommandSender s, Command cmd, String label, String[] a) {
        boolean adm = s.hasPermission("bossraid.admin");
        List<String> opt = new ArrayList<>();
        if (cmd.getName().equalsIgnoreCase("bossarena")) {
            if (a.length == 1) {
                opt.addAll(List.of("erstellen", "bossspawn", "eingang", "altar", "tor", "zeigen", "info", "liste", "loeschen"));
            } else if (a.length == 2 && !a[0].equalsIgnoreCase("erstellen") && !a[0].equalsIgnoreCase("liste")) {
                opt.addAll(pl.speicher.arenaNamen());
            } else if (a.length == 3 && a[0].equalsIgnoreCase("altar")) {
                opt.addAll(pl.speicher.raidNamen());
            } else if (a.length == 3 && a[0].equalsIgnoreCase("tor")) {
                opt.addAll(List.of("speichern", "loeschen"));
            }
        } else {
            if (a.length == 1) {
                opt.addAll(List.of("beitreten", "top", "info", "liste", "bosse", "rezepte"));
                if (adm) {
                    opt.addAll(List.of("erstellen", "set", "loeschen", "start", "stopp", "gegenstand", "neuladen"));
                }
            } else if (a.length == 2) {
                String sub = a[0].toLowerCase(Locale.ROOT);
                if (List.of("top", "info", "set", "loeschen", "start", "stopp", "beitreten").contains(sub)) {
                    opt.addAll(pl.speicher.raidNamen());
                } else if (sub.equals("gegenstand")) {
                    opt.addAll(pl.gegenstaende.defs.keySet());
                }
            } else if (a.length == 3) {
                String sub = a[0].toLowerCase(Locale.ROOT);
                if (sub.equals("set")) {
                    opt.addAll(List.of("boss", "arena", "stufe", "tod", "leben", "zeit", "leer", "spieler", "loot", "abklingzeit", "beschwoerung"));
                } else if (sub.equals("erstellen")) {
                    opt.addAll(pl.bosse.keySet());
                } else if (sub.equals("start")) {
                    opt.add("sofort");
                }
            } else if (a.length == 4) {
                String sub = a[0].toLowerCase(Locale.ROOT);
                if (sub.equals("erstellen")) {
                    opt.addAll(pl.speicher.arenaNamen());
                } else if (sub.equals("set")) {
                    opt.addAll(werte(a[2].toLowerCase(Locale.ROOT)));
                }
            }
        }
        String letzt = a.length == 0 ? "" : a[a.length - 1].toLowerCase(Locale.ROOT);
        opt.removeIf(o -> !o.toLowerCase(Locale.ROOT).startsWith(letzt));
        return opt;
    }

    private Collection<String> werte(String feld) {
        return switch (feld) {
            case "boss" -> pl.bosse.keySet();
            case "arena" -> pl.speicher.arenaNamen();
            case "stufe" -> List.of("leicht", "normal", "schwer");
            case "tod" -> List.of("normal", "grabtruhe", "behalten");
            case "beschwoerung" -> List.of("an", "aus");
            case "leben" -> List.of("1", "3", "5");
            case "zeit" -> List.of("10", "15", "20");
            case "leer" -> List.of("30", "60", "120");
            case "spieler" -> List.of("1-8", "2-8", "3-10");
            case "loot" -> List.of("1.0", "1.5", "2.0");
            case "abklingzeit" -> List.of("30", "60", "120");
            default -> Arrays.asList();
        };
    }
}
