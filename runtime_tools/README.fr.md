# FGO VR — PCVR 0.2.1 / Quest 3 0.2.0

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Português](README.pt.md) | [Italiano](README.it.md)

Jouez à **Fate/Grand Order VR feat. Mash Kyrielight** avec une version de compatibilité basée sur AstroQuest/shadPS4. Le projet cible le jeu PS4 japonais **CUSA09078**, versions **01.00 / 01.01**.

- **PCVR :** OpenXR via Virtual Desktop et VDXR.
- **Quest 3 autonome :** cœur ARM64 local avec FEX et Turnip ; le PC ne diffuse pas les images du jeu.

Ce projet et ses téléchargements sont publics. [Voir la vidéo de démonstration](https://youtu.be/zBSpUSqpUaw). Les paquets ne contiennent aucune donnée de jeu PS4, PKG, firmware, clé ni sauvegarde. Fournissez votre propre jeu extrait.

## Téléchargements

Le dossier Windows portable complet, l’APK Quest et les sources sont disponibles dans la [release v0.2.1](https://github.com/saberwatchmanga/FGO-VR/releases/tag/v0.2.1) :

| Fichier | Composant |
| --- | --- |
| [FGO-VR-0.2.1-PCVR-Windows.zip](https://github.com/saberwatchmanga/FGO-VR/releases/download/v0.2.1/FGO-VR-0.2.1-PCVR-Windows.zip) | Version PCVR pour Windows et réglages de résolution externes |
| [FGO-VR-0.2.0-Quest3.apk](https://github.com/saberwatchmanga/FGO-VR/releases/download/v0.2.1/FGO-VR-0.2.0-Quest3.apk) | Version autonome pour Quest 3, inchangée dans cette mise à jour PC |
| [FGO-VR-0.2.1-Source.zip](https://github.com/saberwatchmanga/FGO-VR/releases/download/v0.2.1/FGO-VR-0.2.1-Source.zip) | Correctifs épinglés, instantanés des sources modifiées, références de compilation et licences |
| `SHA256SUMS` / `artifact-manifest.json` | Vérification des fichiers et versions des composants |

## Démarrage rapide Windows / PCVR

Prérequis : Windows 64 bits, GPU et pilote compatibles Vulkan, runtime Microsoft Visual C++, Virtual Desktop Streamer sur le PC et Virtual Desktop sur le casque.

1. Extrayez `FGO-VR-0.2.1-PCVR-Windows.zip`.
2. Placez votre jeu de base extrait, avec `eboot.bin`, dans `FGO-PC/games/CUSA09078`. Placez la mise à jour facultative à côté, dans `FGO-PC/games/CUSA09078-UPDATE`. La mise à jour ne peut pas fonctionner sans le jeu de base.
3. Connectez le casque avec Virtual Desktop et laissez Streamer en cours d’exécution.
4. Double-cliquez sur **`Launch-PCVR.cmd`**. Le lanceur sélectionne VDXR pour ce processus sans modifier le réglage OpenXR du système. Fermez la fenêtre du jeu pour quitter.
5. Pour modifier la résolution, ouvrez **`Resolution-Settings.cmd`**. Python 3 avec Tk est requis. Enregistrez le réglage puis redémarrez le jeu. Sans Python, modifiez `FGO-Resolution/settings.json` ou utilisez un lanceur direct dans `profiles`.
6. **`Launch-PCVR-Original.cmd`** utilise toujours la version à résolution d’origine avec les mêmes sauvegardes.

Les lanceurs d’origine aux noms chinois sont également conservés. Les polices système facultatives suivent les instructions AstroQuest upstream ; les fichiers système de la console ne sont pas fournis.

Emplacement des sauvegardes : `FGO-PC/runtime-vr/user/home/1000/savedata/CUSA09078`. Fermez le jeu avant de sauvegarder le dossier complet du titre.

## Démarrage rapide Quest 3 autonome

Installez `FGO-VR-0.2.0-Quest3.apk` (paquet `com.fgovr.quest`, code de version 2). Une mise à jour signée avec la même signature peut conserver les données de l’application. Activez le débogage USB et copiez vos dossiers de jeu extraits dans :

```text
/data/local/tmp/fgovr/games/CUSA09078
/data/local/tmp/fgovr/games/CUSA09078-UPDATE
```

Le second chemin concerne uniquement la mise à jour facultative 1.01.

Rendez les fichiers lisibles. Consultez [l’installation Quest](docs/INSTALL_QUEST.md) pour les commandes et les détails de mise à niveau.

Avec un seul Quest connecté en USB, utilisez l’outil de réglages Windows pour envoyer le réglage de résolution au Quest, puis fermez et relancez l’application. L’outil sauvegarde la configuration existante et ne modifie que `fgo_render_scale`.

Les journaux et réglages se trouvent dans `/sdcard/Android/data/com.fgovr.quest/files/`. `vrhost.txt` accepte `fgo_render_scale=100/110/125`. Une fois lancé, le jeu s’exécute localement sur le casque.

## Profils de résolution

Les deux composants démarrent par défaut sur **100 / OFF** : cela correspond à 100% / 1.00x et conserve la résolution d’origine. Les valeurs supérieures augmentent l’utilisation du GPU et de la mémoire. Ce sont des profils de rendu internes au jeu ; le pourcentage de résolution affiché par VDXR est une mesure distincte.

| Profil | PCVR | Quest 3 | Résultat observé |
| --- | --- | --- | --- |
| 100 | Résolution d’origine | Résolution d’origine | Un utilisateur Quest a signalé un fort aliasing |
| 110 | Disponible | Disponible | Un utilisateur Quest l’a jugé acceptable, avec de l’aliasing visible |
| 125 | Démarrage vérifié uniquement | Disponible | Un utilisateur Quest a signalé des saccades notables |
| 150 | Disponible | PC uniquement | Un utilisateur PCVR/VDXR a signalé une bonne qualité d’image et confirmé avoir terminé le jeu |

**110** est le profil de départ recommandé pour Quest. Les images Quest de la vidéo d’aperçu ont été capturées en mode autonome à 100 (1.00x) ; l’aliasing y est plus marqué que sur PC. Si vous disposez d’un PC de jeu, privilégiez le streaming PCVR via Virtual Desktop. Si les performances sont faibles, revenez à 100. Le PC testé était équipé d’un i5-13400F / RTX 4070 / 64 Go de RAM ; aucun FPS quantifié ni résultat de performance sur un jeu complet n’est revendiqué.

Les cibles vérifiées par œil sont de 1408×1512 à 100, 1536×1663 à 110, 1792×1890 à 125 et 2048×2268 à PC150. Le correctif remplace la demande canonique vérifiée du jeu de 1.4f tout en conservant les autres demandes et contrôles d’allocation, et empêche la multiplication répétée de l’échelle.

### Correctif des transitions PCVR 0.2.1

À haute résolution, une transition de l’histoire épuisait auparavant le pool de mémoire graphique fixe du jeu. Un message de mémoire insuffisante mal formé provoquait ensuite un second plantage. PCVR 0.2.1 augmente ensemble le pool graphique et le budget mémoire Backing/Direct correspondant, local au processus, et corrige le format du message. Ce budget supplémentaire n’est pas enregistré dans les paramètres.

Le **7 octobre 2026**, l’utilisateur a confirmé avoir **terminé le jeu dans son intégralité en PCVR / VDXR à 1.50x**. La transition qui plantait auparavant a également réussi lors de son nouveau test, et la session enregistrée s’est terminée normalement. Les vérifications de démarrage PC125/150 et le retour à 100 ont aussi réussi. L’APK et les sources Quest restent en 0.2.0 ; ce correctif PC n’a pas été appliqué à Quest.

Le SHA-256 du cœur accepté est `563be6008f73855c3b4425c93bca104692999e97f0fb16cf956c5d3aa40123c1`.

Consultez les [détails des tests](TESTING.md) et le [compte rendu d’acceptation de l’utilisateur](docs/USER_ACCEPTANCE_20261007.md).

- Une session PC150 ultérieure s’est terminée par une violation d’accès pendant le préchargement Unity. La cause reste indéterminée ; voir les [détails des tests](TESTING.md).

## Commandes

| Entrée | Mappage |
| --- | --- |
| Left Touch stick | Directions du menu |
| Left / right grip | L1 / R1 |
| Left / right trigger | L2 / R2 |
| Right A | Cross / confirmer |
| Clic simultané sur les deux sticks | Recentrer |
| Keyboard Q / E | Confirmer |
| Keyboard arrows | Sélection dans le menu |

La pose de visée de la main droite est reliée au suivi DualShock standard du jeu. Les commandes de base fonctionnent. Le comportement complet de Move, la visée précise et toutes les interactions d’entraînement n’ont pas été validés.

## Limites actuelles

- Quest125 présente des saccades sur le casque de l’utilisateur ; Quest110 conserve de l’aliasing.
- **PCVR / VDXR 1.50x : l’utilisateur a confirmé avoir terminé le jeu.** PC125 n’a fait l’objet que d’une vérification au démarrage lors de cette série de réparations.
- La stabilité après plusieurs exécutions, les FPS mesurés dans le casque et le confort sur d’autres matériels n’ont pas été évalués séparément.
- Il reste des lacunes pour les couches de reprojection supplémentaires, la prise en charge complète de Move et certaines interfaces de suivi.
- Cette version cible FGO VR. Les autres jeux PSVR nécessitent leurs propres vérifications de compatibilité.

## Sources, compilations et crédits

Basé sur [AstroQuest](https://github.com/bigmak94/AstroQuest), épinglé au commit `9f42c44d4e838e3a0df67913e350c4f098110862`, et sur [shadPS4](https://github.com/shadps4-emu/shadPS4).

Les correctifs complets pour chaque plateforme se trouvent dans `patches` ; les fichiers modifiés sont dans `source_snapshot`. **Appliquez un seul correctif complet pour la plateforme choisie. N’empilez pas les correctifs des phases précédentes.**

`tools/prepare_source.py` récupère les sources upstream épinglées et applique le correctif de la plateforme choisie. Les entrées épinglées et scripts de référence figurent dans les [instructions de compilation](docs/BUILD.md). Certains chemins de développeur doivent être ajustés ; une compilation en un clic sur une machine vierge n’est pas garantie. Les clés de signature des releases ne sont pas incluses.

Les avis sur les sources sont conservés sous GPL-2.0-or-later et les licences tierces applicables. Consultez [LICENSE](LICENSE), [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) et les avis upstream. Il s’agit d’un projet de compatibilité non officiel ; le jeu original et ses personnages appartiennent à leurs ayants droit respectifs.

## Soutien

Si ce projet vous est utile, vous pouvez soutenir son développement continu sur [Ko-fi / terry2418](https://ko-fi.com/terry2418). Merci pour votre soutien.
