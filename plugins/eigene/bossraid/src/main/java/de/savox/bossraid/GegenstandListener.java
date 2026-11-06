package de.savox.bossraid;

import org.bukkit.Bukkit;
import org.bukkit.Keyed;
import org.bukkit.Location;
import org.bukkit.NamespacedKey;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.block.Block;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Mob;
import org.bukkit.entity.Monster;
import org.bukkit.entity.Player;
import org.bukkit.entity.Skeleton;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.EntityPotionEffectEvent;
import org.bukkit.event.entity.EntityTargetLivingEntityEvent;
import org.bukkit.event.inventory.BrewingStandFuelEvent;
import org.bukkit.event.inventory.FurnaceBurnEvent;
import org.bukkit.event.inventory.FurnaceSmeltEvent;
import org.bukkit.event.inventory.PrepareItemCraftEvent;
import org.bukkit.event.player.PlayerInteractEntityEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerItemConsumeEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.Recipe;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.potion.PotionEffect;

import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.UUID;

/** Fragmente, Rezepte, Altar, Grabtruhen, Torstab und die Fähigkeiten der epischen Gegenstände. */
final class GegenstandListener implements Listener {
    private static final Random ZUFALL = new Random();
    private final BossRaidPlugin pl;
    private final Map<UUID, Long> stabBereit = new HashMap<>();
    private final Map<UUID, Long> begleiterBis = new HashMap<>();

    GegenstandListener(BossRaidPlugin pl) {
        this.pl = pl;
        Bukkit.getScheduler().runTaskTimer(pl, this::begleiterTick, 20, 20);
    }

    private String faehigkeit(ItemStack i) {
        String id = Gegenstaende.id(i);
        if (id == null) {
            return null;
        }
        ConfigurationSection s = pl.gegenstaende.defs.get(id);
        return s == null ? null : s.getString("faehigkeit");
    }

    /** Fragmente und Beschwörungsgegenstände sind nur zum Herstellen und für den Altar da. */
    private boolean geschuetzt(ItemStack i) {
        String id = Gegenstaende.id(i);
        if (id == null) {
            return false;
        }
        String art = pl.gegenstaende.art(id);
        return art.equals("fragment") || art.equals("beschwoerung") || (art.equals("episch") && faehigkeit(i) != null);
    }

    // ---------- Fragmente ----------

    @EventHandler(priority = EventPriority.HIGH)
    void fragment(EntityDeathEvent e) {
        LivingEntity x = e.getEntity();
        Player killer = x.getKiller();
        if (killer == null || Keys.hat(x, Keys.HELFER) || Keys.hat(x, Keys.BOSS) || Keys.hat(x, Keys.BEGLEITER)) {
            return;
        }
        if (pl.speicher.arenaAn(x.getLocation()) != null) {
            return;
        }
        String grund = x.getEntitySpawnReason().name();
        boolean ausSpawner = grund.contains("SPAWNER");
        long zeit = x.getWorld().getTime();
        boolean nacht = zeit >= 13000 && zeit <= 23000;
        for (Gegenstaende.Quelle q : pl.gegenstaende.quellen) {
            if (!q.mobs().contains(x.getType()) || (q.nurNachts() && !nacht) || (ausSpawner && !q.spawnerErlaubt())) {
                continue;
            }
            if (ZUFALL.nextDouble() * 100 >= q.chance()) {
                continue;
            }
            int stand = pl.speicher.fragmentZaehlen(killer.getUniqueId(), pl.einst.fragmentTageslimit);
            if (stand < 0) {
                return;
            }
            ItemStack f = pl.gegenstaende.erzeuge(q.fragment(), 1);
            if (f != null) {
                e.getDrops().add(f);
                Txt.an(killer, "&dEin Fragment! &f" + Txt.c(pl.gegenstaende.name(q.fragment())) + " &7(" + stand + " von "
                        + pl.einst.fragmentTageslimit + " heute)");
                killer.playSound(killer.getLocation(), Sound.BLOCK_AMETHYST_BLOCK_CHIME, 1f, 1.2f);
            }
            return;
        }
    }

    // ---------- Schutz der Gegenstände ----------

    @EventHandler
    void rezept(PrepareItemCraftEvent e) {
        boolean eigeneTeile = false;
        for (ItemStack i : e.getInventory().getMatrix()) {
            if (i != null && Gegenstaende.id(i) != null) {
                eigeneTeile = true;
                break;
            }
        }
        if (!eigeneTeile) {
            return;
        }
        Recipe r = e.getRecipe();
        boolean unser = r instanceof Keyed k && k.getKey().getNamespace().equals(new NamespacedKey(pl, "x").getNamespace());
        if (!unser) {
            e.getInventory().setResult(null);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void brennstoff(FurnaceBurnEvent e) {
        if (Gegenstaende.id(e.getFuel()) != null) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void schmelzen(FurnaceSmeltEvent e) {
        if (Gegenstaende.id(e.getSource()) != null) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void braustand(BrewingStandFuelEvent e) {
        if (Gegenstaende.id(e.getFuel()) != null) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void platzieren(BlockPlaceEvent e) {
        if (geschuetzt(e.getItemInHand())) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void essen(PlayerItemConsumeEvent e) {
        if (geschuetzt(e.getItem())) {
            e.setCancelled(true);
        }
    }

    @EventHandler(ignoreCancelled = true)
    void anWesen(PlayerInteractEntityEvent e) {
        ItemStack hand = e.getPlayer().getInventory().getItem(e.getHand());
        if (geschuetzt(hand)) {
            e.setCancelled(true);
        }
    }

    @EventHandler
    void beitritt(PlayerJoinEvent e) {
        e.getPlayer().discoverRecipes(pl.gegenstaende.rezepte);
    }

    // ---------- Klicks: Grabtruhe, Altar, Torstab, Seelenstab ----------

    @EventHandler(priority = EventPriority.LOW)
    void klick(PlayerInteractEvent e) {
        Player p = e.getPlayer();
        Block b = e.getClickedBlock();
        ItemStack hand = e.getItem();
        Action a = e.getAction();

        if (a == Action.RIGHT_CLICK_BLOCK && b != null) {
            Graeber.Grab g = pl.graeber.grabVon(b);
            if (g != null) {
                e.setCancelled(true);
                if (e.getHand() == EquipmentSlot.HAND) {
                    pl.graeber.oeffnen(p, g);
                }
                return;
            }
        }
        if (Keys.hat(hand, Keys.TORSTAB) && b != null && (a == Action.LEFT_CLICK_BLOCK || a == Action.RIGHT_CLICK_BLOCK)) {
            e.setCancelled(true);
            if (e.getHand() == EquipmentSlot.HAND) {
                pl.befehle.torstabKlick(p, b);
            }
            return;
        }
        if (e.getHand() != EquipmentSlot.HAND) {
            if (geschuetzt(hand)) {
                e.setCancelled(true);
            }
            return;
        }
        String id = Gegenstaende.id(hand);
        if (id != null && a == Action.RIGHT_CLICK_BLOCK && pl.gegenstaende.art(id).equals("beschwoerung")) {
            Arena ar = pl.speicher.arenaMitAltar(b);
            e.setCancelled(true);
            if (ar != null) {
                pl.kaempfe.altarBenutzt(p, ar, hand);
            } else {
                Txt.an(p, "&7Lege den Gegenstand mit Rechtsklick auf den Altar einer Boss-Arena.");
            }
            return;
        }
        if ((a == Action.RIGHT_CLICK_AIR || a == Action.RIGHT_CLICK_BLOCK) && "seelenstab".equals(faehigkeit(hand))) {
            e.setCancelled(true);
            seelenstab(p, hand);
            return;
        }
        if (geschuetzt(hand) && (a == Action.RIGHT_CLICK_AIR || a == Action.RIGHT_CLICK_BLOCK)) {
            e.setCancelled(true);
        }
    }

    // ---------- Seelenstab: zwei Skelett-Helfer ----------

    private void seelenstab(Player p, ItemStack stab) {
        ConfigurationSection s = pl.gegenstaende.defs.get(Gegenstaende.id(stab));
        int abklingen = s == null ? 120 : s.getInt("abklingzeit", 120);
        int dauer = s == null ? 30 : s.getInt("dauer", 30);
        int anzahl = s == null ? 2 : s.getInt("anzahl", 2);
        long jetzt = System.currentTimeMillis();
        Long bereit = stabBereit.get(p.getUniqueId());
        if (bereit != null && bereit > jetzt) {
            Txt.an(p, "&7Der Seelenstab lädt noch &f" + Txt.zeit((int) ((bereit - jetzt) / 1000)) + "&7.");
            return;
        }
        stabBereit.put(p.getUniqueId(), jetzt + abklingen * 1000L);
        for (int i = 0; i < anzahl; i++) {
            Location l = p.getLocation().add(ZUFALL.nextDouble() * 3 - 1.5, 0, ZUFALL.nextDouble() * 3 - 1.5);
            Skeleton sk = p.getWorld().spawn(l, Skeleton.class, x -> {
                x.setPersistent(false);
                x.getPersistentDataContainer().set(Keys.BEGLEITER, PersistentDataType.STRING, p.getUniqueId().toString());
                x.customName(Txt.komp("&bSeelenkrieger von " + p.getName()));
                x.setCustomNameVisible(false);
                x.setRemoveWhenFarAway(false);
                if (x.getEquipment() != null) {
                    x.getEquipment().setItemInMainHandDropChance(0);
                }
            });
            begleiterBis.put(sk.getUniqueId(), jetzt + dauer * 1000L);
            l.getWorld().spawnParticle(Particle.SOUL, l.clone().add(0, 1, 0), 15, 0.3, 0.6, 0.3, 0.02);
        }
        p.playSound(p.getLocation(), Sound.ENTITY_EVOKER_PREPARE_SUMMON, 1f, 1f);
        Txt.an(p, "&bZwei Seelenkrieger kämpfen &f" + dauer + " s &bfür dich.");
    }

    private void begleiterTick() {
        long jetzt = System.currentTimeMillis();
        begleiterBis.entrySet().removeIf(en -> {
            Entity x = Bukkit.getEntity(en.getKey());
            if (x == null || !x.isValid()) {
                return true;
            }
            if (en.getValue() < jetzt) {
                x.getWorld().spawnParticle(Particle.SOUL, x.getLocation().add(0, 1, 0), 10, 0.3, 0.5, 0.3, 0.02);
                x.remove();
                return true;
            }
            if (x instanceof Mob m && (m.getTarget() == null || !m.getTarget().isValid())) {
                LivingEntity best = null;
                double d = 16 * 16;
                for (Entity n : x.getNearbyEntities(16, 8, 16)) {
                    if (n instanceof LivingEntity le && !Keys.hat(n, Keys.BEGLEITER) && (n instanceof Monster || Keys.hat(n, Keys.BOSS))) {
                        double dd = n.getLocation().distanceSquared(x.getLocation());
                        if (dd < d) {
                            d = dd;
                            best = le;
                        }
                    }
                }
                if (best != null) {
                    m.setTarget(best);
                }
            }
            return false;
        });
    }

    boolean istBegleiter(Entity x) {
        return begleiterBis.containsKey(x.getUniqueId());
    }

    @EventHandler(ignoreCancelled = true)
    void begleiterZiel(EntityTargetLivingEntityEvent e) {
        if (Keys.hat(e.getEntity(), Keys.BEGLEITER) && (e.getTarget() instanceof Player || Keys.hat(e.getTarget(), Keys.BEGLEITER))) {
            e.setCancelled(true);
        }
    }

    // ---------- Hexenbeutel: Trankeffekte doppelt so lang ----------

    @EventHandler(ignoreCancelled = true)
    void trank(EntityPotionEffectEvent e) {
        if (!(e.getEntity() instanceof Player p) || e.getNewEffect() == null) {
            return;
        }
        EntityPotionEffectEvent.Cause c = e.getCause();
        if (c != EntityPotionEffectEvent.Cause.POTION_DRINK && c != EntityPotionEffectEvent.Cause.POTION_SPLASH
                && c != EntityPotionEffectEvent.Cause.AREA_EFFECT_CLOUD) {
            return;
        }
        if (!"hexenbeutel".equals(faehigkeit(p.getInventory().getItemInOffHand()))) {
            return;
        }
        PotionEffect alt = e.getNewEffect();
        if (alt.getType().isInstant() || alt.getDuration() <= 1) {
            return;
        }
        e.setCancelled(true);
        PotionEffect neu = new PotionEffect(alt.getType(), alt.getDuration() * 2, alt.getAmplifier(), alt.isAmbient(), alt.hasParticles(), alt.hasIcon());
        Bukkit.getScheduler().runTask(pl, () -> p.addPotionEffect(neu));
    }

    static String klein(String s) {
        return s.toLowerCase(Locale.ROOT);
    }
}
