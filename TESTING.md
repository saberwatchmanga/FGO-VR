# Test Summary

## PCVR 0.2.1 (2026-10-07)

**Full playthrough completed:** the user has confirmed finishing the complete game on the tested PCVR / VDXR 1.50× setup. This is user-reported gameplay acceptance, separate from the short automated startup checks below.

On October 7, the user reran the original crashing story transition at 1.50× in the matching PCVDXR 01.01 setup. The targeted transition passed. The matching session lasted about 12 minutes 24 seconds and exited with code 0. The accepted core SHA-256 is 563be6008f73855c3b4425c93bca104692999e97f0fb16cf956c5d3aa40123c1. The paired memory budget was active, with no DirectMemory allocation failure or unhandled exception.

The game graphics pool did not grow with the higher render scale, so a 36 MiB allocation failed. A malformed original out-of-memory message then caused a second crash. The fix grows the graphics pool and the matching per-process physical Backing/Direct budgets, and corrects the error message. It applies only when the game title, version, and instruction match. At 100%, the setting is off and the original game resolution is preserved.

Standalone desktop startup checks passed for 1.25× and 1.50× (45 seconds each); the 100% fallback ran for 30 seconds. The game LLE heap context showed the expected capacity and a nonzero handle, CPU loading completed, and controlled exits returned code 0. The saved extra_dmem_in_mbytes value remained 0 and the original settings hash did not change. The patch also passed 21 machine-code cases and checks for registers, relocations, alignment, and corrected formatting. The synthetic HLE mspace test covers only that separate HLE implementation; it does not replace validation of the original game LLE heap or headset play.

## Acceptance limits

PCVR / VDXR 1.50× full game completion is confirmed by the user. The 1.25× run passed startup only. This does not add measured frame-rate results, repeated-run stability tests, precise Move-pointing validation, or a full-playthrough result for standalone Quest.

## Existing PC and Quest results

The verified combined stereo render targets at 100%, 110%, 125%, and 150% are 2816×1512, 3072×1663, 3584×1890, and 4096×2268. The patch replaces the verified original request, avoids repeated scaling on readback, preserves unrelated or lower requests, and supports returning to the original resolution.

On October 6, the user reported that PC 150% looked very good. On Quest 3, 100% had severe aliasing, 110% looked acceptable but still showed aliasing, and 125% had noticeable stutter. Quest 0.2.0 is unchanged and was not retested in this update. No measured Quest frame rate, full-story result, or comfort result is claimed. The portable package defaults to 100% on both platforms; 110% is the suggested first Quest setting.

Original device identifiers, private session logs, saves, game files, and desktop screenshots were not uploaded.