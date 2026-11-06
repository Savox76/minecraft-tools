package de.savox.bossraid;

import io.papermc.paper.registry.RegistryAccess;
import io.papermc.paper.registry.RegistryKey;
import org.bukkit.NamespacedKey;
import org.bukkit.Registry;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeInstance;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.LivingEntity;
import org.bukkit.potion.PotionEffectType;

/**
 * Attribute, Verzauberungen und Effekte über ihren Namen suchen.
 * So läuft das Plugin auf älteren (generic.max_health) und neueren (max_health) Paper-Versionen.
 */
final class Attr {
    static final String[] LEBEN = {"max_health", "generic.max_health"};
    static final String[] SCHADEN = {"attack_damage", "generic.attack_damage"};
    static final String[] RUESTUNG = {"armor", "generic.armor"};
    static final String[] HAERTE = {"armor_toughness", "generic.armor_toughness"};
    static final String[] TEMPO = {"movement_speed", "generic.movement_speed"};
    static final String[] RUECKSTOSS = {"knockback_resistance", "generic.knockback_resistance"};
    static final String[] GROESSE = {"scale", "generic.scale"};
    static final String[] FOLGEN = {"follow_range", "generic.follow_range"};

    private Attr() {
    }

    static Attribute finde(String... namen) {
        for (String n : namen) {
            Attribute a = Registry.ATTRIBUTE.get(NamespacedKey.minecraft(n));
            if (a != null) {
                return a;
            }
        }
        return null;
    }

    static AttributeInstance instanz(LivingEntity e, String... namen) {
        Attribute a = finde(namen);
        if (a == null) {
            return null;
        }
        AttributeInstance i = e.getAttribute(a);
        if (i == null) {
            try {
                e.registerAttribute(a);
                i = e.getAttribute(a);
            } catch (Throwable ignored) {
                return null;
            }
        }
        return i;
    }

    static void setze(LivingEntity e, double wert, String... namen) {
        AttributeInstance i = instanz(e, namen);
        if (i != null) {
            i.setBaseValue(wert);
        }
    }

    static double wert(LivingEntity e, String... namen) {
        AttributeInstance i = instanz(e, namen);
        return i == null ? 0 : i.getValue();
    }

    static Enchantment verzauberung(String name) {
        if (name == null) {
            return null;
        }
        return RegistryAccess.registryAccess().getRegistry(RegistryKey.ENCHANTMENT)
                .get(NamespacedKey.minecraft(name.toLowerCase(java.util.Locale.ROOT)));
    }

    static PotionEffectType effekt(String name) {
        if (name == null) {
            return null;
        }
        return Registry.EFFECT.get(NamespacedKey.minecraft(name.toLowerCase(java.util.Locale.ROOT)));
    }
}
