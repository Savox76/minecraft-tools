package de.savox.bossraid;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.title.Title;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.FireworkEffect;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarStyle;
import org.bukkit.boss.BossBar;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.AbstractArrow;
import org.bukkit.entity.Arrow;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.FallingBlock;
import org.bukkit.entity.Firework;
import org.bukkit.entity.Item;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Mob;
import org.bukkit.entity.Player;
import org.bukkit.entity.Projectile;
import org.bukkit.entity.Slime;
import org.bukkit.entity.Tameable;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.inventory.EntityEquipment;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.PlayerInventory;
import org.bukkit.inventory.meta.FireworkMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.projectiles.ProjectileSource;
import org.bukkit.scheduler.BukkitRunnable;
import org.bukkit.scheduler.BukkitTask;
import org.bukkit.util.Vector;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.UUID;

/** Ein laufender Raid in einer Arena: vom Sammeln über den Auftritt bis Sieg oder Scheitern. */
final class Kampf {
    enum Zustand {SAMMELN, AUFTRITT, LAEUFT, BEENDET}

    static final class Teilnehmer {
        final UUID id;
        final String name;
        int leben;
        double schaden;
        boolean ausgeschieden;
        boolean geflohen;
        int unerreichbar;

        Teilnehmer(Player p, int leben) {
            this.id = p.getUniqueId();
            this.name = p.getName();
            this.leben = leben;
        }
    }

    private static final Random ZUFALL = new Random();

    final BossRaidPlugin pl;
    final Arena arena;
    final RaidVorlage raid;
    final BossTyp typ;
    final Stufe stufe;
    final boolean beschworen;
    final Map<UUID, Teilnehmer> teilnehmer = new LinkedHashMap<>();

    Zustand zustand;
    Mob boss;
    private BossBar bar;
    private BukkitTask task;
    private int t;                 // Ticks seit Beginn
    private int countdown;         // Sekunden für Sammeln/Auftritt
    private int startTick;
    private int phase = 1;
    private int restSek;
    private int leerSek = -1;
    private double lebenGesamt;    // gewünschte Lebenspunkte (kann über dem Höchstwert eines Wesens liegen)
    private double faktor = 1;     // gewünschte / echte Lebenspunkte des Wesens
    private final Map<Faehigkeit, Integer> bereitAb = new HashMap<>();
    private int beschaeftigtBis;
    private int verwundbarBis;
    private int letzterTreffer;
    private int letzterSpielerTreffer = -1000;
    private boolean heiltGerade;
    private boolean steinhautHart;
    private boolean steinhautAktiv;
    private int steinhautWechsel;
    private boolean steinhautGewarnt;
    private final List<UUID> helfer = new ArrayList<>();
    private final Map<Block, Integer> verstaerker = new LinkedHashMap<>();
    private double verstaerkerSchutz;
    private double verstaerkerHeilung;
    private final Map<UUID, Long> hinweisGesendet = new HashMap<>();

    Kampf(BossRaidPlugin pl, Arena arena, RaidVorlage raid, BossTyp typ, Stufe stufe, boolean beschworen) {
        this.pl = pl;
        this.arena = arena;
        this.raid = raid;
        this.typ = typ;
        this.stufe = stufe;
        this.beschworen = beschworen;
    }

    // ===================== Ablauf =====================

    /** Admin-Start: 60 Sekunden zum Beitreten. */
    void sammeln() {
        zustand = Zustand.SAMMELN;
        countdown = pl.einst.sammelnSekunden;
        Txt.alle("&6Raid &f" + raid.name + "&6: " + Txt.c(typ.name) + " &6(Stufe " + stufe.id() + ") in der Arena &f"
                + arena.name + "&6. Beitreten mit &f/raid beitreten &6(" + countdown + " s).");
        task = Bukkit.getScheduler().runTaskTimer(pl, this::tick, 10, 10);
    }

    boolean beitreten(Player p) {
        if (zustand != Zustand.SAMMELN) {
            Txt.an(p, "&cDer Raid läuft schon, Beitreten geht nur vor dem Start.");
            return false;
        }
        if (teilnehmer.containsKey(p.getUniqueId())) {
            Txt.an(p, "&7Du bist schon dabei.");
            return false;
        }
        if (teilnehmer.size() >= raid.spielerMax) {
            Txt.an(p, "&cDer Raid ist voll (" + raid.spielerMax + " Spieler).");
            return false;
        }
        teilnehmer.put(p.getUniqueId(), new Teilnehmer(p, raid.leben));
        p.teleport(arena.eingang);
        Txt.an(p, "&aDu bist dabei! &7Regel beim Tod: &f" + raid.tod.text + "&7, Leben: &f" + raid.leben + "&7.");
        return true;
    }

    /** Beginnt den Auftritt mit den angegebenen Spielern (nach Ritual oder Sammeln). */
    void auftritt(Collection<Player> spieler) {
        for (Player p : spieler) {
            if (teilnehmer.size() >= raid.spielerMax) {
                break;
            }
            teilnehmer.putIfAbsent(p.getUniqueId(), new Teilnehmer(p, raid.leben));
        }
        zustand = Zustand.AUFTRITT;
        countdown = pl.einst.auftrittSekunden;
        arena.torSchliessen();
        for (Player p : online()) {
            if (!arena.enthaelt(p)) {
                p.teleport(arena.eingang);
            }
            Txt.an(p, "&7Regel beim Tod: &f" + raid.tod.text + "&7. Leben: &f" + raid.leben + "&7. Zeit: &f" + raid.zeitMinuten + " Minuten&7.");
        }
        if (task == null) {
            task = Bukkit.getScheduler().runTaskTimer(pl, this::tick, 10, 10);
        }
    }

    private void tick() {
        t += 10;
        boolean sekunde = t % 20 == 0;
        switch (zustand) {
            case SAMMELN -> {
                if (!sekunde) {
                    return;
                }
                countdown--;
                if (countdown == 30 || countdown == 10) {
                    Txt.alle("&6Raid &f" + raid.name + "&6 startet in " + countdown + " s. &f/raid beitreten");
                }
                if (countdown <= 0) {
                    List<Player> dabei = new ArrayList<>(online());
                    for (Player p : arena.spielerDrin()) {
                        if (!dabei.contains(p)) {
                            dabei.add(p);
                        }
                    }
                    if (dabei.size() < raid.spielerMin) {
                        Txt.alle("&cRaid &f" + raid.name + "&c fällt aus: zu wenige Spieler (" + dabei.size() + " von mindestens " + raid.spielerMin + ").");
                        aufraeumen();
                        return;
                    }
                    auftritt(dabei);
                }
            }
            case AUFTRITT -> {
                if (!sekunde) {
                    return;
                }
                if (countdown > 0) {
                    Title ti = Title.title(Txt.komp(typ.name), Txt.komp("&7erscheint in &f" + countdown),
                            Title.Times.times(Duration.ZERO, Duration.ofMillis(1100), Duration.ZERO));
                    for (Player p : online()) {
                        p.showTitle(ti);
                        p.playSound(p.getLocation(), Sound.BLOCK_NOTE_BLOCK_BASEDRUM, 1f, 0.6f);
                    }
                    countdown--;
                } else {
                    bossErscheint();
                }
            }
            case LAEUFT -> laufen(sekunde);
            default -> {
            }
        }
    }

    private void bossErscheint() {
        Location ort = arena.bossSpawn.clone();
        World w = ort.getWorld();
        w.strikeLightningEffect(ort);
        w.playSound(ort, Sound.ENTITY_WITHER_SPAWN, 1.5f, 0.8f);
        int n = Math.max(1, teilnehmer.size());
        Einstellungen.StufenWerte sw = pl.einst.stufe(stufe);
        lebenGesamt = typ.leben * sw.leben() * (1 + pl.einst.lebenProSpieler * (n - 1));
        double echt = Math.min(lebenGesamt, pl.einst.maxLebenpunkteWesen);
        faktor = lebenGesamt / echt;
        Class<? extends Entity> klasse = typ.basis.getEntityClass();
        if (klasse == null || !Mob.class.isAssignableFrom(klasse)) {
            pl.getLogger().warning("Basis " + typ.basis + " ist kein Monster, nehme Zombie.");
            klasse = EntityType.ZOMBIE.getEntityClass();
        }
        Entity e = w.spawn(ort, klasse, (Entity x) -> {
            x.setPersistent(false);
            x.getPersistentDataContainer().set(Keys.BOSS, PersistentDataType.STRING, arena.name);
            x.customName(Txt.komp(typ.name));
            x.setCustomNameVisible(true);
            if (x instanceof Mob m) {
                m.setRemoveWhenFarAway(false);
                m.setCanPickupItems(false);
                EntityEquipment eq = m.getEquipment();
                if (eq != null) {
                    eq.setItemInMainHandDropChance(0);
                    eq.setItemInOffHandDropChance(0);
                    eq.setHelmetDropChance(0);
                    eq.setChestplateDropChance(0);
                    eq.setLeggingsDropChance(0);
                    eq.setBootsDropChance(0);
                }
            }
        });
        boss = (Mob) e;
        Attr.setze(boss, echt, Attr.LEBEN);
        boss.setHealth(echt);
        Attr.setze(boss, typ.schaden * 2 * sw.schaden(), Attr.SCHADEN);
        Attr.setze(boss, typ.ruestung, Attr.RUESTUNG);
        Attr.setze(boss, typ.rueckstoss, Attr.RUECKSTOSS);
        Attr.setze(boss, typ.groesse, Attr.GROESSE);
        Attr.setze(boss, 48, Attr.FOLGEN);
        double tempo = Attr.wert(boss, Attr.TEMPO);
        if (tempo > 0) {
            Attr.setze(boss, tempo * typ.tempo, Attr.TEMPO);
        }
        bar = Bukkit.createBossBar(Txt.c(typ.name), typ.farbe, BarStyle.SEGMENTED_10);
        for (Player p : online()) {
            bar.addPlayer(p);
            p.showTitle(Title.title(Txt.komp(typ.name), Txt.komp("&7Boss der Stufe " + typ.stufeText() + " · " + stufe.id()),
                    Title.Times.times(Duration.ofMillis(200), Duration.ofSeconds(2), Duration.ofMillis(500))));
        }
        if (typ.auftrittText != null) {
            Txt.an(online(), typ.auftrittText);
        }
        restSek = raid.zeitMinuten * 60;
        startTick = t;
        letzterTreffer = t;
        for (Faehigkeit f : typ.faehigkeiten) {
            bereitAb.put(f, t + f.alle * 20);
        }
        zustand = Zustand.LAEUFT;
        balkenAktualisieren();
    }

    private void laufen(boolean sekunde) {
        if (boss == null || !boss.isValid()) {
            if (boss != null && boss.isDead()) {
                return; // Tod wird über das Ereignis behandelt
            }
            scheitern("Der Boss ist verschwunden.");
            return;
        }
        if (sekunde) {
            restSek--;
            if (restSek == 300 || restSek == 60 || restSek == 10) {
                Txt.an(online(), "&eNoch &f" + Txt.zeit(restSek) + " &e, dann verschwindet " + Txt.c(typ.name) + "&e!");
            }
            if (restSek <= 0) {
                scheitern("Die Zeit ist abgelaufen.");
                return;
            }
            if (!leerPruefen()) {
                return;
            }
            phasePruefen();
            if (!arena.enthaelt(boss.getLocation())) {
                boss.teleport(arena.bossSpawn);
            }
            zielSetzen();
            unerreichbarePruefen();
            helferPruefen();
            if (!verstaerker.isEmpty()) {
                heilen(verstaerkerHeilung);
            }
            balkenAktualisieren();
        }
        if (leerSek >= 0) {
            return;
        }
        for (Faehigkeit f : typ.faehigkeiten) {
            if (!f.inPhase(phase)) {
                continue;
            }
            switch (f.art) {
                case "flucht" -> flucht(f);
                case "heilkreis" -> {
                    if (sekunde) {
                        heilkreis(f);
                    }
                }
                case "steinhaut" -> steinhaut(f);
                default -> {
                    if (t >= bereitAb.getOrDefault(f, 0) && t >= beschaeftigtBis) {
                        bereitAb.put(f, t + f.alle * 20);
                        beschaeftigtBis = t + (int) Math.round(f.warnung * 20) + 30;
                        faehigkeitStarten(f);
                        return;
                    }
                }
            }
        }
    }

    /** Liefert false, wenn der Kampf wegen fehlender Spieler pausiert oder endet. */
    private boolean leerPruefen() {
        int lebend = lebende().size();
        if (lebend == 0) {
            if (leerSek < 0) {
                leerSek = raid.leerSekunden;
                boss.setTarget(null);
                boss.setAware(false);
                boss.teleport(arena.bossSpawn);
                Txt.an(online(), "&eKein Spieler mehr am Leben in der Arena. &7" + Txt.c(typ.name)
                        + " &7verschwindet in &f" + leerSek + " s&7, wenn niemand zurückkommt.");
            }
            leerSek--;
            if (leerSek <= 0) {
                scheitern("Niemand ist mehr am Leben.");
            }
            balkenAktualisieren();
            return false;
        }
        if (leerSek >= 0) {
            leerSek = -1;
            boss.setAware(true);
            Txt.an(online(), "&aDer Kampf geht weiter!");
        }
        return true;
    }

    private void phasePruefen() {
        double anteil = boss.getHealth() / maxLeben();
        int neu = anteil <= 0.33 ? 3 : anteil <= 0.66 ? 2 : 1;
        if (neu <= phase) {
            return;
        }
        phase = neu;
        String text = phase == 2 ? typ.phase2Text : typ.phase3Text;
        Txt.an(online(), text != null ? text : "&c" + Txt.c(typ.name) + " &cwird stärker! &7(Phase " + phase + ")");
        for (Player p : online()) {
            p.playSound(p.getLocation(), Sound.ENTITY_ELDER_GUARDIAN_CURSE, 0.8f, 1f);
        }
        if (phase == 3) {
            double tempo = Attr.wert(boss, Attr.TEMPO);
            if (tempo > 0) {
                Attr.setze(boss, tempo * 1.2, Attr.TEMPO);
            }
        }
        boss.getWorld().spawnParticle(Particle.EXPLOSION, boss.getLocation().add(0, 1, 0), 3, 0.5, 0.5, 0.5, 0);
    }

    private void balkenAktualisieren() {
        if (bar == null || boss == null) {
            return;
        }
        double anteil = Math.max(0, Math.min(1, boss.getHealth() / maxLeben()));
        bar.setProgress(anteil);
        bar.setColor(phase == 1 ? typ.farbe : phase == 2 ? BarColor.YELLOW : BarColor.RED);
        String zusatz = leerSek >= 0 ? " §e· verschwindet in " + leerSek + " s" : " §7· §f" + Txt.zeit(restSek);
        bar.setTitle(Txt.c(typ.name) + " §7· Phase " + phase + zusatz);
        for (Player p : online()) {
            Teilnehmer x = teilnehmer(p);
            if (x != null && !x.geflohen && !bar.getPlayers().contains(p)) {
                bar.addPlayer(p);
            }
        }
    }

    // ===================== Spieler =====================

    Teilnehmer teilnehmer(Player p) {
        return teilnehmer.get(p.getUniqueId());
    }

    List<Player> online() {
        List<Player> l = new ArrayList<>();
        for (Teilnehmer x : teilnehmer.values()) {
            Player p = Bukkit.getPlayer(x.id);
            if (p != null && p.isOnline()) {
                l.add(p);
            }
        }
        return l;
    }

    boolean lebend(Player p) {
        Teilnehmer x = p == null ? null : teilnehmer.get(p.getUniqueId());
        return x != null && !x.ausgeschieden && !x.geflohen && p.isOnline() && !p.isDead() && arena.enthaelt(p)
                && (p.getGameMode() == GameMode.SURVIVAL || p.getGameMode() == GameMode.ADVENTURE);
    }

    List<Player> lebende() {
        List<Player> l = new ArrayList<>();
        for (Player p : online()) {
            if (lebend(p)) {
                l.add(p);
            }
        }
        return l;
    }

    private Player zufallsSpieler() {
        List<Player> l = lebende();
        return l.isEmpty() ? null : l.get(ZUFALL.nextInt(l.size()));
    }

    private Player naechster() {
        Player best = null;
        double d = Double.MAX_VALUE;
        for (Player p : lebende()) {
            double x = p.getLocation().distanceSquared(boss.getLocation());
            if (x < d) {
                d = x;
                best = p;
            }
        }
        return best;
    }

    private void zielSetzen() {
        LivingEntity z = boss.getTarget();
        if (z instanceof Player p && lebend(p)) {
            return;
        }
        Player n = naechster();
        if (n != null) {
            boss.setTarget(n);
        }
    }

    /** Wer sich eintürmt, wird nach ein paar Sekunden zum Boss heruntergezogen. */
    private void unerreichbarePruefen() {
        for (Player p : lebende()) {
            Teilnehmer x = teilnehmer(p);
            if (p.getLocation().getY() - boss.getLocation().getY() > pl.einst.unerreichbarHoehe) {
                x.unerreichbar++;
                if (x.unerreichbar >= pl.einst.unerreichbarSekunden) {
                    x.unerreichbar = 0;
                    Vector weg = p.getLocation().toVector().subtract(boss.getLocation().toVector()).setY(0);
                    if (weg.lengthSquared() < 0.01) {
                        weg = new Vector(1, 0, 0);
                    }
                    Location ziel = boss.getLocation().add(weg.normalize().multiply(2.5));
                    ziel.setYaw(p.getLocation().getYaw());
                    ziel.setPitch(p.getLocation().getPitch());
                    p.teleport(ziel);
                    p.getWorld().spawnParticle(Particle.PORTAL, ziel, 40, 0.4, 1, 0.4, 0.2);
                    Txt.an(p, Txt.c(typ.name) + " &czieht dich herunter! &7Eintürmen gilt nicht.");
                }
            } else {
                x.unerreichbar = 0;
            }
        }
    }

    void spielerTod(PlayerDeathEvent e) {
        Player p = e.getEntity();
        Teilnehmer x = teilnehmer(p);
        if (x == null || x.ausgeschieden || x.geflohen || zustand != Zustand.LAEUFT) {
            return;
        }
        x.leben--;
        if (boss != null && boss.isValid()) {
            heilen(pl.einst.heilungBeiTod);
        }
        Location ort = p.getLocation();
        switch (raid.tod) {
            case BEHALTEN -> {
                e.setKeepInventory(true);
                e.getDrops().clear();
                e.setKeepLevel(false);
                e.setNewLevel(p.getLevel() / 2);
                e.setNewExp(0);
                e.setDroppedExp(0);
            }
            case NORMAL, GRABTRUHE -> {
                List<ItemStack> sachen = abnehmen(p);
                e.setKeepInventory(true);
                e.getDrops().clear();
                e.setKeepLevel(true);
                e.setDroppedExp(0);
                if (raid.tod == Todesregel.NORMAL) {
                    fallenLassen(p, ort, sachen);
                } else {
                    pl.graeber.anlegen(p, ort, sachen);
                }
            }
        }
        if (x.leben <= 0) {
            x.ausgeschieden = true;
            Txt.an(online(), "&c" + p.getName() + " &7ist ausgeschieden. " + Txt.c(typ.name) + " &7heilt sich.");
        } else {
            Txt.an(online(), "&c" + p.getName() + " &7ist gefallen (noch &f" + x.leben + " &7Leben). " + Txt.c(typ.name) + " &7heilt sich.");
        }
    }

    /** Nimmt dem Spieler alles ab, außer Gegenständen wie dem Hilfe-Buch. Fluch des Verschwindens verschwindet. */
    private List<ItemStack> abnehmen(Player p) {
        List<ItemStack> l = new ArrayList<>();
        PlayerInventory inv = p.getInventory();
        Enchantment verschwinden = Attr.verzauberung("vanishing_curse");
        ItemStack[] inhalt = inv.getContents();
        for (int i = 0; i < inhalt.length; i++) {
            ItemStack it = inhalt[i];
            if (it == null || it.getType().isAir() || pl.einst.nieAbnehmen(it)) {
                continue;
            }
            inv.setItem(i, null);
            if (verschwinden != null && it.containsEnchantment(verschwinden)) {
                continue;
            }
            l.add(it);
        }
        return l;
    }

    private void fallenLassen(Player p, Location ort, List<ItemStack> sachen) {
        int minuten = pl.einst.besitzerschutzMinuten;
        List<Item> fallen = new ArrayList<>();
        for (ItemStack i : sachen) {
            Item it = ort.getWorld().dropItemNaturally(ort, i);
            it.setOwner(p.getUniqueId());
            it.setUnlimitedLifetime(true);
            fallen.add(it);
        }
        Txt.an(p, "&7Deine Sachen liegen am Todesort. &f" + minuten + " Minuten &7lang kannst nur du sie aufheben.");
        Bukkit.getScheduler().runTaskLater(pl, () -> {
            for (Item it : fallen) {
                if (it.isValid()) {
                    it.setOwner(null);
                    it.setUnlimitedLifetime(false);
                }
            }
        }, minuten * 60L * 20L);
    }

    Location wiederbeleben(Player p) {
        Teilnehmer x = teilnehmer(p);
        if (x == null || x.ausgeschieden || x.geflohen || zustand == Zustand.BEENDET) {
            return null;
        }
        return arena.eingang;
    }

    void geflohen(Player p, String grund) {
        Teilnehmer x = teilnehmer(p);
        if (x == null || x.geflohen || x.ausgeschieden || zustand == Zustand.BEENDET) {
            return;
        }
        if (zustand == Zustand.SAMMELN) {
            teilnehmer.remove(p.getUniqueId());
            return;
        }
        x.geflohen = true;
        Txt.an(online(), "&e" + p.getName() + " &7" + grund + " und bekommt keinen Loot.");
        if (bar != null) {
            bar.removePlayer(p);
        }
    }

    // ===================== Schaden am Boss =====================

    void bossSchaden(EntityDamageEvent e) {
        if (zustand != Zustand.LAEUFT || !(e instanceof EntityDamageByEntityEvent be)) {
            e.setCancelled(true);
            return;
        }
        Player p = verursacher(be.getDamager());
        if (p == null) {
            e.setCancelled(true);
            return;
        }
        Teilnehmer x = teilnehmer(p);
        if (x == null || x.ausgeschieden || x.geflohen) {
            e.setCancelled(true);
            hinweis(p, "&7Du kämpfst nicht in diesem Raid mit.");
            return;
        }
        if (leerSek >= 0) {
            e.setCancelled(true);
            return;
        }
        if (steinhautHart) {
            e.setCancelled(true);
            boss.getWorld().playSound(boss.getLocation(), Sound.BLOCK_ANVIL_LAND, 0.6f, 1.6f);
            hinweis(p, "&7Die Steinhaut hält jeden Schlag ab. &fWarte, bis sie bröckelt!");
            return;
        }
        double f = 1;
        if (t < verwundbarBis || steinhautAktiv) {
            f *= 2;
        }
        if (!verstaerker.isEmpty()) {
            f *= 1 - verstaerkerSchutz;
        }
        Entity d = be.getDamager();
        for (BossTyp.Schwaeche s : typ.schwaechen) {
            switch (s.art()) {
                case "waffe" -> {
                    if (d instanceof Player pp && pp.getInventory().getItemInMainHand().getType().name().endsWith(s.wert().toUpperCase())) {
                        f *= s.faktor();
                    }
                }
                case "verzauberung" -> {
                    Enchantment en = Attr.verzauberung(s.wert());
                    if (d instanceof Player pp && en != null && pp.getInventory().getItemInMainHand().containsEnchantment(en)) {
                        f *= s.faktor();
                    }
                }
                case "geschoss" -> {
                    if (d instanceof Projectile) {
                        f *= s.faktor();
                    }
                }
                case "wurfgeschoss" -> {
                    if (d.getType().name().equals(s.wert().toUpperCase())) {
                        f *= s.faktor();
                    }
                }
                default -> {
                }
            }
        }
        if (d instanceof Projectile && p.getLocation().distance(boss.getLocation()) > pl.einst.fernkampfEntfernung) {
            f *= pl.einst.fernkampfFaktor;
        }
        e.setDamage(e.getDamage() * f / faktor);
        double echt = Math.min(e.getFinalDamage(), boss.getHealth());
        x.schaden += Math.max(0, echt);
        letzterTreffer = t;
        letzterSpielerTreffer = t;
        heiltGerade = false;
    }

    /** Wer hat den Schaden verursacht? Spieler direkt, über ein Geschoss, ein Haustier oder einen Seelenstab-Helfer. */
    static Player verursacher(Entity d) {
        if (d instanceof Player p) {
            return p;
        }
        if (d instanceof Projectile pr) {
            ProjectileSource s = pr.getShooter();
            if (s instanceof Player p) {
                return p;
            }
            if (s instanceof Entity e) {
                return verursacher(e);
            }
        }
        if (d instanceof Tameable ta && ta.getOwner() instanceof Player p) {
            return p;
        }
        String besitzer = Keys.text(d, Keys.BEGLEITER);
        if (besitzer != null) {
            return Bukkit.getPlayer(UUID.fromString(besitzer));
        }
        return null;
    }

    private void hinweis(Player p, String text) {
        long jetzt = System.currentTimeMillis();
        Long vorher = hinweisGesendet.get(p.getUniqueId());
        if (vorher == null || jetzt - vorher > 4000) {
            hinweisGesendet.put(p.getUniqueId(), jetzt);
            Txt.an(p, text);
        }
    }

    private double maxLeben() {
        return Attr.wert(boss, Attr.LEBEN);
    }

    private void heilen(double anteil) {
        if (boss == null || !boss.isValid() || anteil <= 0) {
            return;
        }
        double max = maxLeben();
        boss.setHealth(Math.min(max, boss.getHealth() + max * anteil));
    }

    // ===================== Ende =====================

    void bossTot(EntityDeathEvent e) {
        e.getDrops().clear();
        e.setDroppedExp(0);
        if (zustand != Zustand.LAEUFT) {
            return;
        }
        zustand = Zustand.BEENDET;
        int sek = (t - startTick) / 20;
        Location ort = boss.getLocation();
        boolean loot = t - letzterSpielerTreffer <= 100;
        List<Map.Entry<Teilnehmer, Double>> rang = Loot.rangliste(this);
        raid.siege++;
        if (raid.besteZeit == 0 || sek < raid.besteZeit) {
            raid.besteZeit = sek;
        }
        raid.letzteRangliste.clear();
        int platz = 1;
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<Teilnehmer, Double> r : rang) {
            String zeile = platz + ". " + r.getKey().name + " – " + Txt.prozent(r.getValue());
            raid.letzteRangliste.add(zeile);
            sb.append("\n&7").append(zeile);
            platz++;
        }
        Txt.alle("&a" + Txt.c(typ.name) + " &awurde besiegt! &7Raid &f" + raid.name + " &7in &f" + Txt.zeit(sek) + "&7.");
        Txt.an(online(), "&6Schaden-Rangliste:" + sb);
        if (typ.siegText != null) {
            Txt.an(online(), typ.siegText);
        }
        feuerwerk(ort);
        if (loot) {
            Loot.verteilen(this, rang);
        } else {
            Txt.an(online(), "&7Der Boss ist nicht durch einen Spieler gestorben, deshalb gibt es keinen Loot.");
        }
        Bukkit.getScheduler().runTaskLater(pl, this::aufraeumen, 60);
    }

    void scheitern(String grund) {
        if (zustand == Zustand.BEENDET) {
            return;
        }
        boolean warLaufend = zustand == Zustand.LAEUFT || zustand == Zustand.AUFTRITT;
        zustand = Zustand.BEENDET;
        String rest = "";
        if (boss != null && boss.isValid()) {
            rest = " &7Restleben: &f" + Txt.prozent(boss.getHealth() / maxLeben()) + "&7.";
            Location o = boss.getLocation();
            o.getWorld().spawnParticle(Particle.LARGE_SMOKE, o.add(0, 1, 0), 60, 0.6, 1, 0.6, 0.02);
            o.getWorld().playSound(o, Sound.ENTITY_WITHER_DEATH, 0.8f, 1.4f);
            boss.remove();
        }
        if (warLaufend) {
            raid.gescheitert++;
            Txt.alle("&cRaid &f" + raid.name + " &cgescheitert: " + grund + rest);
            if (typ.flopText != null) {
                Txt.an(online(), typ.flopText);
            }
        }
        aufraeumen();
    }

    void aufraeumen() {
        zustand = Zustand.BEENDET;
        if (task != null) {
            task.cancel();
        }
        if (bar != null) {
            bar.removeAll();
        }
        if (boss != null && boss.isValid()) {
            boss.remove();
        }
        for (UUID u : helfer) {
            Entity h = Bukkit.getEntity(u);
            if (h != null) {
                h.remove();
            }
        }
        helfer.clear();
        for (Block b : new ArrayList<>(verstaerker.keySet())) {
            pl.temp.zurueck(b);
        }
        verstaerker.clear();
        arena.torOeffnen();
        arena.kerzenLoeschen();
        if (beschworen) {
            arena.abklingBis = System.currentTimeMillis() + raid.abklingzeitMinuten * 60_000L;
        }
        pl.speicher.allesSpeichern();
        pl.kaempfe.entfernen(this);
    }

    private void feuerwerk(Location ort) {
        for (int i = 0; i < 3; i++) {
            Location l = ort.clone().add(ZUFALL.nextDouble() * 4 - 2, 1, ZUFALL.nextDouble() * 4 - 2);
            Firework fw = l.getWorld().spawn(l, Firework.class, f -> {
                f.getPersistentDataContainer().set(Keys.FEUERWERK, PersistentDataType.BYTE, (byte) 1);
                FireworkMeta m = f.getFireworkMeta();
                m.addEffect(FireworkEffect.builder().with(FireworkEffect.Type.BALL_LARGE)
                        .withColor(Color.fromRGB(0xF6B500), Color.PURPLE).withFade(Color.WHITE).trail(true).build());
                m.setPower(1);
                f.setFireworkMeta(m);
            });
            fw.setPersistent(false);
        }
    }

    // ===================== Fähigkeiten =====================

    private boolean aktiv() {
        return zustand == Zustand.LAEUFT && boss != null && boss.isValid() && leerSek < 0;
    }

    private double herzen(Faehigkeit f, String key, double def) {
        return f.d(key, def) * 2 * pl.einst.stufe(stufe).schaden();
    }

    private void ansage(Faehigkeit f, Player ziel) {
        if (f.text != null) {
            Txt.an(online(), f.text.replace("{ziel}", ziel == null ? "jemand" : ziel.getName()).replace("{boss}", typ.name));
        }
    }

    /** Warnung über eine Zeit zeigen (alle 5 Ticks zeichnen), danach die Aktion ausführen. */
    private void warnen(double sekunden, Runnable zeichnen, Runnable aktion) {
        int dauer = Math.max(1, (int) Math.round(sekunden * 20));
        new BukkitRunnable() {
            int i;

            @Override
            public void run() {
                if (!aktiv()) {
                    cancel();
                    return;
                }
                if (i >= dauer) {
                    cancel();
                    aktion.run();
                    return;
                }
                zeichnen.run();
                i += 5;
            }
        }.runTaskTimer(pl, 0, 5);
    }

    private void ring(Location mitte, double r, Particle p, Object daten) {
        World w = mitte.getWorld();
        int punkte = Math.max(12, (int) (r * 10));
        for (int i = 0; i < punkte; i++) {
            double a = 2 * Math.PI * i / punkte;
            w.spawnParticle(p, mitte.clone().add(Math.cos(a) * r, 0.15, Math.sin(a) * r), 1, 0, 0, 0, 0, daten);
        }
    }

    private void faehigkeitStarten(Faehigkeit f) {
        switch (f.art) {
            case "salve" -> salve(f);
            case "beschwoeren" -> beschwoeren(f);
            case "teleport" -> teleport(f);
            case "zone" -> zone(f);
            case "schockwelle" -> schockwelle(f);
            case "wurf" -> wurf(f);
            case "verstaerker" -> verstaerkerSetzen(f);
            case "fluch" -> fluch(f);
            default -> pl.getLogger().warning("Unbekannte Fähigkeit: " + f.art);
        }
    }

    private void salve(Faehigkeit f) {
        Player ziel = naechster();
        if (ziel == null) {
            return;
        }
        ansage(f, ziel);
        warnen(f.warnung, () -> {
            boss.getWorld().spawnParticle(Particle.ENCHANT, boss.getEyeLocation(), 20, 0.4, 0.4, 0.4, 0.5);
            boss.getWorld().playSound(boss.getLocation(), Sound.ITEM_CROSSBOW_LOADING_MIDDLE, 0.8f, 0.6f);
        }, () -> {
            int anzahl = f.i("anzahl", 3);
            double schaden = herzen(f, "schaden", 2);
            for (int i = 0; i < anzahl; i++) {
                Bukkit.getScheduler().runTaskLater(pl, () -> {
                    if (!aktiv() || !lebend(ziel)) {
                        return;
                    }
                    Vector dir = ziel.getEyeLocation().toVector().subtract(boss.getEyeLocation().toVector()).normalize();
                    dir.add(new Vector(ZUFALL.nextGaussian() * 0.04, ZUFALL.nextGaussian() * 0.03, ZUFALL.nextGaussian() * 0.04));
                    Arrow a = boss.launchProjectile(Arrow.class, dir.multiply(1.9));
                    a.setPickupStatus(AbstractArrow.PickupStatus.DISALLOWED);
                    a.setPersistent(false);
                    a.getPersistentDataContainer().set(Keys.PFEIL, PersistentDataType.DOUBLE, schaden);
                    Bukkit.getScheduler().runTaskLater(pl, a::remove, 100);
                }, i * 4L);
            }
        });
    }

    private void beschwoeren(Faehigkeit f) {
        EntityType art;
        try {
            art = EntityType.valueOf(f.s("mob", "SKELETON").toUpperCase());
        } catch (IllegalArgumentException ex) {
            return;
        }
        Class<? extends Entity> klasse = art.getEntityClass();
        if (klasse == null) {
            return;
        }
        int maxHelfer = f.i("max", 8);
        helfer.removeIf(u -> {
            Entity h = Bukkit.getEntity(u);
            return h == null || !h.isValid();
        });
        if (helfer.size() >= maxHelfer) {
            return;
        }
        int anzahl = Math.min(f.i("anzahl", 3), maxHelfer - helfer.size());
        List<Location> orte = new ArrayList<>();
        for (int i = 0; i < anzahl; i++) {
            orte.add(zufallsOrt(boss.getLocation(), 2, 5));
        }
        ansage(f, null);
        warnen(f.warnung, () -> {
            for (Location o : orte) {
                o.getWorld().spawnParticle(Particle.SOUL_FIRE_FLAME, o.clone().add(0, 0.2, 0), 6, 0.3, 0.05, 0.3, 0.01);
            }
        }, () -> {
            double heilt = f.d("heilt", 0) / 100.0;
            int groesse = f.i("groesse", 0);
            for (Location o : orte) {
                Entity h = o.getWorld().spawn(o, klasse, (Entity x) -> {
                    x.setPersistent(false);
                    x.getPersistentDataContainer().set(Keys.HELFER, PersistentDataType.STRING, arena.name);
                    if (heilt > 0) {
                        x.getPersistentDataContainer().set(Keys.HEILT, PersistentDataType.DOUBLE, heilt);
                    }
                    if (x instanceof Slime s && groesse > 0) {
                        s.setSize(groesse);
                    }
                    if (x instanceof Mob m) {
                        m.setRemoveWhenFarAway(false);
                        EntityEquipment eq = m.getEquipment();
                        if (eq != null) {
                            eq.setItemInMainHandDropChance(0);
                            eq.setHelmetDropChance(0);
                        }
                    }
                });
                if (h instanceof Mob m) {
                    Player z = naechster();
                    if (z != null) {
                        m.setTarget(z);
                    }
                }
                o.getWorld().spawnParticle(Particle.LARGE_SMOKE, o.clone().add(0, 0.5, 0), 10, 0.3, 0.3, 0.3, 0.02);
                helfer.add(h.getUniqueId());
            }
            int v = f.i("danach-verwundbar", 0);
            if (v > 0) {
                verwundbarBis = t + v * 20;
                boss.getWorld().spawnParticle(Particle.CRIT, boss.getLocation().add(0, 1, 0), 30, 0.5, 0.8, 0.5, 0.2);
                Txt.an(online(), "&e" + Txt.c(typ.name) + " &eist für " + v + " s verwundbar: doppelter Schaden!");
            }
        });
    }

    private void helferPruefen() {
        List<UUID> weg = new ArrayList<>();
        for (UUID u : helfer) {
            Entity h = Bukkit.getEntity(u);
            if (h == null || !h.isValid()) {
                weg.add(u);
                continue;
            }
            double heilt = Keys.zahl(h, Keys.HEILT);
            if (heilt > 0 && h.getLocation().distanceSquared(boss.getLocation()) < 4) {
                heilen(heilt);
                h.getWorld().spawnParticle(Particle.HEART, boss.getLocation().add(0, 2, 0), 5, 0.4, 0.3, 0.4, 0);
                h.remove();
                weg.add(u);
                Txt.an(online(), "&c" + Txt.c(typ.name) + " &cnimmt die Kraft eines Helfers auf und heilt sich!");
                continue;
            }
            if (h instanceof Mob m && !(m.getTarget() instanceof Player pp && lebend(pp))) {
                Player z = naechster();
                if (z != null) {
                    m.setTarget(z);
                }
            }
        }
        helfer.removeAll(weg);
    }

    private void teleport(Faehigkeit f) {
        Player ziel = zufallsSpieler();
        if (ziel == null) {
            return;
        }
        Vector hinten = ziel.getLocation().getDirection().setY(0);
        if (hinten.lengthSquared() < 0.01) {
            hinten = new Vector(0, 0, 1);
        }
        Location dest = ziel.getLocation().clone().add(hinten.normalize().multiply(-2));
        if (!dest.getBlock().isPassable() || !dest.clone().add(0, 1, 0).getBlock().isPassable() || !arena.enthaelt(dest)) {
            dest = ziel.getLocation().clone();
        }
        Location ort = dest;
        int unsichtbar = f.i("unsichtbar", 0);
        ansage(f, ziel);
        if (unsichtbar > 0) {
            boss.addPotionEffect(new PotionEffect(PotionEffectType.INVISIBILITY, unsichtbar * 20, 0, false, false));
            boss.setCustomNameVisible(false);
            Bukkit.getScheduler().runTaskLater(pl, () -> {
                if (boss != null && boss.isValid()) {
                    boss.setCustomNameVisible(true);
                }
            }, unsichtbar * 20L);
        }
        warnen(f.warnung, () -> ort.getWorld().spawnParticle(Particle.PORTAL, ort.clone().add(0, 1, 0), 25, 0.3, 0.8, 0.3, 0.3), () -> {
            boss.teleport(ort);
            boss.getWorld().playSound(ort, Sound.ENTITY_ENDERMAN_TELEPORT, 1f, 0.7f);
            boss.setTarget(ziel);
        });
    }

    private void zone(Faehigkeit f) {
        PotionEffectType eff = Attr.effekt(f.s("effekt", "wither"));
        double r = f.d("radius", 5);
        int dauer = f.i("dauer", 8);
        int st = Math.max(0, f.i("stufe", 1) - 1);
        ansage(f, null);
        warnen(f.warnung, () -> ring(boss.getLocation(), r, Particle.SOUL, null), () -> new BukkitRunnable() {
            int i;

            @Override
            public void run() {
                if (!aktiv() || i >= dauer * 20) {
                    cancel();
                    return;
                }
                ring(boss.getLocation(), r, Particle.SOUL_FIRE_FLAME, null);
                for (Player p : lebende()) {
                    if (p.getLocation().distanceSquared(boss.getLocation()) <= r * r && eff != null) {
                        p.addPotionEffect(new PotionEffect(eff, 40, st));
                    }
                }
                i += 10;
            }
        }.runTaskTimer(pl, 0, 10));
    }

    private void schockwelle(Faehigkeit f) {
        double r = f.d("radius", 6);
        double schaden = herzen(f, "schaden", 6);
        double hoch = f.d("hoch", 1.0);
        Particle.DustOptions staub = new Particle.DustOptions(Color.fromRGB(0x8A6A4A), 1.6f);
        ansage(f, null);
        warnen(f.warnung, () -> {
            ring(boss.getLocation(), r, Particle.DUST, staub);
            ring(boss.getLocation(), r * 0.5, Particle.DUST, staub);
            boss.getWorld().playSound(boss.getLocation(), Sound.ENTITY_IRON_GOLEM_HURT, 0.6f, 0.5f);
        }, () -> {
            Location o = boss.getLocation();
            o.getWorld().playSound(o, Sound.ENTITY_GENERIC_EXPLODE, 1f, 0.6f);
            o.getWorld().spawnParticle(Particle.EXPLOSION, o.clone().add(0, 0.5, 0), 6, r / 3, 0.2, r / 3, 0);
            for (Player p : lebende()) {
                if (p.getLocation().distanceSquared(o) <= r * r && amBoden(p)) {
                    p.damage(schaden, boss);
                    Vector weg = p.getLocation().toVector().subtract(o.toVector()).setY(0);
                    if (weg.lengthSquared() < 0.01) {
                        weg = new Vector(0.1, 0, 0);
                    }
                    p.setVelocity(weg.normalize().multiply(0.7).setY(hoch));
                }
            }
        });
    }

    private void wurf(Faehigkeit f) {
        Player ziel = naechster();
        if (ziel == null) {
            return;
        }
        Material m = Material.matchMaterial(f.s("block", "COBBLESTONE"));
        BlockData daten = (m == null || !m.isBlock() ? Material.COBBLESTONE : m).createBlockData();
        double schaden = herzen(f, "schaden", 4);
        ansage(f, ziel);
        warnen(f.warnung, () -> {
            Vector richtung = ziel.getLocation().toVector().subtract(boss.getLocation().toVector());
            for (double s = 0.2; s < 1; s += 0.2) {
                Location l = boss.getLocation().add(richtung.clone().multiply(s)).add(0, 1.2, 0);
                l.getWorld().spawnParticle(Particle.CRIT, l, 2, 0.05, 0.05, 0.05, 0);
            }
        }, () -> {
            if (!lebend(ziel)) {
                return;
            }
            Location start = boss.getEyeLocation().add(0, 1, 0);
            FallingBlock fb = start.getWorld().spawn(start, FallingBlock.class, x -> {
                x.setBlockData(daten);
                x.setDropItem(false);
                x.setHurtEntities(false);
                x.setPersistent(false);
                x.getPersistentDataContainer().set(Keys.WURF, PersistentDataType.DOUBLE, schaden);
            });
            Vector v = ziel.getLocation().toVector().subtract(start.toVector());
            double dist = Math.sqrt(v.getX() * v.getX() + v.getZ() * v.getZ());
            Vector flug = v.clone().setY(0).normalize().multiply(Math.min(1.8, 0.25 + dist * 0.055));
            flug.setY(0.35 + dist * 0.018);
            fb.setVelocity(flug);
            boss.getWorld().playSound(boss.getLocation(), Sound.ENTITY_IRON_GOLEM_ATTACK, 1f, 0.5f);
            Bukkit.getScheduler().runTaskLater(pl, () -> {
                if (fb.isValid()) {
                    wurfLandet(fb);
                }
            }, 100);
        });
    }

    void wurfLandet(FallingBlock fb) {
        double schaden = Keys.zahl(fb, Keys.WURF);
        Location o = fb.getLocation();
        fb.remove();
        o.getWorld().spawnParticle(Particle.BLOCK, o, 40, 0.6, 0.3, 0.6, 0.1, fb.getBlockData());
        o.getWorld().playSound(o, Sound.BLOCK_STONE_BREAK, 1f, 0.6f);
        if (boss == null) {
            return;
        }
        for (Player p : lebende()) {
            if (p.getLocation().distanceSquared(o) <= 4.4) {
                p.damage(schaden, boss);
            }
        }
    }

    private void verstaerkerSetzen(Faehigkeit f) {
        if (!verstaerker.isEmpty()) {
            return;
        }
        Material m = Material.matchMaterial(f.s("block", "CAULDRON"));
        if (m == null || !m.isBlock()) {
            m = Material.CAULDRON;
        }
        int anzahl = f.i("anzahl", 3);
        int treffer = f.i("treffer", 3);
        verstaerkerSchutz = f.d("schutz", 50) / 100.0;
        verstaerkerHeilung = f.d("heilung", 0.5) / 100.0;
        List<Location> orte = new ArrayList<>();
        for (int i = 0; i < anzahl; i++) {
            orte.add(zufallsOrt(boss.getLocation(), 6, 16));
        }
        Material block = m;
        ansage(f, null);
        warnen(f.warnung, () -> {
            for (Location o : orte) {
                o.getWorld().spawnParticle(Particle.WITCH, o.clone().add(0, 0.5, 0), 8, 0.3, 0.3, 0.3, 0);
            }
        }, () -> {
            for (Location o : orte) {
                Block b = o.getBlock();
                if (!b.getType().isAir() && !b.isReplaceable()) {
                    continue;
                }
                pl.temp.setzen(b, block.createBlockData());
                verstaerker.put(b, treffer);
                o.getWorld().spawnParticle(Particle.WITCH, o.clone().add(0.5, 1, 0.5), 20, 0.3, 0.4, 0.3, 0);
            }
            if (!verstaerker.isEmpty()) {
                Txt.an(online(), "&7Zerschlagt die &f" + verstaerker.size() + " &7Verstärker! Jeder braucht &f" + treffer
                        + " &7Schläge. Solange sie stehen, nimmt " + Txt.c(typ.name) + " &7weniger Schaden.");
            }
        });
    }

    boolean istVerstaerker(Block b) {
        return verstaerker.containsKey(b);
    }

    void verstaerkerTreffer(Player p, Block b) {
        Integer rest = verstaerker.get(b);
        if (rest == null || !lebend(p)) {
            return;
        }
        rest--;
        b.getWorld().playSound(b.getLocation(), Sound.BLOCK_ANVIL_HIT, 0.7f, 1.3f);
        b.getWorld().spawnParticle(Particle.CRIT, b.getLocation().add(0.5, 1, 0.5), 8, 0.3, 0.2, 0.3, 0.1);
        if (rest <= 0) {
            verstaerker.remove(b);
            pl.temp.zurueck(b);
            b.getWorld().spawnParticle(Particle.LARGE_SMOKE, b.getLocation().add(0.5, 0.5, 0.5), 15, 0.3, 0.3, 0.3, 0.02);
            Txt.an(online(), "&a" + p.getName() + " &7hat einen Verstärker zerschlagen. &f" + verstaerker.size() + " &7übrig.");
        } else {
            verstaerker.put(b, rest);
        }
    }

    private void fluch(Faehigkeit f) {
        Player ziel = zufallsSpieler();
        PotionEffectType eff = Attr.effekt(f.s("effekt", "blindness"));
        if (ziel == null || eff == null) {
            return;
        }
        int dauer = f.i("dauer", 3);
        ansage(f, ziel);
        warnen(f.warnung, () -> ziel.getWorld().spawnParticle(Particle.WITCH, ziel.getLocation().add(0, 2.2, 0), 10, 0.3, 0.2, 0.3, 0),
                () -> {
                    if (lebend(ziel)) {
                        ziel.addPotionEffect(new PotionEffect(eff, dauer * 20, Math.max(0, f.i("stufe", 1) - 1)));
                    }
                });
    }

    // ----- dauerhafte Fähigkeiten -----

    private int fluchtBereit;

    private void flucht(Faehigkeit f) {
        if (t < fluchtBereit) {
            return;
        }
        double r = f.d("radius", 3);
        for (Player p : lebende()) {
            if (p.getLocation().distanceSquared(boss.getLocation()) <= r * r) {
                fluchtBereit = t + f.alle * 20;
                Location ziel = zufallsOrt(p.getLocation(), f.d("min", 8), f.d("max", 15));
                ansage(f, p);
                warnen(f.warnung, () -> boss.getWorld().spawnParticle(Particle.WITCH, boss.getLocation().add(0, 1, 0), 15, 0.4, 0.6, 0.4, 0), () -> {
                    boss.getWorld().spawnParticle(Particle.PORTAL, boss.getLocation().add(0, 1, 0), 40, 0.4, 0.8, 0.4, 0.3);
                    boss.teleport(ziel);
                    boss.getWorld().playSound(ziel, Sound.ENTITY_ENDERMAN_TELEPORT, 1f, 1.3f);
                });
                return;
            }
        }
    }

    private void heilkreis(Faehigkeit f) {
        int ruhe = f.i("ruhe", 5);
        if (t - letzterTreffer < ruhe * 20) {
            return;
        }
        if (!heiltGerade) {
            heiltGerade = true;
            Txt.an(online(), f.text != null ? f.text : "&a" + Txt.c(typ.name) + " &aheilt sich! Unterbrecht sie mit einem Treffer!");
        }
        heilen(f.d("prozent", 5) / 100.0);
        ring(boss.getLocation(), 1.5, Particle.HAPPY_VILLAGER, null);
    }

    private void steinhaut(Faehigkeit f) {
        if (!steinhautAktiv && steinhautWechsel == 0) {
            steinhautWechsel = t + f.i("aus", 5) * 20;
        }
        steinhautAktiv = !steinhautHart;
        if (!steinhautHart && !steinhautGewarnt && t >= steinhautWechsel - 20) {
            steinhautGewarnt = true;
            boss.getWorld().spawnParticle(Particle.BLOCK, boss.getLocation().add(0, 1.5, 0), 30, 0.6, 0.8, 0.6, 0,
                    Material.STONE.createBlockData());
            Txt.an(online(), f.text != null ? f.text : "&7" + Txt.c(typ.name) + " &7wird zu Stein!");
        }
        if (t >= steinhautWechsel) {
            steinhautHart = !steinhautHart;
            steinhautGewarnt = false;
            steinhautWechsel = t + (steinhautHart ? f.i("an", 5) : f.i("aus", 5)) * 20;
            if (steinhautHart) {
                boss.getWorld().playSound(boss.getLocation(), Sound.BLOCK_STONE_PLACE, 1f, 0.5f);
            } else {
                boss.getWorld().playSound(boss.getLocation(), Sound.BLOCK_STONE_BREAK, 1f, 0.7f);
                Txt.an(online(), "&e" + Txt.c(typ.name) + "&e: Die Steinhaut bröckelt, jetzt doppelter Schaden!");
            }
        }
        if (steinhautHart && t % 20 == 0) {
            boss.getWorld().spawnParticle(Particle.BLOCK, boss.getLocation().add(0, 1, 0), 10, 0.5, 0.8, 0.5, 0,
                    Material.STONE.createBlockData());
        }
    }

    // ===================== Hilfen =====================

    /** Steht der Spieler auf dem Boden? (Wer im richtigen Moment springt, entgeht der Schockwelle.) */
    private static boolean amBoden(Player p) {
        Location l = p.getLocation();
        if (l.getY() - Math.floor(l.getY()) > 0.25 && !l.getBlock().getType().isSolid()) {
            return !l.clone().subtract(0, 0.3, 0).getBlock().isPassable();
        }
        return !l.clone().subtract(0, 0.1, 0).getBlock().isPassable();
    }

    /** Zufälliger begehbarer Ort in der Arena, im Abstand min..max um einen Punkt. */
    private Location zufallsOrt(Location um, double min, double max) {
        World w = um.getWorld();
        for (int versuch = 0; versuch < 30; versuch++) {
            double a = ZUFALL.nextDouble() * Math.PI * 2;
            double d = min + ZUFALL.nextDouble() * Math.max(0, max - min);
            double x = um.getX() + Math.cos(a) * d, z = um.getZ() + Math.sin(a) * d;
            Location boden = boden(w, x, z, um.getY());
            if (boden != null && arena.enthaelt(boden)) {
                return boden;
            }
        }
        return arena.bossSpawn.clone();
    }

    private static Location boden(World w, double x, double z, double hoehe) {
        int bx = (int) Math.floor(x), bz = (int) Math.floor(z);
        for (int y = (int) hoehe + 4; y >= (int) hoehe - 6; y--) {
            Block b = w.getBlockAt(bx, y, bz);
            if (b.getType().isSolid() && b.getRelative(0, 1, 0).isPassable() && b.getRelative(0, 2, 0).isPassable()
                    && !b.getRelative(0, 1, 0).isLiquid()) {
                return new Location(w, bx + 0.5, y + 1, bz + 0.5);
            }
        }
        return null;
    }

    boolean istHelfer(Entity e) {
        return helfer.contains(e.getUniqueId());
    }

    int sekundenUebrig() {
        return restSek;
    }

    int phase() {
        return phase;
    }
}
