package de.savox.bossraid;

import java.util.Locale;

enum Stufe {
    LEICHT, NORMAL, SCHWER;

    static Stufe von(String s) {
        if (s == null) {
            return null;
        }
        for (Stufe x : values()) {
            if (x.id().equals(s.toLowerCase(Locale.ROOT))) {
                return x;
            }
        }
        return null;
    }

    String id() {
        return name().toLowerCase(Locale.ROOT);
    }
}
