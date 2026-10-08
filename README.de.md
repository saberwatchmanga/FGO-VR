# FGO VR — PCVR 0.2.1 / Quest 3 0.2.0

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Português](README.pt.md) | [Italiano](README.it.md)

Spiele **Fate/Grand Order VR feat. Mash Kyrielight** mit einem auf AstroQuest/shadPS4 basierenden Kompatibilitäts-Build. Das Projekt unterstützt den japanischen PS4-Titel **CUSA09078**, Spielversionen **01.00 / 01.01**.

- **PCVR:** OpenXR über Virtual Desktop und VDXR.
- **Standalone Quest 3:** ein lokaler ARM64-Kern mit FEX und Turnip; der PC streamt keine Spielbilder.

Dies ist derzeit eine private Vorschau. Repository und Releases bleiben privat bzw. Entwürfe. Das Release-Demovideo ist eine private Vorschau, die nur für autorisierte YouTube-Konten erreichbar ist: [Privates Vorschauvideo ansehen](https://youtu.be/zBSpUSqpUaw). Die Pakete enthalten keine PS4-Spieldaten, PKGs, Firmware, Schlüssel oder Spielstände. Stelle dein eigenes extrahiertes Spiel bereit.

## Downloads

Vorschaupakete sind in den [Entwurfs-Releases](https://github.com/saberwatchmanga/FGO-VR/releases) bereitgestellt:

| Datei | Komponente |
| --- | --- |
| `FGO-VR-0.2.1-PCVR-Windows.zip` | Windows-PCVR-Build und externe Auflösungseinstellungen |
| `FGO-VR-0.2.0-Quest3.apk` | Standalone-Quest-3-Build, in diesem PC-Update unverändert |
| `FGO-VR-0.2.1-Source.zip` | Gepinnte Patches, geänderte Quelltext-Snapshots, Build-Referenzen und Lizenzen |
| `SHA256SUMS` / `artifact-manifest.json` | Dateiüberprüfung und Komponentenversionen |

## Schnellstart für Windows / PCVR

Voraussetzungen: 64-Bit-Windows, eine Vulkan-fähige GPU und ein passender Treiber, Microsoft-Visual-C++-Runtime, Virtual Desktop Streamer auf dem PC und Virtual Desktop auf dem Headset.

1. Entpacke `FGO-VR-0.2.1-PCVR-Windows.zip`.
2. Lege dein extrahiertes Basisspiel einschließlich `eboot.bin` unter `FGO-PC/games/CUSA09078` ab. Lege das optionale Update daneben unter `FGO-PC/games/CUSA09078-UPDATE` ab. Ohne Basisspiel kann das Update nicht ausgeführt werden.
3. Verbinde das Headset über Virtual Desktop und lasse Streamer laufen.
4. Starte **`Launch-PCVR.cmd`** per Doppelklick. Der Starter wählt für diesen Prozess VDXR aus, ohne die systemweite OpenXR-Einstellung zu ändern. Schließe zum Beenden das Spielfenster.
5. Öffne zum Ändern der Auflösung **`Resolution-Settings.cmd`**. Das Programm benötigt Python 3 mit Tk. Speichere die Einstellung und starte das Spiel neu. Ohne Python kannst du `FGO-Resolution/settings.json` bearbeiten oder einen direkten Starter unter `profiles` verwenden.
6. **`Launch-PCVR-Original.cmd`** verwendet immer den Build mit Originalauflösung und denselben Spielständen.

Die ursprünglichen Starter mit chinesischen Dateinamen bleiben ebenfalls erhalten. Optionale Systemschriftarten werden nach den AstroQuest-Anweisungen des Upstream-Projekts eingebunden; Systemdateien der Konsole sind nicht enthalten.

Speicherort: `FGO-PC/runtime-vr/user/home/1000/savedata/CUSA09078`. Schließe das Spiel, bevor du das gesamte Titelverzeichnis sicherst.

## Schnellstart für Standalone Quest 3

Installiere `FGO-VR-0.2.0-Quest3.apk` (Paket `com.fgovr.quest`, Versionscode 2). Ein Update mit derselben Signatur kann App-Daten erhalten. Aktiviere USB-Debugging und kopiere deine extrahierten Spielordner nach:

```text
/data/local/tmp/fgovr/games/CUSA09078
/data/local/tmp/fgovr/games/CUSA09078-UPDATE
```

Die zweite Adresse ist nur für das optionale Update 1.01 bestimmt.

Sorge dafür, dass die Dateien lesbar sind. Befehle und Upgrade-Details findest du unter [Quest-Installation](docs/INSTALL_QUEST.md).

Wenn genau ein Quest per USB verbunden ist, kannst du mit dem Windows-Einstellungsprogramm die Quest-Auflösung übertragen. Schließe danach die App und starte sie erneut. Das Programm sichert die bestehende Konfiguration und ändert ausschließlich `fgo_render_scale`.

Protokolle und Einstellungen befinden sich unter `/sdcard/Android/data/com.fgovr.quest/files/`. In `vrhost.txt` kannst du `fgo_render_scale=100/110/125` eintragen. Nach dem Start läuft das Spiel lokal auf dem Headset.

## Auflösungsprofile

Beide Komponenten starten standardmäßig mit **100 / OFF**: Das entspricht 100% / 1.00x und erhält die Originalauflösung. Höhere Werte erhöhen GPU- und Speicherbedarf. Dies sind interne Renderprofile des Spiels; der von VDXR angezeigte Auflösungsprozentsatz ist ein separater Messwert.

| Profil | PCVR | Quest 3 | Beobachtetes Ergebnis |
| --- | --- | --- | --- |
| 100 | Originalauflösung | Originalauflösung | Quest-Nutzer meldete starkes Aliasing |
| 110 | Verfügbar | Verfügbar | Quest-Nutzer fand es akzeptabel, mit sichtbarem Aliasing |
| 125 | Nur Start geprüft | Verfügbar | Quest-Nutzer meldete merkliches Ruckeln |
| 150 | Verfügbar | Nur PC | PCVR-/VDXR-Nutzer meldete gute Bildqualität und bestätigte einen vollständigen Spieldurchlauf |

**110** ist das empfohlene Startprofil für Quest. Das Quest-Material im Release-Video wurde standalone mit 100 (1.00x) aufgenommen; Aliasing ist dabei stärker sichtbar als auf dem PC. Wenn dir ein Gaming-PC zur Verfügung steht, ist PCVR-Streaming über Virtual Desktop vorzuziehen. Bei schlechter Leistung kannst du auf 100 zurückstellen. Der getestete PC hatte einen i5-13400F / RTX 4070 / 64 GB RAM; es werden weder quantitative FPS-Werte noch eine Leistungsbehauptung für den vollständigen Spielverlauf gemacht.

Die verifizierten Ziele pro Auge sind 1408×1512 bei 100, 1536×1663 bei 110, 1792×1890 bei 125 und 2048×2268 bei PC150. Der Patch ersetzt die verifizierte kanonische Spielanforderung von 1.4f, erhält andere Anforderungen und Allokationsprüfungen und verhindert wiederholte Skalierung.

### Übergangsfehler in PCVR 0.2.1

Bei höherer Auflösung erschöpfte ein Story-Übergang zuvor den festen Grafikspeicherpool des Spiels. Eine fehlerhafte Out-of-Memory-Meldung verursachte anschließend einen zweiten Absturz. PCVR 0.2.1 vergrößert den Grafikspeicherpool zusammen mit dem zugehörigen prozesslokalen Backing-/Direct-Memory-Budget und korrigiert das Meldungsformat. Das zusätzliche Budget wird nicht in den gespeicherten Einstellungen abgelegt.

Am **7. Oktober 2026** bestätigte der Nutzer einen **vollständigen Spieldurchlauf mit PCVR / VDXR bei 1.50x**. Auch der zuvor abstürzende Übergang bestand den erneuten Test; die aufgezeichnete Sitzung wurde regulär beendet. Die Startprüfungen für PC125/150 und die Rückstellung auf 100 bestanden ebenfalls. APK und Quelltext für Quest bleiben auf 0.2.0; dieser PC-Fix wurde nicht auf Quest angewendet.

Der akzeptierte Core-Build hat den SHA-256-Hash `563be6008f73855c3b4425c93bca104692999e97f0fb16cf956c5d3aa40123c1`.

Weitere Angaben stehen in den [Testdetails](TESTING.md) und im [Abnahmeprotokoll des Nutzers](docs/USER_ACCEPTANCE_20261007.md).

- Eine spätere PC150-Sitzung endete während des Unity-Preloads mit einer Zugriffsverletzung. Die Ursache ist ungeklärt; siehe [Testdetails](TESTING.md).

## Steuerung

| Eingabe | Belegung |
| --- | --- |
| Left Touch stick | Menü-Richtungen |
| Left / right grip | L1 / R1 |
| Left / right trigger | L2 / R2 |
| Right A | Cross / bestätigen |
| Beide Stick-Klicks gleichzeitig | Neu zentrieren |
| Keyboard Q / E | Bestätigen |
| Keyboard arrows | Menüauswahl |

Die Zielpose der rechten Hand wird an das normale DualShock-Tracking des Spiels übertragen. Die grundlegende Steuerung funktioniert. Vollständiges Move-Verhalten, präzises Zielen und sämtliche Trainingsinteraktionen wurden nicht validiert.

## Aktuelle Einschränkungen

- Quest125 ruckelt auf dem Headset des Nutzers; Quest110 zeigt weiterhin Aliasing.
- **PCVR / VDXR 1.50x: Der Nutzer hat den vollständigen Spieldurchlauf bestätigt.** PC125 wurde in dieser Reparaturrunde nur beim Start geprüft.
- Stabilität wiederholter Durchläufe, gemessene Headset-FPS und Komfort auf anderer Hardware wurden nicht gesondert bewertet.
- Zusätzliche Reprojection-Layer, vollständige Move-Unterstützung und einige Tracking-Schnittstellen haben noch Lücken.
- Dieser Build ist für FGO VR gedacht. Andere PSVR-Spiele benötigen eigene Kompatibilitätsprüfungen.

## Quellcode, Builds und Credits

Basierend auf [AstroQuest](https://github.com/bigmak94/AstroQuest), festgesetzt auf Commit `9f42c44d4e838e3a0df67913e350c4f098110862`, und [shadPS4](https://github.com/shadps4-emu/shadPS4).

Vollständige Plattform-Patches liegen unter `patches`; geänderte Dateien liegen unter `source_snapshot`. **Wende für die gewählte Plattform genau einen vollständigen Patch an. Staple keine früheren Phasen-Patches darüber.**

`tools/prepare_source.py` lädt den festgelegten Upstream-Quellcode und wendet den gewählten Plattform-Patch an. Die festgelegten Eingaben und Referenzskripte stehen in den [Build-Anweisungen](docs/BUILD.md). Einige Entwicklerpfade müssen angepasst werden; ein Ein-Klick-Build auf einem sauberen System wird nicht zugesichert. Release-Signaturschlüssel sind nicht enthalten.

Quellcode-Hinweise unter GPL-2.0-or-later und die geltenden Drittanbieter-Lizenzen bleiben erhalten. Siehe [LICENSE](LICENSE), [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) und die Hinweise der Upstream-Projekte. Dies ist ein inoffizielles Kompatibilitätsprojekt; das Originalspiel und die Figuren gehören ihren jeweiligen Rechteinhabern.

## Unterstützung

Wenn dir dieses Projekt hilft, kannst du seine weitere Entwicklung auf [Ko-fi / terry2418](https://ko-fi.com/terry2418) unterstützen. Vielen Dank für deine Unterstützung.
