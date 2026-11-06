package de.savox.bossraid;

import org.bukkit.Location;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.FallingBlock;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Mob;
import org.bukkit.entity.Player;
import org.bukkit.entity.Projectile;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockDamageEvent;
import org.bukkit.event.block.BlockExplodeEvent;
import org.bukkit.event.block.BlockPistonExtendEvent;
import org.bukkit.event.block.BlockPistonRetractEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityChangeBlockEvent;
import org.bukkit.event.entity.EntityCombustEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.EntityTargetLivingEntityEvent;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.event.entity.SlimeSplitEvent;
import org.bukkit.event.player.PlayerBucketEmptyEvent;
import org.bukkit.event.player.PlayerBucketFillEvent;
import org.bukkit.event.player.PlayerMoveEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.player.PlayerRespawnEvent;
import org.bukkit.event.player.PlayerTeleportEvent;
import org.bukkit.event.world.EntitiesLoadEvent;

import java.util.List;

/** Alles rund um den laufenden Kampf: Schaden, Tod, Wiederbelebung, Arena-Grenzen und Schutz. */
final class KampfListener implements Listener {
    private final BossRaidPlugin pl;

    KampfListener(BossRaidPlugin pl) {
        this.pl = pl;
    }

    private static boolean kaempft(Kampf k) {
        return k != null && (k.zustand == Kampf.Zustand.AUFTRITT || k.zustand == Kampf.Zustand.LAEUFT);
    }

    // ---------- Schaden ----------

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    void schaden(EntityDamageEvent e) {
        Entity opfer = e.getEntity();
        if (Keys.hat(opfer, Keys.BOSS)) {
            Kampf k = pl.kaempfe.mitBoss(opfer);
            if (k == null) {
                e.setCancelled(true);
                return;
            }
            k.bossSchaden(e);
            return;
        }
        if (e instanceof EntityDamageByEntityEvent be) {
            Entity d = be.getDamager();
            if (Keys.hat(d, Keys.FEUERWERK)) {
                e.setCancelled(true);
                return;
            }
            if (Keys.hat(d, Keys.PFEIL)) {
                e.setDamage(Keys.zahl(d, Keys.PFEIL));
            }
            // Helfer und Bosse verletzen sich nicht gegenseitig
            Entity quelle = d instanceof Projectile pr && pr.getShooter() instanceof Entity s ? s : d;
            if ((istBossOderHelfer(quelle) || Keys.hat(d, Keys.PFEIL)) && Keys.hat(opfer, Keys.HELFER)) {
                e.setCancelled(true);
            }
        }
    }

    @EventHandler(ignoreCancelled = true)
    void schleimTeilen(SlimeSplitEvent e) {
        if (Keys.hat(e.getEntity(), Keys.HELFER)) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void brennen(EntityCombustEvent e) {
        Entity x = e.getEntity();
        if (Keys.hat(x, Keys.BOSS) || Keys.hat(x, Keys.HELFER) || Keys.hat(x, Keys.BEGLEITER)) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void ziel(EntityTargetLivingEntityEvent e) {
        Entity x = e.getEntity();
        LivingEntity z = e.getTarget();
        if (z == null) {
            return;
        }
        if (Keys.hat(x, Keys.BOSS) || Keys.hat(x, Keys.HELFER)) {
            Kampf k = pl.kaempfe.an(x.getLocation());
            if (!(z instanceof Player p) || k == null || !k.lebend(p)) {
                e.setCancelled(true);
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGH)
    void tod(EntityDeathEvent e) {
        Entity x = e.getEntity();
        if (Keys.hat(x, Keys.BOSS)) {
            Kampf k = pl.kaempfe.mitBoss(x);
            if (k != null) {
                k.bossTot(e);
            } else {
                e.getDrops().clear();
                e.setDroppedExp(0);
            }
        } else if (Keys.hat(x, Keys.HELFER) || Keys.hat(x, Keys.BEGLEITER)) {
            e.getDrops().clear();
            e.setDroppedExp(0);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void felsLandet(EntityChangeBlockEvent e) {
        if (e.getEntity() instanceof FallingBlock fb && Keys.hat(fb, Keys.WURF)) {
            e.setCancelled(true);
            Kampf k = pl.kaempfe.an(fb.getLocation());
            if (k != null) {
                k.wurfLandet(fb);
            } else {
                fb.remove();
            }
        }
    }

    // ---------- Spieler ----------

    @EventHandler(priority = EventPriority.HIGHEST)
    void spielerTod(PlayerDeathEvent e) {
        Player p = e.getEntity();
        Kampf k = pl.kaempfe.von(p);
        if (k != null && k.zustand == Kampf.Zustand.LAEUFT && k.arena.enthaelt(p.getLocation())) {
            k.spielerTod(e);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    void wiederbeleben(PlayerRespawnEvent e) {
        Kampf k = pl.kaempfe.von(e.getPlayer());
        if (k != null) {
            Location l = k.wiederbeleben(e.getPlayer());
            if (l != null) {
                e.setRespawnLocation(l);
            }
        }
    }

    @EventHandler
    void verlassen(PlayerQuitEvent e) {
        Kampf k = pl.kaempfe.von(e.getPlayer());
        if (k != null) {
            k.geflohen(e.getPlayer(), "hat den Server verlassen");
        }
    }

    @EventHandler(ignoreCancelled = true)
    void bewegen(PlayerMoveEvent e) {
        Location von = e.getFrom(), nach = e.getTo();
        if (von.getBlockX() == nach.getBlockX() && von.getBlockY() == nach.getBlockY() && von.getBlockZ() == nach.getBlockZ()) {
            return;
        }
        if (grenze(e.getPlayer(), von, nach, false)) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void teleport(PlayerTeleportEvent e) {
        if (e.getTo() != null && grenze(e.getPlayer(), e.getFrom(), e.getTo(), true)) {
            e.setCancelled(true);
        }
    }

    /** Liefert true, wenn die Bewegung verhindert werden soll. */
    private boolean grenze(Player p, Location von, Location nach, boolean teleport) {
        Kampf eigener = pl.kaempfe.von(p);
        if (kaempft(eigener)) {
            Kampf.Teilnehmer t = eigener.teilnehmer(p);
            boolean dabei = t != null && !t.ausgeschieden && !t.geflohen;
            if (dabei && eigener.arena.enthaelt(von) && !eigener.arena.enthaelt(nach)) {
                eigener.geflohen(p, teleport ? "hat sich aus der Arena teleportiert" : "ist aus der Arena geflohen");
                return false;
            }
            if (dabei) {
                return false;
            }
        }
        Kampf fremd = pl.kaempfe.an(nach);
        if (kaempft(fremd) && !fremd.arena.enthaelt(von) && !p.hasPermission("bossraid.admin")) {
            Kampf.Teilnehmer t = fremd.teilnehmer(p);
            if (t == null || t.ausgeschieden || t.geflohen) {
                Txt.an(p, "&7In der Arena läuft ein Boss-Kampf. Rein kommt man erst wieder nach dem Kampf.");
                return true;
            }
        }
        return false;
    }

    // ---------- Arena schützen ----------

    private boolean geschuetzt(Location l) {
        return kaempft(pl.kaempfe.an(l));
    }

    @EventHandler(ignoreCancelled = true)
    void abbauen(BlockBreakEvent e) {
        Block b = e.getBlock();
        if (pl.graeber.grabVon(b) != null) {
            e.setCancelled(true);
            Txt.an(e.getPlayer(), "&7Eine Grabtruhe öffnet man mit Rechtsklick. Abbauen geht nicht.");
            return;
        }
        if (geschuetzt(b.getLocation()) || pl.temp.istTemp(b)) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void anschlagen(BlockDamageEvent e) {
        Kampf k = pl.kaempfe.an(e.getBlock().getLocation());
        if (k != null && k.istVerstaerker(e.getBlock())) {
            e.setCancelled(true);
            k.verstaerkerTreffer(e.getPlayer(), e.getBlock());
        }
    }

    @EventHandler(ignoreCancelled = true)
    void bauen(BlockPlaceEvent e) {
        if (geschuetzt(e.getBlock().getLocation())) {
            e.setCancelled(true);
            Txt.an(e.getPlayer(), "&7Während des Boss-Kampfs kann in der Arena nicht gebaut werden.");
        }
    }

    @EventHandler(ignoreCancelled = true)
    void eimerLeeren(PlayerBucketEmptyEvent e) {
        if (geschuetzt(e.getBlock().getLocation())) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void eimerFuellen(PlayerBucketFillEvent e) {
        if (geschuetzt(e.getBlock().getLocation())) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void explosion(EntityExplodeEvent e) {
        schuetzen(e.blockList());
    }

    @EventHandler(ignoreCancelled = true)
    void blockExplosion(BlockExplodeEvent e) {
        schuetzen(e.blockList());
    }

    private void schuetzen(List<Block> bloecke) {
        bloecke.removeIf(b -> pl.graeber.grabVon(b) != null || pl.temp.istTemp(b) || geschuetzt(b.getLocation()));
    }

    @EventHandler(ignoreCancelled = true)
    void kolbenRaus(BlockPistonExtendEvent e) {
        for (Block b : e.getBlocks()) {
            if (pl.graeber.grabVon(b) != null || pl.temp.istTemp(b)) {
                e.setCancelled(true);
                return;
            }
        }
    }

    @EventHandler(ignoreCancelled = true)
    void kolbenRein(BlockPistonRetractEvent e) {
        for (Block b : e.getBlocks()) {
            if (pl.graeber.grabVon(b) != null || pl.temp.istTemp(b)) {
                e.setCancelled(true);
                return;
            }
        }
    }

    // ---------- übrig gebliebene Wesen ----------

    @EventHandler
    void geladen(EntitiesLoadEvent e) {
        for (Entity x : e.getEntities()) {
            pl.aufraeumen(x);
        }
    }

    static boolean istBossOderHelfer(Entity x) {
        return Keys.hat(x, Keys.BOSS) || Keys.hat(x, Keys.HELFER);
    }

    static boolean mob(Entity x) {
        return x instanceof Mob;
    }
}
