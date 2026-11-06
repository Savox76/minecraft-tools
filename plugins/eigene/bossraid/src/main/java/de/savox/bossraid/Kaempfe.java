package de.savox.bossraid;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.scheduler.BukkitTask;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** Laufende Kämpfe und Rituale, je Arena höchstens einer. */
final class Kaempfe {
    /** Ein Ritual am Altar: Gegenstand liegt, Kerzen werden angezündet, dann erscheint der Boss. */
    final class Ritual {
        final Arena arena;
        final RaidVorlage raid;
        final BossTyp typ;
        final UUID beschwoerer;
        final ItemStack gegenstand;
        final boolean verflucht;
        int sekunden;
        int countdown = -1;
        BukkitTask task;

        Ritual(Arena arena, RaidVorlage raid, BossTyp typ, Player p, ItemStack gegenstand, boolean verflucht) {
            this.arena = arena;
            this.raid = raid;
            this.typ = typ;
            this.beschwoerer = p.getUniqueId();
            this.gegenstand = gegenstand;
            this.verflucht = verflucht;
        }
    }

    private final BossRaidPlugin pl;
    private final Map<String, Kampf> kaempfe = new LinkedHashMap<>();
    private final Map<String, Ritual> rituale = new LinkedHashMap<>();
    private final Map<UUID, Long> bestaetigung = new HashMap<>();

    Kaempfe(BossRaidPlugin pl) {
        this.pl = pl;
    }

    Kampf in(Arena a) {
        return a == null ? null : kaempfe.get(Speicher.key(a.name));
    }

    boolean belegt(Arena a) {
        return in(a) != null || rituale.containsKey(Speicher.key(a.name));
    }

    Kampf von(Player p) {
        for (Kampf k : kaempfe.values()) {
            if (k.teilnehmer.containsKey(p.getUniqueId())) {
                return k;
            }
        }
        return null;
    }

    Kampf mitBoss(Entity e) {
        for (Kampf k : kaempfe.values()) {
            if (k.boss != null && k.boss.getUniqueId().equals(e.getUniqueId())) {
                return k;
            }
        }
        return null;
    }

    Kampf an(Location l) {
        for (Kampf k : kaempfe.values()) {
            if (k.arena.enthaelt(l)) {
                return k;
            }
        }
        return null;
    }

    List<Kampf> alle() {
        return new ArrayList<>(kaempfe.values());
    }

    boolean irgendwas() {
        return !kaempfe.isEmpty() || !rituale.isEmpty();
    }

    void entfernen(Kampf k) {
        kaempfe.values().remove(k);
    }

    /** Prüft, ob Arena und Raid startklar sind. Liefert eine Fehlermeldung oder null. */
    String pruefen(RaidVorlage r) {
        Arena a = pl.speicher.arena(r.arena);
        if (a == null) {
            return "Der Raid hat keine gültige Arena. &f/raid set " + r.name + " arena <arena>";
        }
        if (!a.bereit()) {
            return "In der Arena &f" + a.name + " &cfehlen Boss-Spawn oder Eingang.";
        }
        if (pl.bosse.get(r.boss) == null) {
            return "Der Raid hat keinen gültigen Boss. &f/raid set " + r.name + " boss <boss>";
        }
        if (belegt(a)) {
            return "In der Arena &f" + a.name + " &cläuft gerade schon etwas.";
        }
        return null;
    }

    Kampf adminStart(RaidVorlage r, boolean sofort) {
        Arena a = pl.speicher.arena(r.arena);
        Kampf k = new Kampf(pl, a, r, pl.bosse.get(r.boss), r.stufe, false);
        kaempfe.put(Speicher.key(a.name), k);
        if (sofort) {
            List<Player> drin = a.spielerDrin();
            k.auftritt(drin);
        } else {
            k.sammeln();
        }
        return k;
    }

    void alleAbbrechen(String grund) {
        for (Ritual r : new ArrayList<>(rituale.values())) {
            ritualAbbrechen(r, grund);
        }
        for (Kampf k : alle()) {
            k.scheitern(grund);
        }
    }

    // ===================== Ritual =====================

    /** Rechtsklick mit einem Beschwörungsgegenstand auf den Altar. */
    void altarBenutzt(Player p, Arena a, ItemStack hand) {
        String id = Gegenstaende.id(hand);
        RaidVorlage r = pl.speicher.raid(a.altarRaid);
        if (r == null) {
            Txt.an(p, "&cDieser Altar ist mit keinem Raid verbunden. Ein Admin richtet ihn mit &f/bossarena altar &cein.");
            return;
        }
        BossTyp typ = pl.bosse.get(r.boss);
        if (typ == null || id == null || !id.equals(typ.beschwoerung)) {
            Txt.an(p, "&7Dieser Altar ruft " + (typ == null ? "keinen Boss" : Txt.c(typ.name))
                    + "&7. Dafür brauchst du: &f" + (typ == null ? "?" : Txt.c(pl.gegenstaende.name(typ.beschwoerung))));
            return;
        }
        if (!r.beschwoerung) {
            Txt.an(p, "&cAn diesem Altar kann gerade niemand beschwören. Den Raid startet ein Admin.");
            return;
        }
        String fehler = pruefen(r);
        if (fehler != null) {
            Txt.an(p, "&c" + fehler);
            return;
        }
        long jetzt = System.currentTimeMillis();
        if (a.abklingBis > jetzt) {
            Txt.an(p, "&7Der Altar ruht noch &f" + Txt.zeit((int) ((a.abklingBis - jetzt) / 1000)) + "&7.");
            return;
        }
        int drin = a.spielerDrin().size();
        if (drin < r.spielerMin) {
            Txt.an(p, "&cZu wenige Spieler in der Arena: " + drin + " von mindestens " + r.spielerMin + ".");
            return;
        }
        if (drin == 1) {
            Long vorher = bestaetigung.get(p.getUniqueId());
            if (vorher == null || jetzt - vorher > 10_000) {
                bestaetigung.put(p.getUniqueId(), jetzt);
                Txt.an(p, "&eDu bist allein! " + Txt.c(typ.name) + " &eist stark und kann dich töten. "
                        + "&7Zum Bestätigen innerhalb von 10 s nochmal auf den Altar klicken.");
                return;
            }
            bestaetigung.remove(p.getUniqueId());
        }
        boolean verflucht = Gegenstaende.verflucht(hand);
        ItemStack echt = p.getInventory().getItemInMainHand();
        ItemStack eins = echt.clone();
        eins.setAmount(1);
        echt.setAmount(echt.getAmount() - 1);
        p.getInventory().setItemInMainHand(echt.getAmount() > 0 ? echt : null);
        Ritual ri = new Ritual(a, r, typ, p, eins, verflucht);
        rituale.put(Speicher.key(a.name), ri);
        a.kerzenSetzen();
        Block altar = a.altar();
        altar.getWorld().playSound(altar.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1f, 0.6f);
        Txt.an(a.spielerDrin(), "&5" + p.getName() + " &7hat " + Txt.c(pl.gegenstaende.name(typ.beschwoerung))
                + " &7auf den Altar gelegt. &fZündet die vier Kerzen an! &7(" + pl.einst.kerzenZeit + " s)");
        ri.task = Bukkit.getScheduler().runTaskTimer(pl, () -> ritualTick(ri), 20, 20);
    }

    private void ritualTick(Ritual ri) {
        Arena a = ri.arena;
        Player p = Bukkit.getPlayer(ri.beschwoerer);
        if (p == null || !a.enthaelt(p)) {
            ritualAbbrechen(ri, "Der Beschwörer hat die Arena verlassen.");
            return;
        }
        Block altar = a.altar();
        Location mitte = altar.getLocation().add(0.5, 1.2, 0.5);
        int an = a.kerzenAn();
        if (ri.countdown < 0) {
            ri.sekunden++;
            mitte.getWorld().spawnParticle(Particle.ENCHANT, mitte, 20, 0.4, 0.3, 0.4, 0.8);
            if (an == 4) {
                ri.countdown = pl.einst.ritualDauer;
                Txt.an(a.spielerDrin(), "&5Das Ritual beginnt! &7Bleibt in der Arena. " + Txt.c(ri.typ.name)
                        + " &7erscheint in &f" + ri.countdown + " s&7.");
            } else if (ri.sekunden >= pl.einst.kerzenZeit) {
                ritualAbbrechen(ri, "Die Kerzen wurden nicht rechtzeitig angezündet.");
            } else if (ri.sekunden % 15 == 0) {
                Txt.an(a.spielerDrin(), "&7Kerzen: &f" + an + " von 4 &7brennen. Noch &f" + (pl.einst.kerzenZeit - ri.sekunden) + " s&7.");
            }
            return;
        }
        if (an < 4) {
            ritualAbbrechen(ri, "Eine Kerze ist erloschen.");
            return;
        }
        ri.countdown--;
        mitte.getWorld().spawnParticle(Particle.SOUL_FIRE_FLAME, mitte, 30, 0.6, 0.6, 0.6, 0.05);
        mitte.getWorld().playSound(mitte, Sound.BLOCK_BELL_RESONATE, 0.6f, 0.5f + (pl.einst.ritualDauer - ri.countdown) * 0.08f);
        if (ri.countdown == 3) {
            mitte.getWorld().strikeLightningEffect(mitte);
        }
        if (ri.countdown > 0) {
            return;
        }
        ri.task.cancel();
        rituale.remove(Speicher.key(a.name));
        List<Player> dabei = a.spielerDrin();
        if (dabei.size() < ri.raid.spielerMin) {
            zurueckgeben(ri, "Zu wenige Spieler in der Arena.");
            return;
        }
        Stufe st = ri.verflucht ? Stufe.SCHWER : ri.raid.stufe;
        Kampf k = new Kampf(pl, a, ri.raid, ri.typ, st, true);
        kaempfe.put(Speicher.key(a.name), k);
        Txt.alle("&5Ein Ritual in der Arena &f" + a.name + " &5ruft " + Txt.c(ri.typ.name) + " &5(Stufe " + st.id() + ")!");
        k.auftritt(dabei);
    }

    void ritualAbbrechen(Ritual ri, String grund) {
        if (ri.task != null) {
            ri.task.cancel();
        }
        rituale.remove(Speicher.key(ri.arena.name));
        zurueckgeben(ri, grund);
    }

    private void zurueckgeben(Ritual ri, String grund) {
        ri.arena.kerzenLoeschen();
        Player p = Bukkit.getPlayer(ri.beschwoerer);
        if (p != null) {
            for (ItemStack rest : p.getInventory().addItem(ri.gegenstand).values()) {
                p.getWorld().dropItem(p.getLocation(), rest).setOwner(p.getUniqueId());
            }
            Txt.an(p, "&cRitual abgebrochen: " + grund + " &7Du hast deinen Gegenstand zurück.");
        } else {
            Location l = ri.arena.altar().getLocation().add(0.5, 1, 0.5);
            l.getWorld().dropItem(l, ri.gegenstand);
        }
        Txt.an(ri.arena.spielerDrin(), "&cDas Ritual wurde abgebrochen: " + grund);
    }

    Ritual ritualIn(Arena a) {
        return rituale.get(Speicher.key(a.name));
    }
}
