package de.savox.bossraid;

import com.destroystokyo.paper.profile.PlayerProfile;
import com.destroystokyo.paper.profile.ProfileProperty;
import net.kyori.adventure.text.Component;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeModifier;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.EntityType;
import org.bukkit.inventory.EquipmentSlotGroup;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.RecipeChoice;
import org.bukkit.inventory.ShapedRecipe;
import org.bukkit.inventory.ShapelessRecipe;
import org.bukkit.Registry;
import org.bukkit.inventory.meta.EnchantmentStorageMeta;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.inventory.meta.PotionMeta;
import org.bukkit.inventory.meta.SkullMeta;
import org.bukkit.potion.PotionType;
import org.bukkit.persistence.PersistentDataType;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.UUID;

/** Fragmente, Beschwörungsgegenstände, epische Gegenstände und Trophäen aus bosse.yml. */
final class Gegenstaende {
    record Quelle(String fragment, Set<EntityType> mobs, boolean nurNachts, boolean spawnerErlaubt, double chance) {
    }

    private final BossRaidPlugin pl;
    final Map<String, ConfigurationSection> defs = new LinkedHashMap<>();
    final List<Quelle> quellen = new ArrayList<>();
    final List<NamespacedKey> rezepte = new ArrayList<>();
    final List<String> rezeptTexte = new ArrayList<>();

    Gegenstaende(BossRaidPlugin pl) {
        this.pl = pl;
    }

    void laden(ConfigurationSection gegenstaende, ConfigurationSection fragmente) {
        defs.clear();
        quellen.clear();
        if (gegenstaende != null) {
            for (String id : gegenstaende.getKeys(false)) {
                ConfigurationSection s = gegenstaende.getConfigurationSection(id);
                if (s != null) {
                    defs.put(id.toLowerCase(Locale.ROOT), s);
                }
            }
        }
        if (fragmente != null) {
            for (String id : fragmente.getKeys(false)) {
                ConfigurationSection s = fragmente.getConfigurationSection(id);
                if (s == null) {
                    continue;
                }
                Set<EntityType> mobs = new HashSet<>();
                for (String m : s.getStringList("mobs")) {
                    try {
                        mobs.add(EntityType.valueOf(m.toUpperCase(Locale.ROOT)));
                    } catch (IllegalArgumentException e) {
                        pl.getLogger().warning("Unbekanntes Monster in fragmente." + id + ": " + m);
                    }
                }
                quellen.add(new Quelle(id.toLowerCase(Locale.ROOT), mobs, s.getBoolean("nur-nachts", false),
                        s.getBoolean("spawner-erlaubt", false), s.getDouble("chance", 3.0)));
            }
        }
    }

    String art(String id) {
        ConfigurationSection s = defs.get(id);
        return s == null ? "" : s.getString("art", "");
    }

    String name(String id) {
        ConfigurationSection s = defs.get(id);
        return s == null ? id : s.getString("name", id);
    }

    /** ID eines BossRaid-Gegenstands oder null. */
    static String id(ItemStack i) {
        return Keys.text(i, Keys.TEIL);
    }

    static boolean verflucht(ItemStack i) {
        return Keys.hat(i, Keys.VERFLUCHT);
    }

    ItemStack erzeuge(String id, int menge) {
        return erzeuge(id, menge, false);
    }

    ItemStack erzeuge(String id, int menge, boolean verflucht) {
        ConfigurationSection s = defs.get(id.toLowerCase(Locale.ROOT));
        if (s == null) {
            return null;
        }
        Material m = Material.matchMaterial(s.getString("material", "PAPER"));
        if (m == null) {
            m = Material.PAPER;
        }
        ItemStack it = new ItemStack(m, Math.max(1, menge));
        ItemMeta meta = it.getItemMeta();
        String name = s.getString("name", id);
        if (verflucht) {
            name = "&4Verfluchter " + name.replaceAll("^&[0-9a-fk-or]", "");
        }
        meta.displayName(Txt.komp(name));
        List<Component> lore = new ArrayList<>();
        for (String z : s.getStringList("text")) {
            lore.add(Txt.komp("&7" + z));
        }
        if (verflucht) {
            lore.add(Txt.komp("&cRuft den Boss auf der Stufe schwer, mit besserem Loot."));
        }
        meta.lore(lore);
        meta.getPersistentDataContainer().set(Keys.TEIL, PersistentDataType.STRING, id.toLowerCase(Locale.ROOT));
        if (verflucht) {
            meta.getPersistentDataContainer().set(Keys.VERFLUCHT, PersistentDataType.BYTE, (byte) 1);
        }
        if (s.getBoolean("glanz", false) || verflucht) {
            meta.setEnchantmentGlintOverride(true);
        }
        for (String v : s.getStringList("verzauberungen")) {
            String[] p = v.split(":");
            Enchantment e = Attr.verzauberung(p[0]);
            if (e != null) {
                meta.addEnchant(e, p.length > 1 ? Integer.parseInt(p[1].trim()) : 1, true);
            }
        }
        ConfigurationSection attr = s.getConfigurationSection("attribute");
        if (attr != null) {
            EquipmentSlotGroup slot = EquipmentSlotGroup.getByName(s.getString("slot", "any"));
            if (slot == null) {
                slot = EquipmentSlotGroup.ANY;
            }
            for (String k : attr.getKeys(false)) {
                Attribute a = Attr.finde(k, "generic." + k);
                if (a != null) {
                    meta.addAttributeModifier(a, new AttributeModifier(new NamespacedKey(pl, id + "_" + k),
                            attr.getDouble(k), AttributeModifier.Operation.ADD_NUMBER, slot));
                }
            }
        }
        if (meta instanceof SkullMeta skull && !s.getString("textur", "").isEmpty()) {
            PlayerProfile profil = Bukkit.createProfile(UUID.nameUUIDFromBytes(("bossraid:" + id).getBytes()), "BossRaid");
            profil.setProperty(new ProfileProperty("textures", s.getString("textur")));
            skull.setPlayerProfile(profil);
        }
        it.setItemMeta(meta);
        return it;
    }

    /** Rezepte für alle Beschwörungsgegenstände anmelden: 8 Fragmente um einen Kern, verflucht mit einer Zusatz-Zutat. */
    void rezepteAnmelden() {
        for (NamespacedKey k : rezepte) {
            Bukkit.removeRecipe(k);
        }
        rezepte.clear();
        rezeptTexte.clear();
        for (Map.Entry<String, ConfigurationSection> e : defs.entrySet()) {
            ConfigurationSection r = e.getValue().getConfigurationSection("rezept");
            if (r == null) {
                continue;
            }
            String id = e.getKey();
            String teil = r.getString("teil", "").toLowerCase(Locale.ROOT);
            ItemStack fragment = erzeuge(teil, 1);
            Material kern = Material.matchMaterial(r.getString("kern", ""));
            ItemStack ergebnis = erzeuge(id, 1);
            if (fragment == null || kern == null || ergebnis == null) {
                pl.getLogger().warning("Rezept für " + id + " unvollständig (teil oder kern fehlt)");
                continue;
            }
            NamespacedKey k = new NamespacedKey(pl, "rezept_" + id);
            ShapedRecipe sr = new ShapedRecipe(k, ergebnis);
            sr.shape("TTT", "TKT", "TTT");
            sr.setIngredient('T', new RecipeChoice.ExactChoice(fragment));
            sr.setIngredient('K', kern);
            if (Bukkit.addRecipe(sr)) {
                rezepte.add(k);
            }
            String text = "&f" + name(id) + "&7: 8× " + name(teil) + " &7um 1× " + kernName(kern);
            Material fluch = Material.matchMaterial(r.getString("verflucht", ""));
            if (fluch != null) {
                NamespacedKey kv = new NamespacedKey(pl, "rezept_" + id + "_verflucht");
                ShapelessRecipe vr = new ShapelessRecipe(kv, erzeuge(id, 1, true));
                vr.addIngredient(new RecipeChoice.ExactChoice(ergebnis));
                vr.addIngredient(fluch);
                if (Bukkit.addRecipe(vr)) {
                    rezepte.add(kv);
                }
                text += "&7, verflucht: + 1× " + kernName(fluch);
            }
            rezeptTexte.add(text);
        }
    }

    private static String kernName(Material m) {
        String n = m.name().toLowerCase(Locale.ROOT).replace('_', ' ');
        return Character.toUpperCase(n.charAt(0)) + n.substring(1);
    }

    // ---------- Loot-Einträge ----------

    /**
     * Ein Loot-Eintrag aus bosse.yml, z. B. "DIAMOND 3-6", "DIAMOND_SWORD 1 smite:6" oder "@seelenstab".
     */
    ItemStack lootErzeugen(String eintrag, Random r, double faktor) {
        String[] t = eintrag.trim().split("\\s+");
        if (t.length == 0 || t[0].isEmpty()) {
            return null;
        }
        int min = 1, max = 1;
        if (t.length > 1 && t[1].matches("\\d+(-\\d+)?")) {
            String[] mm = t[1].split("-");
            min = Integer.parseInt(mm[0]);
            max = mm.length > 1 ? Integer.parseInt(mm[1]) : min;
        }
        int menge = min + (max > min ? r.nextInt(max - min + 1) : 0);
        menge = Math.max(1, (int) Math.round(menge * faktor));
        if (t[0].startsWith("@")) {
            return erzeuge(t[0].substring(1), menge);
        }
        Material m = Material.matchMaterial(t[0]);
        if (m == null || m.isAir()) {
            pl.getLogger().warning("Unbekannter Loot-Eintrag: " + eintrag);
            return null;
        }
        ItemStack it = new ItemStack(m, Math.min(menge, m.getMaxStackSize()));
        ItemMeta meta = it.getItemMeta();
        for (int i = 1; i < t.length; i++) {
            if (!t[i].contains(":")) {
                continue;
            }
            String[] p = t[i].split(":");
            if (p[0].equalsIgnoreCase("trank")) {
                PotionType typ = Registry.POTION.get(NamespacedKey.minecraft(p[1].toLowerCase(Locale.ROOT)));
                if (meta instanceof PotionMeta pm && typ != null) {
                    pm.setBasePotionType(typ);
                }
                continue;
            }
            Enchantment e = Attr.verzauberung(p[0]);
            if (e != null && meta != null) {
                try {
                    int stufe = Integer.parseInt(p[1]);
                    if (meta instanceof EnchantmentStorageMeta buch) {
                        buch.addStoredEnchant(e, stufe, true);
                    } else {
                        meta.addEnchant(e, stufe, true);
                    }
                } catch (NumberFormatException ignored) {
                    // falsche Stufe
                }
            }
        }
        if (meta != null) {
            it.setItemMeta(meta);
        }
        return it;
    }
}
