plugins {
    java
}

group = "de.savox"
version = "0.1.0"

repositories {
    mavenCentral()
    maven("https://repo.papermc.io/repository/maven-public/")
}

dependencies {
    compileOnly("io.papermc.paper:paper-api:1.21.4-R0.1-SNAPSHOT")
}

java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(21))
}

tasks.withType<JavaCompile> {
    options.encoding = "UTF-8"
    options.release.set(21)
    options.compilerArgs.add("-Xlint:-deprecation")
}

tasks.processResources {
    filteringCharset = "UTF-8"
    filesMatching("plugin.yml") {
        expand("version" to project.version)
    }
}

tasks.jar {
    archiveBaseName.set("BossRaid")
}

// Nur für die lokale Prüfung: legt alle Bibliotheken zum Kompilieren in build/klassenpfad ab
tasks.register<Copy>("klassenpfad") {
    from(configurations.compileClasspath)
    into(layout.buildDirectory.dir("klassenpfad"))
}
