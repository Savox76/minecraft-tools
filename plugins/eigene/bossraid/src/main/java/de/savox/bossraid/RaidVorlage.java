package de.savox.bossraid;

import java.util.ArrayList;
import java.util.List;

/** Eine gespeicherte Raid-Vorlage: welcher Boss, wo, und nach welchen Regeln. */
final class RaidVorlage {
    final String name;
    String boss;
    String arena;
    Stufe stufe = Stufe.NORMAL;
    Todesregel tod = Todesregel.GRABTRUHE;
    int leben = 3;
    int zeitMinuten = 15;
    int leerSekunden = 60;
    int spielerMin = 1;
    int spielerMax = 8;
    double loot = 1.0;
    int abklingzeitMinuten = 60;
    boolean beschwoerung = true;

    int siege;
    int gescheitert;
    int besteZeit;   // Sekunden, 0 = noch keine
    final List<String> letzteRangliste = new ArrayList<>();

    RaidVorlage(String name) {
        this.name = name;
    }
}
