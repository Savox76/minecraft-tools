package de.savox.bossraid;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.Bukkit;
import org.bukkit.Sound;
import org.bukkit.entity.Item;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;

/** Persönlicher Loot nach Schadensanteil. */
final class Loot {
    private static final Random ZUFALL = new Random();

    private Loot() {
    }

    static List<Map.Entry<Kampf.Teilnehmer, Double>> rangliste(Kampf k) {
        double summe = 0;
        for (Kampf.Teilnehmer t : k.teilnehmer.values()) {
            summe += t.schaden;
        }
        List<Map.Entry<Kampf.Teilnehmer, Double>> l = new ArrayList<>();
        for (Kampf.Teilnehmer t : k.teilnehmer.values()) {
            l.add(new AbstractMap.SimpleEntry<>(t, summe > 0 ? t.schaden / summe : 0));
        }
        l.sort((a, b) -> Double.compare(b.getValue(), a.getValue()));
        return l;
    }

    static void verteilen(Kampf k, List<Map.Entry<Kampf.Teilnehmer, Double>> rang) {
        BossRaidPlugin pl = k.pl;
        double sf = pl.einst.stufe(k.stufe).loot() * k.raid.loot;
        for (Map.Entry<Kampf.Teilnehmer, Double> r : rang) {
            Kampf.Teilnehmer t = r.getKey();
            double anteil = r.getValue();
            Player p = Bukkit.getPlayer(t.id);
            if (p == null || !p.isOnline() || t.geflohen) {
                continue;
            }
            if (anteil < pl.einst.mindestAnteil) {
                Txt.an(p, "&7Du hast weniger als " + Txt.prozent(pl.einst.mindestAnteil) + " des Schadens gemacht und bekommst keinen Loot.");
                continue;
            }
            List<ItemStack> beute = new ArrayList<>();
            for (String s : k.typ.sicher) {
                ItemStack i = pl.gegenstaende.lootErzeugen(s, ZUFALL, sf);
                if (i != null) {
                    beute.add(i);
                }
            }
            String besonders = null;
            ItemStack selten = ziehen(k, k.typ.selten, sf, anteil);
            if (selten != null) {
                beute.add(selten);
                besonders = "&9Selten";
            }
            ItemStack episch = ziehen(k, k.typ.episch, sf, anteil);
            if (episch != null) {
                beute.add(episch);
                besonders = "&dEpisch";
                Txt.an(k.online(), "&d★ " + p.getName() + " &derhält einen epischen Gegenstand!");
            }
            ItemStack trophaee = ziehen(k, k.typ.trophaee, sf, anteil);
            if (trophaee != null) {
                beute.add(trophaee);
            }
            int xp = (int) Math.round(k.typ.erfahrung * sf);
            if (xp > 0) {
                p.giveExp(xp);
            }
            for (ItemStack i : beute) {
                for (ItemStack rest : p.getInventory().addItem(i).values()) {
                    Item it = p.getWorld().dropItem(p.getLocation(), rest);
                    it.setOwner(p.getUniqueId());
                }
            }
            p.sendMessage(Component.text("[BossRaid] ", NamedTextColor.DARK_PURPLE).append(beuteText(beute, xp)));
            p.playSound(p.getLocation(), besonders != null ? Sound.UI_TOAST_CHALLENGE_COMPLETE : Sound.ENTITY_PLAYER_LEVELUP, 1f, 1f);
        }
    }

    private static ItemStack ziehen(Kampf k, BossTyp.LootTopf topf, double sf, double anteil) {
        if (topf == null || topf.eintraege().isEmpty()) {
            return null;
        }
        double chance = Math.min(100, topf.chance() * sf * (0.5 + anteil));
        if (ZUFALL.nextDouble() * 100 >= chance) {
            return null;
        }
        String e = topf.eintraege().get(ZUFALL.nextInt(topf.eintraege().size()));
        return k.pl.gegenstaende.lootErzeugen(e, ZUFALL, 1);
    }

    /** "Deine Beute: 4× Diamant, Schwert ..." in der Sprache des Spielers. */
    private static Component beuteText(List<ItemStack> beute, int xp) {
        Component c = Component.text("Deine Beute: ", NamedTextColor.GOLD);
        boolean erst = true;
        for (ItemStack i : beute) {
            if (!erst) {
                c = c.append(Component.text(", ", NamedTextColor.GRAY));
            }
            erst = false;
            ItemMeta m = i.getItemMeta();
            Component name = m != null && m.hasDisplayName() && m.displayName() != null ? m.displayName() : Component.translatable(i.translationKey());
            c = c.append(Component.text(i.getAmount() + "× ", NamedTextColor.WHITE)).append(name.colorIfAbsent(NamedTextColor.WHITE));
            if (m != null && !m.getEnchants().isEmpty() && !Keys.hat(i, Keys.TEIL)) {
                c = c.append(Component.text(" (verzaubert)", NamedTextColor.AQUA));
            }
        }
        if (xp > 0) {
            c = c.append(Component.text(erst ? "" : ", ", NamedTextColor.GRAY)).append(Component.text(xp + " Erfahrung", NamedTextColor.GREEN));
        }
        return c;
    }
}
