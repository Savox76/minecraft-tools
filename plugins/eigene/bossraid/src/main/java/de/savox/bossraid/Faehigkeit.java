package de.savox.bossraid;

import org.bukkit.configuration.ConfigurationSection;

import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Eine Fähigkeit aus dem Baukasten, eingestellt in bosse.yml.
 * Gemeinsame Werte: art, alle (Sekunden), ab-phase, bis-phase, warnung (Sekunden), text (Ansage).
 */
final class Faehigkeit {
    final String art;
    final int alle;
    final int abPhase;
    final int bisPhase;
    final double warnung;
    final String text;
    private final Map<String, Object> werte = new HashMap<>();

    Faehigkeit(Map<?, ?> m) {
        for (Map.Entry<?, ?> e : m.entrySet()) {
            werte.put(String.valueOf(e.getKey()).toLowerCase(Locale.ROOT), e.getValue());
        }
        art = s("art", "").toLowerCase(Locale.ROOT);
        alle = i("alle", 15);
        abPhase = i("ab-phase", 1);
        bisPhase = i("bis-phase", 3);
        warnung = d("warnung", 1.0);
        text = s("text", null);
    }

    static Faehigkeit aus(ConfigurationSection s) {
        return new Faehigkeit(s.getValues(false));
    }

    boolean inPhase(int phase) {
        return phase >= abPhase && phase <= bisPhase;
    }

    String s(String k, String def) {
        Object o = werte.get(k);
        return o == null ? def : String.valueOf(o);
    }

    int i(String k, int def) {
        Object o = werte.get(k);
        if (o instanceof Number n) {
            return n.intValue();
        }
        try {
            return o == null ? def : Integer.parseInt(String.valueOf(o));
        } catch (NumberFormatException e) {
            return def;
        }
    }

    double d(String k, double def) {
        Object o = werte.get(k);
        if (o instanceof Number n) {
            return n.doubleValue();
        }
        try {
            return o == null ? def : Double.parseDouble(String.valueOf(o));
        } catch (NumberFormatException e) {
            return def;
        }
    }

    boolean b(String k, boolean def) {
        Object o = werte.get(k);
        return o == null ? def : Boolean.parseBoolean(String.valueOf(o));
    }

    @SuppressWarnings("unchecked")
    List<String> liste(String k) {
        Object o = werte.get(k);
        return o instanceof List<?> l ? (List<String>) l : List.of();
    }
}
