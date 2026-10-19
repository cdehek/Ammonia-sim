# Physical iPad owner review

**AWAITING USER DEVICE REVIEW.** Desktop browsers and touch/viewport emulation are not a physical iPad test. No device result is supplied in B11.

Use the extracted `preview/` folder, served from a reachable trusted HTTPS origin, or another independently verified supported origin. Desktop `localhost` points to that desktop; on an iPad it points to the iPad. Ordinary `http://192.168.x.x` cannot be assumed to provide the crypto APIs B10 requires. See SERVER_AND_ORIGIN_COMPATIBILITY.md. Public/remote hosting still requires separate approval.

Record before opening:

| Field | Owner entry |
|---|---|
| Device model | |
| iPadOS version | |
| Browser and version | |
| Preview URL and package identity | |
| Review date / reviewer | |
| Portrait / landscape dimensions | |
| Browser zoom / display scaling | |
| Wi-Fi / other network, signal, client isolation | |
| Navigation/load time and original readiness | |
| Actual panel/module/asset/worker initialization | |

Use Pass / Fail / Not tested for each item; record exact error text and a screenshot where useful.

1. Open the original plant schematic. Inspect compressor and other equipment; operate Initialize auto DX, Start, Pause and +10 s on the **original** simulator. Read compressor/controller displays and trends/history. Change settings and display units.
2. Open the bottom Operator Console. Try collapsed, partial and expanded states; switch tools and return to the schematic. Open Operator Assist. Run one guided training lesson, check grading, retained history and evidence export. Note touch comfort and accidental taps.
3. Open **A2 Evaporator Research**. Initialize cold. Confirm real values for five sections and the independent accepted clock at 0 s. Request exactly **0.0001, 0.0004 and 0.0005 s**, in that order; accepted clocks must be **0.0001, 0.0005, 0.001 s**. No additional advance or continuous operation is authorized.
4. Inspect signed inlet/outlet flows, bulk wet/phase/quality (including “unavailable”), heat exchange, thermal nodes, conservation residuals and diagnostics. Restart warm at 0 s; repeat only the same three supported intervals if needed. Do not interpret terminal bulk wet as compressor safety. A2 is a five-section evaporator, not a complete refrigeration plant.
5. Return to the original plant. Confirm its clock, history and controls remain independent. Stop A2 scheduling; dispose and restart. Observe whether a fresh session clears its old history. Record any lost/unavailable state truthfully; never treat original plant operation as proof that A2 initialized.
6. Inspect gauge readability, wide-table horizontal scrolling and touch control sizing in landscape (including a 1024×768-like layout) and portrait. Check console clipping, onscreen keyboard, safe areas, Safari browser chrome and browser zoom. Note whether controls remain reachable.
7. Rotate during an initialized session. Background and foreground Safari. Record interruptions, stale readings, worker/session state, memory-related reloads and repeatable crashes. A browser reload starts fresh sessions; do not assume recovery of an in-flight solve. Test disposal/restart again if needed.

No sustained real-time performance, multi-second A2 operation, compressor safety or full-plant scientific qualification follows from this review. Do not bypass Safari security or install untrusted certificate exceptions to make it work.

## Returnable observation form

```text
B11 physical review status: TESTED WITH RESULTS / AWAITING USER DEVICE REVIEW
Device / iPadOS / browser/version:
Preview URL / package identity:
Orientation / zoom / network:
Original startup time / original ready:
A2 module + worker + cold/warm initialization outcome:
Item number / Pass-Fail-Not tested:
Expected behavior / actual behavior:
Browser error text:
Steps to reproduce, including session time:
Screenshot filename / orientation:
Touch problems / clipping / keyboard / safe area:
Background, rotation, memory/reload/crash observations:
Repeat count / reproducibility:
Improvement suggestions:
```

Attach owner screenshots/results through the review conversation. Keep this milestone's physical-device status unchanged until genuine device evidence arrives.
