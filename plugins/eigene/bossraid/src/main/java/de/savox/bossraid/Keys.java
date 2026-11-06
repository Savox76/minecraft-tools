package de.savox.bossraid;

import org.bukkit.NamespacedKey;
import org.bukkit.entity.Entity;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.Plugin;

/** Unsichtbare Markierungen an Wesen und Gegenständen. */
final class Keys {
    static NamespacedKey BOSS;        // Wesen ist ein Boss (Wert: Arena)
    static NamespacedKey HELFER;      // beschworener Helfer eines Bosses (Wert: Arena)
    static NamespacedKey HEILT;       // Helfer heilt den Boss, wenn er ihn erreicht (Wert: Prozent)
    static NamespacedKey PFEIL;       // Geschoss eines Bosses (Wert: Schaden)
    static NamespacedKey WURF;        // geworfener Felsbrocken (Wert: Schaden)
    static NamespacedKey BEGLEITER;   // Skelett-Helfer aus dem Seelenstab (Wert: Besitzer-UUID)
    static NamespacedKey FEUERWERK;   // Siegesfeuerwerk, macht keinen Schaden
    static NamespacedKey TEIL;        // Gegenstand aus BossRaid (Wert: ID)
    static NamespacedKey VERFLUCHT;   // verfluchter Beschwörungsgegenstand
    static NamespacedKey TORSTAB;     // Stab zum Markieren der Tor-Blöcke
    static NamespacedKey GRAB;        // Grabtruhe (Wert: Grab-ID)

    private Keys() {
    }

    static void init(Plugin p) {
        BOSS = new NamespacedKey(p, "boss");
        HELFER = new NamespacedKey(p, "helfer");
        HEILT = new NamespacedKey(p, "heilt");
        PFEIL = new NamespacedKey(p, "pfeil");
        WURF = new NamespacedKey(p, "wurf");
        BEGLEITER = new NamespacedKey(p, "begleiter");
        FEUERWERK = new NamespacedKey(p, "feuerwerk");
        TEIL = new NamespacedKey(p, "teil");
        VERFLUCHT = new NamespacedKey(p, "verflucht");
        TORSTAB = new NamespacedKey(p, "torstab");
        GRAB = new NamespacedKey(p, "grab");
    }

    static boolean hat(Entity e, NamespacedKey k) {
        return e != null && e.getPersistentDataContainer().has(k);
    }

    static String text(Entity e, NamespacedKey k) {
        return e == null ? null : e.getPersistentDataContainer().get(k, PersistentDataType.STRING);
    }

    static double zahl(Entity e, NamespacedKey k) {
        Double d = e == null ? null : e.getPersistentDataContainer().get(k, PersistentDataType.DOUBLE);
        return d == null ? 0 : d;
    }

    static String text(ItemStack i, NamespacedKey k) {
        if (i == null || !i.hasItemMeta()) {
            return null;
        }
        ItemMeta m = i.getItemMeta();
        return m.getPersistentDataContainer().get(k, PersistentDataType.STRING);
    }

    static boolean hat(ItemStack i, NamespacedKey k) {
        return i != null && i.hasItemMeta() && i.getItemMeta().getPersistentDataContainer().has(k);
    }
}
