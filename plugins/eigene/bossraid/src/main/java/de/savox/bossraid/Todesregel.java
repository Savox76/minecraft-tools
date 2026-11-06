package de.savox.bossraid;

import java.util.Locale;

/** Was mit den Sachen eines Spielers passiert, der im Raid stirbt. */
enum Todesregel {
    /** Sachen fallen in der Arena, eine Zeit lang nur für den Besitzer aufhebbar. */
    NORMAL("normal", "Sachen fallen, nur du kannst sie aufheben"),
    /** Sachen kommen in eine Grabtruhe, die nur der Besitzer öffnen kann. */
    GRABTRUHE("grabtruhe", "Sachen kommen in deine Grabtruhe"),
    /** Man behält alles, verliert aber die Hälfte der Level. */
    BEHALTEN("behalten", "du behältst alles, verlierst aber die Hälfte der Level");

    final String id;
    final String text;

    Todesregel(String id, String text) {
        this.id = id;
        this.text = text;
    }

    static Todesregel von(String s) {
        if (s == null) {
            return null;
        }
        for (Todesregel t : values()) {
            if (t.id.equals(s.toLowerCase(Locale.ROOT))) {
                return t;
            }
        }
        return null;
    }
}
