package de.savox.bossraid;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.TextDecoration;
import net.kyori.adventure.text.serializer.legacy.LegacyComponentSerializer;
import org.bukkit.Bukkit;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

import java.util.Collection;

/** Texte und Farben. Im Code und in den Configs steht &a, &7 usw. für Farben. */
final class Txt {
    static final String PREFIX = "§5[BossRaid] §7";

    private Txt() {
    }

    static String c(String s) {
        return s == null ? "" : s.replace('&', '§');
    }

    static void an(CommandSender s, String text) {
        s.sendMessage(PREFIX + c(text));
    }

    static void an(Collection<? extends Player> spieler, String text) {
        for (Player p : spieler) {
            an(p, text);
        }
    }

    static void alle(String text) {
        an(Bukkit.getOnlinePlayers(), text);
        Bukkit.getConsoleSender().sendMessage(PREFIX + c(text));
    }

    /** Für Gegenstands-Namen und Beschreibungen: ohne Kursivschrift. */
    static Component komp(String text) {
        return LegacyComponentSerializer.legacySection().deserialize(c(text)).decoration(TextDecoration.ITALIC, false);
    }

    static String zeit(int sekunden) {
        if (sekunden < 0) {
            sekunden = 0;
        }
        return String.format("%d:%02d", sekunden / 60, sekunden % 60);
    }

    static String prozent(double anteil) {
        return Math.round(anteil * 100) + " %";
    }
}
